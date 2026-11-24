"""FlowBench repeated burst-load and acknowledgement-loss recovery with durable resume."""
from pathlib import Path
import sys,asyncio,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from depth_support import *
from reliability_lab.config import Config
from reliability_lab.engine import run_experiment
from reliability_lab.store import Store
HERE=Path(__file__).resolve().parent
async def experiment():
    rows=[];runs=[];resumes=[]
    for profile in ['ack_loss','slow','mixed']:
        for concurrency in [1,4,8]:
            for seed in [100001,100002,100003]:
                cfg=Config(count=16,concurrency=concurrency,seed=seed,profile=profile,timeout_ms=35,budget_ms=600,base_ms=3,backoff_ms=2)
                policies=['baseline','retry','resilient'];rotation=seed%3
                for policy in policies[rotation:]+policies[:rotation]:
                    out=await run_experiment(cfg,policy);runs.append(dict(profile=profile,concurrency=concurrency,seed=seed,policy=policy,summary=out['summary']))
                    for r in out['tasks']:rows.append(dict(model=policy,condition=f'{profile}_c{concurrency}',index=f'{seed}:{r["task"]}',correct=r['status']=='succeeded',confidence=0.,loss=0.,status=r['status'],elapsed_ms=r['latency_ms'],attempts=r['attempts'],queue_ms=r['queue_ms']))
    with tempfile.TemporaryDirectory() as t:
        cfg=Config(count=8,profile='ack_loss',base_ms=1);path=Path(t)/'checkpoints.db';store=Store(path);first=await run_experiment(cfg,'resilient',store=store,scope='resume',pause_after='validate');store.close();store=Store(path);second=await run_experiment(cfg,'resilient',store=store,scope='resume');third=await run_experiment(cfg,'resilient',store=store,scope='resume');store.close();resumes=[r['summary'] for r in [first,second,third]];assert resumes[-1]['duplicate_effects']==0 and resumes[-1]['succeeded']==8
    return rows,runs,resumes

def main():
    rows,runs,resumes=asyncio.run(experiment());save(HERE,'FlowBench burst load, duplicate effects & resume','81 actual local async runs:3 fault profiles×3 concurrency levels×3 manifest seeds×3 strategies.16 tasks per run; same fault manifest across policies. SQLite pause/resume/reopen integration separate.',rows,['Retries can duplicate acknowledgement-lost commit effects; resilient ledger bound is local SQLite only.','Queue delay and failed tasks are included; do not report only successful latency.','Seeds are repeated synthetic manifests, not production outage statistics.'],extra=dict(runs=runs,resume=resumes),sources=[HERE/'reliability_lab/engine.py',HERE/'reliability_lab/config.py',HERE/'reliability_lab/store.py'])
if __name__=='__main__':main()
