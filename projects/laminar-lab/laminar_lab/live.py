"""Local real-time asynchronous RL + durable token prefixes + atomic learner.
Independently authored educational coordinator; no CUDA/RDMA/Ray or LLM claims.
All DB mutations occur on one asyncio thread; numerical work can run in a thread.
"""
import asyncio,hashlib,json,os,sqlite3,time
from pathlib import Path
import numpy as np
from .model import pretrain,features,forward,objective_gradient,model_hash,serialize,deserialize,evaluate

SCORER={'name':'symbol-shift','version':1,'rule':'target = (prompt symbol + 1) mod 4; score matching tokens / length'}
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def adam_init(model):return {'step':0,'first':{k:np.zeros_like(v) for k,v in model.items()},'second':{k:np.zeros_like(v) for k,v in model.items()}}
def adam_pack(o):return {'step':o['step'],'first':serialize(o['first']),'second':serialize(o['second'])}
def adam_unpack(o):return {'step':o['step'],'first':deserialize(o['first']),'second':deserialize(o['second'])}
def adam_step(model,grad,state,lr=.02):
 norm=float(np.sqrt(sum(np.square(v).sum() for v in grad.values())));scale=min(1.,5/max(norm,1e-12));t=state['step']+1;m={};v={};new={}
 for k in model:
  g=grad[k]*scale;m[k]=.9*state['first'][k]+.1*g;v[k]=.999*state['second'][k]+.001*g*g
  new[k]=model[k]-lr*(m[k]/(1-.9**t))/(np.sqrt(v[k]/(1-.999**t))+1e-8)
 return new,{'step':t,'first':m,'second':v},norm

def prompt_for(seed,gid):
 rng=np.random.default_rng(seed*10000+gid);n=int(rng.choice([1,2,4,8],p=[.4,.3,.2,.1]));return rng.integers(0,4,n).tolist()
def new_progress(seed,gid):
 return {'sample_index':0,'actions':[],'logps':[],'samples':[],'rng':np.random.default_rng(seed*1000000+gid*10).bit_generator.state,'tokens_written':0}
def hydrate(g):
 out=dict(g);out['samples']=[]
 for s in g['samples']:
  r=dict(s);r['features']=[features(g['prompt'],i,0 if i==0 else s['actions'][i-1]).tolist() for i in range(len(s['actions']))];out['samples'].append(r)
 return out

def optimize(model,opt,reference,groups,steps=4):
 diagnostics=[]
 for _ in range(steps):
  loss,grad,d=objective_gradient(model,reference,[hydrate(g) for g in groups]);model,opt,norm=adam_step(model,grad,opt)
  diagnostics.append({'loss':loss,'gradient_norm':norm,**d})
 return model,opt,diagnostics

