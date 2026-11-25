"""Atomic toy-learner checkpoint + consumption ledger under real process failures.
Deterministic ordered batches isolate crash semantics from asynchronous completion order.
This is not the live asyncio worker pool, distributed training, or optimizer-state recovery.
"""
import sqlite3,json,os,sys,tempfile,subprocess,hashlib,time
from pathlib import Path
from .model import pretrain,group,objective_gradient,apply,model_hash,serialize,deserialize,evaluate

def connect(path):
 db=sqlite3.connect(str(path));db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL');db.executescript('CREATE TABLE IF NOT EXISTS learner(version INTEGER PRIMARY KEY,model TEXT,sha TEXT); CREATE TABLE IF NOT EXISTS consumption(gid TEXT PRIMARY KEY,version INTEGER,body TEXT);');return db

def train(path,seed,updates=12,phase='none',crash_at=5):
 db=connect(path);initial,_=pretrain(seed);reference=initial;row=db.execute('SELECT version,model FROM learner ORDER BY version DESC LIMIT 1').fetchone()
 if not row:
  with db:db.execute('INSERT INTO learner VALUES (?,?,?)',(0,json.dumps(serialize(initial)),model_hash(initial)))
  row=(0,json.dumps(serialize(initial)))
 version=int(row[0]);m=deserialize(json.loads(row[1]));resume_from=version
 while version<updates:
  batch=[group(seed,version*6+j,m,version) for j in range(6)]
  for _ in range(4):_,g,_=objective_gradient(m,reference,batch);m,_=apply(m,g,.8)
  target_version=version+1
  if target_version==crash_at and phase=='before_transaction':os._exit(81)
  db.execute('BEGIN IMMEDIATE')
  try:
   db.execute('INSERT INTO learner VALUES (?,?,?)',(target_version,json.dumps(serialize(m)),model_hash(m)))
   for sample in batch:db.execute('INSERT INTO consumption VALUES (?,?,?)',(sample['id'],target_version,json.dumps(sample,sort_keys=True)))
   if target_version==crash_at and phase=='inside_transaction':os._exit(82)
   db.commit()
  except BaseException:db.rollback();raise
  if target_version==crash_at and phase=='after_commit':os._exit(83)
  version=target_version
 count=db.execute('SELECT COUNT(*) FROM consumption').fetchone()[0];ids=[r[0] for r in db.execute('SELECT gid FROM consumption ORDER BY gid')];versions=[r[0] for r in db.execute('SELECT version FROM learner ORDER BY version')];db.close()
 return {'seed':seed,'resume_from':resume_from,'final_version':version,'final_sha256':model_hash(m),'consumption_count':count,'consumed_ids':ids,'checkpoint_versions':versions,'final_probe':evaluate(m),'optimizer':'plain SGD; no momentum state','atomic_scope':'single SQLite transaction, learner snapshot and ledger','async_fault_recovery':False}

def run(output):
 out=Path(output);out.mkdir(parents=True,exist_ok=True);results=[]
 for seed in [7,19,41]:
  with tempfile.TemporaryDirectory() as d:
   baseline=train(Path(d)/'baseline.sqlite',seed)
   for phase in ['before_transaction','inside_transaction','after_commit']:
    path=Path(d)/(phase+'.sqlite');cmd=[sys.executable,'-m','laminar_lab.durable','--child',str(path),'--seed',str(seed),'--phase',phase];killed=subprocess.run(cmd,capture_output=True,text=True)
    resumed=subprocess.run([sys.executable,'-m','laminar_lab.durable','--child',str(path),'--seed',str(seed),'--phase','none'],capture_output=True,text=True)
    if resumed.returncode:raise RuntimeError(resumed.stderr)
    recovered=json.loads(resumed.stdout);exact=recovered['final_sha256']==baseline['final_sha256'] and recovered['consumed_ids']==baseline['consumed_ids'];db=connect(path);v=db.execute('SELECT version,sha FROM learner ORDER BY version').fetchall();db.close()
    r={'seed':seed,'phase':phase,'killed_returncode':killed.returncode,'resumed_returncode':resumed.returncode,'exact_model_and_consumption_match':exact,'baseline':baseline,'recovered':recovered,'checkpoint_chain':v,'distributed_exactly_once':False};results.append(r)
    assert killed.returncode=={'before_transaction':81,'inside_transaction':82,'after_commit':83}[phase] and exact
    assert recovered['consumption_count']==72 and recovered['checkpoint_versions']==list(range(13))
 out_file=out/'durable-learner.json'
 if out_file.exists():raise FileExistsError(out_file)
 out_file.write_text(json.dumps({'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'protocol':{'actual_process_kills':9,'seeds':[7,19,41],'updates_per_chain':12,'groups_per_update':6,'gradient_steps_per_update':4,'crash_version':5,'deterministic_ordered_batches':True,'not_live_async_resume':True},'results':results},indent=2));print('9 actual learner process failures, atomic exact-recovery verified')
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/system');p.add_argument('--child');p.add_argument('--seed',type=int,default=7);p.add_argument('--phase',default='none');a=p.parse_args()
 if a.child:print(json.dumps(train(a.child,a.seed,phase=a.phase)))
 else:run(a.output)
