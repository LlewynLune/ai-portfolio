"""Immutable weight plane, deduplicated experience/partial pools, same-version packing."""
import sqlite3,json,hashlib
import numpy as np
from .model import model_hash,serialize,deserialize

class Relay:
 def __init__(self,model):self.versions={};self.latest=-1;self.publish(0,model)
 def publish(self,version,model):
  if version<=self.latest:raise ValueError('strictly monotonic publication required')
  snapshot={k:np.array(v,copy=True) for k,v in model.items()}
  for v in snapshot.values():v.setflags(write=False)
  self.versions[version]=(snapshot,model_hash(snapshot));self.latest=version
 def pull(self,version=None):
  version=self.latest if version is None else version
  if version not in self.versions:raise ValueError('unknown version')
  m,h=self.versions[version];return version,{k:v.copy() for k,v in m.items()},h

class Pool:
 def __init__(self,path=':memory:'):
  self.db=sqlite3.connect(str(path));self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
  self.db.executescript('CREATE TABLE IF NOT EXISTS experience(id TEXT PRIMARY KEY,body TEXT NOT NULL);CREATE TABLE IF NOT EXISTS partial(id TEXT PRIMARY KEY,version INTEGER,body TEXT NOT NULL);CREATE TABLE IF NOT EXISTS checkpoints(version INTEGER PRIMARY KEY,body TEXT NOT NULL);')
 def complete(self,g):
  body=json.dumps(g,sort_keys=True);old=self.db.execute('SELECT body FROM experience WHERE id=?',(g['id'],)).fetchone()
  if old:
   if old[0]!=body:raise ValueError('immutable experience conflict')
   return False
  with self.db:self.db.execute('INSERT INTO experience VALUES (?,?)',(g['id'],body));self.db.execute('DELETE FROM partial WHERE id=?',(g['id'],))
  return True
 def save_partial(self,id,version,tokens):
  previous=self.db.execute('SELECT version,body FROM partial WHERE id=?',(id,)).fetchone()
  if previous and (version!=previous[0] or tokens[:len(json.loads(previous[1]))]!=json.loads(previous[1])):raise ValueError('version or prefix mismatch')
  with self.db:self.db.execute('INSERT OR REPLACE INTO partial VALUES (?,?,?)',(id,version,json.dumps(tokens)))
 def checkpoint(self,version,model):
  with self.db:self.db.execute('INSERT INTO checkpoints VALUES (?,?)',(version,json.dumps(serialize(model))))
 def latest_checkpoint(self):
  r=self.db.execute('SELECT version,body FROM checkpoints ORDER BY version DESC LIMIT 1').fetchone();return (r[0],deserialize(json.loads(r[1]))) if r else None
 def close(self):self.db.close()

def best_fit(replicas,cache_cap,batch_cap):
 """Paper-inspired packing PLAN only. No GPU/KV migration or timing claims.
 Replica versions must match. Whole source load merges into feasible destination.
 """
 state={r['id']:dict(r) for r in replicas};plan=[];empty=set()
 candidates=sorted([r for r in replicas if r.get('ramp_down',False) and r['cache']<cache_cap and r['requests']<batch_cap],key=lambda r:(r['cache'],r['id']))
 for src in candidates:
  sid=src['id']
  if sid in empty:continue
  s=state[sid];valid=[state[d['id']] for d in candidates if d['id']!=sid and d['id'] not in empty and state[d['id']]['version']==s['version'] and state[d['id']]['cache']+s['cache']<=cache_cap and state[d['id']]['requests']+s['requests']<=batch_cap]
  if not valid:continue
  dest=max(valid,key=lambda d:(d['cache'],d['id']));dest['cache']+=s['cache'];dest['requests']+=s['requests'];empty.add(sid);plan.append({'source':sid,'destination':dest['id'],'version':s['version'],'cache':s['cache'],'requests':s['requests']})
 return plan,{k:v for k,v in state.items() if k not in empty}
