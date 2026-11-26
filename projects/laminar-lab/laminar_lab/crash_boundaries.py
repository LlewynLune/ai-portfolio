"""Focused crash-point evidence captured from SQLite before restarting live RL.
Additional exploratory recovery regression; preserves first run matrix unchanged.
"""
import json,sqlite3,tempfile,subprocess,sys,time,hashlib
from pathlib import Path
from .live import canonical
from .live_audit import audit,tamper_checks

def inspect(path):
 db=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True)
 latest=db.execute('SELECT version,hash,optimizer FROM policy ORDER BY version DESC LIMIT 1').fetchone();pending=db.execute('SELECT base_version,gids FROM pending').fetchall();commits=db.execute('SELECT COUNT(*) FROM commits').fetchone()[0];counts=dict(db.execute('SELECT status,COUNT(*) FROM work GROUP BY status').fetchall());prefixes=[{'gid':gid,'version':v,'sample_index':json.loads(s)['sample_index'],'saved_tokens':json.loads(s)['tokens_written'],'rng_sha256':hashlib.sha256(canonical(json.loads(s)['rng']).encode()).hexdigest()} for gid,v,s in db.execute("SELECT gid,version,state FROM work WHERE status IN ('partial','running')")];db.close()
 return {'latest_committed_version':latest[0],'model_sha256':latest[1],'committed_adam_step':json.loads(latest[2])['step'],'consumption_rows':commits,'pending_batches':[{'base_version':v,'gids':json.loads(ids)} for v,ids in pending],'status_counts':counts,'partial_prefixes':prefixes,'after_os_exit_before_restart':True}

def main():
 out=Path('artifacts/live-crash-boundaries')
 if out.exists():raise FileExistsError('immutable output exists')
 out.mkdir();protocol={'seed':19,'faults':['token_prefix','before_commit','inside_commit','after_commit'],'updates':20,'crash_version':5,'note':'Focused additional regression after first live matrix; snapshot actual DB immediately after process termination, before any recovery. Deterministic counters, not deterministic async completion order.'};(out/'protocol.json').write_text(json.dumps(protocol,indent=2));rows=[]
 for fault in protocol['faults']:
  cfg={'seed':19,'updates':20,'batch_groups':6,'workers':4,'capacity':12,'staleness_bound':None,'delay_scale':.001,'learner_delay':.002,'gradient_steps':4,'scorer_version':1,'coordinator_version':1};config=out/(fault+'-config.json');config.write_text(canonical(cfg));start=time.perf_counter()
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'runtime.sqlite';cmd=[sys.executable,'-m','laminar_lab.live','--db',str(db),'--config',str(config.resolve())];killed=subprocess.run(cmd+['--fault',fault],capture_output=True,text=True,timeout=90);before=inspect(db)
   assert killed.returncode=={'token_prefix':94,'before_commit':91,'inside_commit':92,'after_commit':93}[fault]
   if fault in ['before_commit','inside_commit']:assert before['latest_committed_version']==4 and before['consumption_rows']==24 and before['pending_batches'][0]['base_version']==4
   if fault=='after_commit':assert before['latest_committed_version']==5 and before['consumption_rows']==30 and not before['pending_batches']
   if fault=='token_prefix':assert any(p['saved_tokens']>0 for p in before['partial_prefixes'])
   resumed=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
   if resumed.returncode:raise RuntimeError(resumed.stderr)
   data=json.loads(resumed.stdout);data['before_restart']=before;data['audit']=audit(data);data['tamper_checks']=tamper_checks(data);data['run']={'name':'boundary-'+fault,'fault':fault,'first_exit':killed.returncode,'final_exit':resumed.returncode,'elapsed_with_restart_s':time.perf_counter()-start};data['source_hashes']={n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest() for n in ['live.py','live_audit.py','crash_boundaries.py','model.py']};(out/(fault+'.json')).write_text(canonical(data));rows.append({'fault':fault,'before_restart':before,'audit':data['audit'],'summary':data['summary']})
 (out/'summary.json').write_text(json.dumps({'runs':rows,'actual_forced_exits':4,'note':'Not a new independent task; boundary-focused regression in same synthetic setting.'},indent=2));print('4 crash-boundary snapshots verified')
if __name__=='__main__':main()