class Ledger:
 def __init__(self,path,config):
  self.conn=sqlite3.connect(str(path));self.conn.execute('PRAGMA journal_mode=WAL');self.conn.execute('PRAGMA synchronous=FULL')
  self.conn.executescript('''CREATE TABLE IF NOT EXISTS config(id INTEGER PRIMARY KEY,body TEXT);
 CREATE TABLE IF NOT EXISTS policy(version INTEGER PRIMARY KEY,model TEXT,hash TEXT,optimizer TEXT,update_data TEXT);
 CREATE TABLE IF NOT EXISTS work(gid INTEGER PRIMARY KEY,version INTEGER,prompt TEXT,state TEXT,status TEXT,body TEXT,completed_seq INTEGER);
 CREATE TABLE IF NOT EXISTS pending(id INTEGER PRIMARY KEY,base_version INTEGER,gids TEXT);
 CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,session INTEGER,kind TEXT,body TEXT,prev_hash TEXT,event_hash TEXT);
 CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY AUTOINCREMENT,started REAL,resume_version INTEGER);
 CREATE TABLE IF NOT EXISTS commits(gid INTEGER PRIMARY KEY,update_version INTEGER);
 ''')
  old=self.conn.execute('SELECT body FROM config WHERE id=1').fetchone()
  if old and old[0]!=canonical(config):raise ValueError('Frozen runtime config mismatch')
  if not old:
   m,warm=pretrain(config['seed']);o=adam_init(m)
   with self.conn:self.conn.execute('INSERT INTO config VALUES (1,?)',(canonical(config),));self.conn.execute('INSERT INTO policy VALUES (?,?,?,?,?)',(0,canonical(serialize(m)),model_hash(m),canonical(adam_pack(o)),canonical({'warmstart_loss':warm})))
  self.config=config;self.reference=deserialize(json.loads(self.conn.execute('SELECT model FROM policy WHERE version=0').fetchone()[0]));self.started=time.perf_counter()
  with self.conn:
   v=self.latest()[0];cur=self.conn.execute('INSERT INTO sessions(started,resume_version) VALUES (?,?)',(time.time(),v));self.session=cur.lastrowid
   # Work ownership is process-local. On restart all pending prefixes become available.
   self.conn.execute("UPDATE work SET status='partial' WHERE status='running'");self.event('session_start',{'resume_version':v})
 def event(self,kind,body):
  body={**body,'session_elapsed_s':time.perf_counter()-self.started};row=self.conn.execute('SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1').fetchone();prev=row[0] if row else '0'*64;payload={'session':self.session,'kind':kind,'body':body,'prev_hash':prev};h=digest(payload)
  cur=self.conn.execute('INSERT INTO events(session,kind,body,prev_hash,event_hash) VALUES (?,?,?,?,?)',(self.session,kind,canonical(body),prev,h));return cur.lastrowid
 def latest(self):
  r=self.conn.execute('SELECT version,model,optimizer FROM policy ORDER BY version DESC LIMIT 1').fetchone();return r[0],deserialize(json.loads(r[1])),adam_unpack(json.loads(r[2]))
 def policy(self,version):
  r=self.conn.execute('SELECT model,hash FROM policy WHERE version=?',(version,)).fetchone()
  if not r:raise ValueError('Snapshot unavailable; cannot resume using new weights')
  m=deserialize(json.loads(r[0]));assert model_hash(m)==r[1];return m,r[1]
 def claim(self):
  with self.conn:
   row=self.conn.execute("SELECT gid,version,prompt,state FROM work WHERE status='partial' ORDER BY gid LIMIT 1").fetchone()
   if row:
    gid,version,prompt,state=row;self.conn.execute("UPDATE work SET status='running' WHERE gid=?",(gid,));self.event('resume_prefix',{'gid':gid,'version':version,'saved_tokens':json.loads(state)['tokens_written']});return gid,version,json.loads(prompt),json.loads(state)
   inventory=self.conn.execute("SELECT COUNT(*) FROM work WHERE status IN ('partial','running','ready')").fetchone()[0]
   if inventory>=self.config['capacity']:return None
   gid=self.conn.execute('SELECT COALESCE(MAX(gid),-1)+1 FROM work').fetchone()[0];version=self.latest()[0];prompt=prompt_for(self.config['seed'],gid);state=new_progress(self.config['seed'],gid)
   self.conn.execute('INSERT INTO work VALUES (?,?,?,?,?,?,?)',(gid,version,canonical(prompt),canonical(state),'running',None,None));self.event('reserve',{'gid':gid,'version':version,'inventory_before':inventory});return gid,version,prompt,state
 def save(self,gid,version,prompt,state):
  with self.conn:
   row=self.conn.execute('SELECT version,state FROM work WHERE gid=?',(gid,)).fetchone();assert row[0]==version;old=json.loads(row[1]);assert state['tokens_written']>=old['tokens_written'];self.conn.execute('UPDATE work SET state=? WHERE gid=?',(canonical(state),gid));self.event('token_checkpoint',{'gid':gid,'version':version,'tokens_written':state['tokens_written'],'sample_index':state['sample_index']})
 def complete(self,gid,version,prompt,state):
  m,h=self.policy(version);g={'id':str(self.config['seed'])+':'+str(gid),'gid':gid,'prompt':prompt,'length':len(prompt),'policy_version':version,'behavior_model_sha256':h,'samples':state['samples'],'scorer':SCORER,'scorer_sha256':digest(SCORER),'finish_version':self.latest()[0]}
  with self.conn:
   seq=self.event('ready',{'gid':gid,'version':version,'finish_version':g['finish_version']});self.conn.execute("UPDATE work SET status='ready',body=?,completed_seq=? WHERE gid=?",(canonical(g),seq,gid))
 def batch(self):
  existing=self.conn.execute('SELECT base_version,gids FROM pending WHERE id=1').fetchone()
  if existing:
   base,ids=existing;assert base==self.latest()[0];ids=json.loads(ids);return [json.loads(self.conn.execute('SELECT body FROM work WHERE gid=?',(i,)).fetchone()[0]) for i in ids]
  version=self.latest()[0];bound=self.config.get('staleness_bound');rows=self.conn.execute("SELECT gid,version,body FROM work WHERE status='ready' ORDER BY completed_seq,gid").fetchall()
  with self.conn:
   if bound is not None:
    drop=[i for i,v,b in rows if version-v>bound]
    for i in drop:self.conn.execute("UPDATE work SET status='discarded' WHERE gid=?",(i,));self.event('discard',{'gid':i,'consume_version':version})
    rows=[r for r in rows if r[0] not in drop]
   if len(rows)<self.config['batch_groups']:return None
   rows=rows[:self.config['batch_groups']];ids=[i for i,v,b in rows];self.conn.execute('INSERT INTO pending VALUES (1,?,?)',(version,canonical(ids)));self.event('batch_reserved',{'base_version':version,'gids':ids})
  return [json.loads(b) for i,v,b in rows]
 def commit(self,base,model,opt,groups,steps,crash):
  next_version=base+1;ids=[g['gid'] for g in groups];meta={'gids':ids,'base_version':base,'consume_staleness':[base-g['policy_version'] for g in groups],'steps':steps,'fixed_probe':evaluate(model),'reward':float(np.mean([s['reward'] for g in groups for s in g['samples']]))}
  crash('before_commit',next_version)
  self.conn.execute('BEGIN IMMEDIATE')
  try:
   assert self.latest()[0]==base
   self.conn.execute('INSERT INTO policy VALUES (?,?,?,?,?)',(next_version,canonical(serialize(model)),model_hash(model),canonical(adam_pack(opt)),canonical(meta)))
   for gid in ids:
    assert self.conn.execute('SELECT status FROM work WHERE gid=?',(gid,)).fetchone()[0]=='ready';self.conn.execute('INSERT INTO commits VALUES (?,?)',(gid,next_version));self.conn.execute("UPDATE work SET status='consumed' WHERE gid=?",(gid,))
   self.conn.execute('DELETE FROM pending WHERE id=1');self.event('learner_commit',{'version':next_version,'gids':ids,'model_sha256':model_hash(model),'adam_step':opt['step']});crash('inside_commit',next_version);self.conn.commit()
  except BaseException:self.conn.rollback();raise
  crash('after_commit',next_version)
 def export(self):
  policies=[{'version':v,'model':json.loads(m),'model_sha256':h,'optimizer':json.loads(o),'update':json.loads(u)} for v,m,h,o,u in self.conn.execute('SELECT * FROM policy ORDER BY version')]
  work=[{'gid':gid,'policy_version':v,'prompt':json.loads(p),'state':json.loads(s),'status':st,'group':json.loads(b) if b else None,'completed_seq':seq} for gid,v,p,s,st,b,seq in self.conn.execute('SELECT * FROM work ORDER BY gid')]
  events=[{'seq':seq,'session':session,'kind':kind,'body':json.loads(body),'prev_hash':prev,'event_hash':h} for seq,session,kind,body,prev,h in self.conn.execute('SELECT * FROM events ORDER BY seq')]
  sessions=[{'id':i,'started':t,'resume_version':v} for i,t,v in self.conn.execute('SELECT * FROM sessions')];counts={st:sum(r['status']==st for r in work) for st in ['partial','running','ready','consumed','discarded']}
  return {'protocol':self.config,'policies':policies,'work':work,'events':events,'sessions':sessions,'counts':counts,'commit_ledger':[{'gid':gid,'version':v} for gid,v in self.conn.execute('SELECT * FROM commits ORDER BY update_version,gid')],'summary':{'latest_version':policies[-1]['version'],'model_sha256':policies[-1]['model_sha256'],'adam_step':policies[-1]['optimizer']['step'],'fixed_probe':policies[-1]['update'].get('fixed_probe'), 'session_count':len(sessions),'group_counts':counts,'all_reserved_groups':len(work),'distributed_exactly_once':False,'language_model':False}}

