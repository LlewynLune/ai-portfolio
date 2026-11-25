"""Real child-process termination and same-version prefix recovery, separate from RL bench.
The tiny model is frozen in SQLite; recovery replays saved RNG draws to prefix, checks
exact equality, then generates only unsaved suffix. This recomputes prefix, not KV restore.
"""
import sys,os,json,tempfile,subprocess,sqlite3
from pathlib import Path
from .model import init,group,model_hash,serialize,deserialize,rollout
from .planes import Pool

def child(path,cut,phase):
 db=Pool(path);version,m=db.latest_checkpoint();g=group(13,5,m,version);tokens=g['samples'][0]['actions'];current=db.db.execute('SELECT version,body FROM partial WHERE id=?',('trajectory',)).fetchone()
 saved=json.loads(current[1]) if current else []
 if current and current[0]!=version:raise ValueError('resume policy version changed')
 if saved!=tokens[:len(saved)]:raise ValueError('deterministic prefix mismatch')
 # Each persisted prefix is a committed generating boundary; forced process exit follows it.
 for i in range(len(saved)+1,len(tokens)+1):
  db.save_partial('trajectory',version,tokens[:i])
  if phase=='prefix' and i==cut:os._exit(73)
 db.complete(g)
 if phase=='after_commit':os._exit(74)
 db.close()

def run(output):
 out=Path(output);out.mkdir(parents=True,exist_ok=True);results=[]
 for phase in ['prefix','after_commit']:
  for cut in [1,2,3]:
   with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'recovery.sqlite';p=Pool(path);m=init(11);p.checkpoint(4,m);p.close()
    cmd=[sys.executable,'-m','laminar_lab.recovery','--child',str(path),'--cut',str(cut),'--phase',phase];killed=subprocess.run(cmd,capture_output=True)
    resumed=subprocess.run([sys.executable,'-m','laminar_lab.recovery','--child',str(path),'--cut','0','--phase','resume'],capture_output=True)
    p=Pool(path);rows=p.db.execute('SELECT body FROM experience').fetchall();expected=group(13,5,m,4);actual=json.loads(rows[0][0]) if rows else None;cp=p.latest_checkpoint();p.close()
    row={'phase':phase,'cut':cut,'killed_exit_code':killed.returncode,'resume_exit_code':resumed.returncode,'exact_trajectory_matches':actual==expected,'experience_rows':len(rows),'same_version':cp[0]==4,'same_weight_hash':model_hash(cp[1])==model_hash(m),'prefix_recomputed':True,'distributed_exactly_once':False};results.append(row)
    if killed.returncode not in [73,74] or resumed.returncode!=0 or actual!=expected or len(rows)!=1:raise AssertionError(row)
 (out/'recovery.json').write_text(json.dumps(results,indent=2));print('Actual killed/restarted child processes:',len(results))
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/system');p.add_argument('--child');p.add_argument('--phase',default='prefix');p.add_argument('--cut',type=int,default=1);a=p.parse_args()
 if a.child:child(a.child,a.cut,a.phase)
 else:run(a.output)
