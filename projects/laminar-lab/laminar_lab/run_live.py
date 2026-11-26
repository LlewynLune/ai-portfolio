"""Run real subprocess crashes and restart the LIVE asynchronous coordinator.
Do not compare final model to a non-crash run: completion order is nondeterministic.
Instead every committed update is independently replayed against persisted inputs.
"""
import json,subprocess,sys,tempfile,hashlib,time,platform
from pathlib import Path
from .live_audit import audit,tamper_checks
from .live import canonical

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/live-system');p.add_argument('--smoke',action='store_true');a=p.parse_args();out=Path(a.output)
 if out.exists():raise FileExistsError('immutable output already exists')
 out.mkdir(parents=True);configs=[]
 for seed in ([7] if a.smoke else [7,19,41]):
  for fault in (['token_prefix'] if a.smoke else ['none','token_prefix','before_commit','inside_commit','after_commit']):configs.append((f'{seed}-{fault}',seed,fault,12,None,.001))
 if not a.smoke:
  for cap in [6,12,32]:
   for bound in [None,2]:
    if cap==12 and bound is None:continue
    configs.append((f'capacity{cap}-bound{bound}',7,'none',cap,bound,.001))
 summaries=[];protocol={'frozen_before_run':True,'matrix':configs,'model':'NumPy autoregressive MLP, not a language model','scope':'single machine real-time asyncio and whole-process forced exit; no multi-node/RDMA/CUDA','checks':'independent reward, behavior-logprob version replay, exact committed Adam replay, inventory conservation, duplicate consumption, offline tamper detection','note':'Fixed toy probes overlap previous grammar; fault chains not equal-sample quality benchmarks. Full wall time includes startup, warm-start, sleeps, restart and verification.'};(out/'protocol.json').write_text(json.dumps(protocol,indent=2))
 for name,seed,fault,cap,bound,delay in configs:
  cfg={'seed':seed,'updates':20,'batch_groups':6,'workers':4,'capacity':cap,'staleness_bound':bound,'delay_scale':delay,'learner_delay':.002,'gradient_steps':4,'scorer_version':1,'coordinator_version':1};configfile=out/(name+'-config.json');configfile.write_text(canonical(cfg));start=time.perf_counter()
  with tempfile.TemporaryDirectory() as temp:
   cmd=[sys.executable,'-m','laminar_lab.live','--db',str(Path(temp)/'live.sqlite'),'--config',str(configfile.resolve())];first=subprocess.run(cmd+['--fault',fault],capture_output=True,text=True,timeout=90)
   expected={'none':0,'before_commit':91,'inside_commit':92,'after_commit':93,'token_prefix':94}[fault]
   if first.returncode!=expected:raise RuntimeError(f'{name}: unexpected return {first.returncode}\n{first.stderr}')
   if fault!='none':
    final=subprocess.run(cmd+['--fault','none'],capture_output=True,text=True,timeout=90)
    if final.returncode:raise RuntimeError(final.stderr)
   else:final=first
   data=json.loads(final.stdout)
  elapsed=time.perf_counter()-start;report=audit(data);attacks=tamper_checks(data);data['audit']=report;data['tamper_checks']=attacks;data['run']={'name':name,'fault':fault,'first_exit':first.returncode,'final_exit':final.returncode,'elapsed_with_restart_s':elapsed};data['source_hashes']={n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest() for n in ['live.py','live_audit.py','run_live.py','model.py']}
  (out/(name+'.json')).write_text(canonical(data));stale=[s for p in data['policies'][1:] for s in p['update']['consume_staleness']];row={'name':name,'seed':seed,'fault':fault,'capacity':cap,'bound':bound,'mean_consume_staleness':sum(stale)/len(stale),'max_consume_staleness':max(stale),'counts':data['counts'],'fixed_probe':data['summary']['fixed_probe'],'audit':report,'elapsed_with_restart_s':elapsed,'generated_groups':len(data['work'])};summaries.append(row);print(canonical(row),flush=True)
 (out/'summary.json').write_text(json.dumps({'runs':summaries,'total_real_process_crashes':sum(r['fault']!='none' for r in summaries),'environment':{'python':sys.version,'numpy':__import__('numpy').__version__,'platform':platform.platform()},'note':'Not independent tasks, not comparable final datasets after nondeterministic scheduler restart. Live optimizer states and accepted samples persist; all committed model updates exactly replayed.'},indent=2))
if __name__=='__main__':main()