async def run(path,config,fault='none'):
 ledger=Ledger(path,config);stop=asyncio.Event();fault_at=5
 def crash(phase,value):
  if fault==phase and value==fault_at:os._exit({'before_commit':91,'inside_commit':92,'after_commit':93,'token_prefix':94}[phase])
 async def producer(worker):
  while not stop.is_set():
   claimed=ledger.claim()
   if claimed is None:
    await asyncio.sleep(.001);continue
   gid,version,prompt,state=claimed;m,h=ledger.policy(version)
   while state['sample_index']<4:
    j=state['sample_index'];rng=np.random.default_rng();rng.bit_generator.state=state['rng']
    for pos in range(len(state['actions']),len(prompt)):
     previous=state['actions'][-1] if state['actions'] else 0;x=features(prompt,pos,previous);probs,_=await asyncio.to_thread(forward,x[None],m);a=int(rng.choice(4,p=probs[0]));state['actions'].append(a);state['logps'].append(float(np.log(probs[0,a])));state['rng']=rng.bit_generator.state;state['tokens_written']+=1;ledger.save(gid,version,prompt,state)
     if fault=='token_prefix' and gid==2 and state['tokens_written']==1:os._exit(94)
     await asyncio.sleep(config['delay_scale']*(4 if gid%17==0 else 1))
    target=[(int(v)+1)%4 for v in prompt];reward=sum(a==t for a,t in zip(state['actions'],target))/len(prompt)
    state['samples'].append({'actions':state['actions'][:],'behavior_logp':state['logps'][:],'reward':reward,'target':target,'policy_version':version,'length':len(prompt),'behavior_model_sha256':h});state['sample_index']+=1;state['actions']=[];state['logps']=[];state['rng']=np.random.default_rng(config['seed']*1000000+gid*10+state['sample_index']).bit_generator.state;ledger.save(gid,version,prompt,state)
   ledger.complete(gid,version,prompt,state)
 async def learner():
  while ledger.latest()[0]<config['updates']:
   batch=ledger.batch()
   if batch is None:await asyncio.sleep(.001);continue
   base,m,opt=ledger.latest()
   with ledger.conn:ledger.event('train_start',{'version':base,'gids':[g['gid'] for g in batch]})
   m,opt,steps=await asyncio.to_thread(optimize,m,opt,ledger.reference,batch,config['gradient_steps']);await asyncio.sleep(config['learner_delay']);ledger.commit(base,m,opt,batch,steps,crash)
  stop.set()
 tasks=[asyncio.create_task(producer(w)) for w in range(config['workers'])];trainer=asyncio.create_task(learner())
 try:
  # Any producer error ends this run. Do not turn a corrupt worker into endless learner wait.
  done,pending=await asyncio.wait([trainer]+tasks,return_when=asyncio.FIRST_COMPLETED)
  for task in done:
   if task.exception():raise task.exception()
  if not trainer.done():await trainer
 finally:
  stop.set()
  for t in tasks+[trainer]:
   if not t.done():t.cancel()
  await asyncio.gather(*tasks,trainer,return_exceptions=True)
 result=ledger.export();ledger.conn.close();return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--db',required=True);p.add_argument('--config',required=True);p.add_argument('--fault',default='none');a=p.parse_args();r=asyncio.run(run(a.db,json.loads(Path(a.config).read_text()),a.fault));print(canonical(r))
