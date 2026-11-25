"""Actual asyncio producer/learner loops with real autoregressive MLP RL.
Artificial per-token I/O delays explicitly named, never interpreted as GPU speedup.
"""
import asyncio,time,json,platform,sys,hashlib
from pathlib import Path
import numpy as np
from .model import pretrain,group,objective_gradient,apply,evaluate,model_hash,serialize
from .planes import Relay,Pool
MODES=['synchronous','async_ratio','async_no_ratio','async_bound2']

async def run(seed,mode,updates=40,batch_groups=6,workers=4,delay_scale=.0015):
 m,warmup=pretrain(seed);reference={k:v.copy() for k,v in m.items()};relay=Relay(m);pool=Pool();records=[];events=[];metrics=[];discarded=[];version=0;start=time.perf_counter();queue=asyncio.Queue(maxsize=24);stop=asyncio.Event();next_id=0;backpressure=0.;inflight=0;max_depth=0
 initial=evaluate(m);models={0:model_hash(m)}
 def stamp():return time.perf_counter()-start
 def event(kind,**kw):events.append({'time_s':stamp(),'kind':kind,**kw})
 def record(g):
  # Regenerate exact features from prompt and preceding sampled action.
  r={k:v for k,v in g.items() if k!='samples'};r['samples']=[{k:v for k,v in s.items() if k!='features'} for s in g['samples']];records.append(r)
 async def produce(worker):
  nonlocal next_id,backpressure,inflight,max_depth
  while not stop.is_set():
   gid=next_id;next_id+=1;v,snapshot,h=relay.pull();inflight+=1;event('rollout_start',group=gid,worker=worker,version=v,sha256=h)
   g=await asyncio.to_thread(group,seed,gid,snapshot,v)
   # Emulated variable I/O/environment duration, independent of optimizer. Not GPU timing.
   await asyncio.sleep(delay_scale*g['length']*(4 if gid%17==0 else 1));inflight-=1
   g['finish_version']=relay.latest;g['inherent_staleness']=relay.latest-v;g['finish_time_s']=stamp();pool.complete(g);record(g);event('rollout_finish',group=gid,worker=worker,version=v,staleness=g['inherent_staleness'])
   t=time.perf_counter();await queue.put(g);backpressure+=time.perf_counter()-t;max_depth=max(max_depth,queue.qsize())
 async def optimize(batch):
  nonlocal m,version
  event('train_start',version=version,groups=[g['gid'] for g in batch]);stale=[version-g['policy_version'] for g in batch];steps=[]
  for _ in range(4):
   loss,grad,diagnostics=await asyncio.to_thread(objective_gradient,m,reference,batch,mode!='async_no_ratio');m,norm=apply(m,grad,.8);steps.append({'loss':loss,'gradient_norm':norm,**diagnostics})
  # Common illustrative optimizer/control-plane overhead; recorded separately from compute.
  await asyncio.sleep(.002)
  version+=1;relay.publish(version,m);models[version]=model_hash(m);ev=evaluate(m);metrics.append({'update':version,'time_s':stamp(),'groups':[g['gid'] for g in batch],'sample_staleness':stale,'reward':float(np.mean([s['reward'] for g in batch for s in g['samples']])),'steps':steps,**ev});event('publish',version=version,sha256=models[version])
 if mode=='synchronous':
  for step in range(updates):
   v,snapshot,h=relay.pull();batch=[]
   async def sync_one(gid):
    event('rollout_start',group=gid,version=v);g=await asyncio.to_thread(group,seed,gid,snapshot,v);await asyncio.sleep(delay_scale*g['length']*(4 if gid%17==0 else 1));g['finish_version']=version;g['inherent_staleness']=0;g['finish_time_s']=stamp();pool.complete(g);record(g);event('rollout_finish',group=gid,version=v,staleness=0);return g
   # Same four worker slots; barrier after common batch, NOT a hardware colocated baseline.
   sem=asyncio.Semaphore(workers)
   async def limited(gid):
    async with sem:return await sync_one(gid)
   batch=await asyncio.gather(*(limited(step*batch_groups+j) for j in range(batch_groups)));await optimize(batch)
 else:
  tasks=[asyncio.create_task(produce(i)) for i in range(workers)]
  try:
   for step in range(updates):
    batch=[]
    while len(batch)<batch_groups:
     g=await queue.get();queue.task_done();stale=version-g['policy_version']
     if mode=='async_bound2' and stale>2:discarded.append({'group':g['gid'],'staleness':stale});event('discard',group=g['gid'],staleness=stale);continue
     batch.append(g)
    await optimize(batch)
  finally:
   stop.set()
   for t in tasks:t.cancel()
   await asyncio.gather(*tasks,return_exceptions=True)
 elapsed=stamp();pool.close();consumed=[i for row in metrics for i in row['groups']];used={g['gid']:g for g in records if g['gid'] in consumed};all_stale=[s for row in metrics for s in row['sample_staleness']];tok=sum(sum(s['length'] for s in g['samples']) for g in used.values())
 summary={'seed':seed,'mode':mode,'updates':updates,'groups_per_update':batch_groups,'consumed_groups':len(consumed),'generated_groups':len(records),'discarded_groups':len(discarded),'unused_generated_groups':len(records)-len(used)-len(discarded),'actual_sampled_tokens_consumed':tok,'elapsed_s':elapsed,'illustrative_tokens_per_s':tok/elapsed,'staleness_mean':float(np.mean(all_stale)),'staleness_p95':float(np.quantile(all_stale,.95)),'staleness_max':max(all_stale),'backpressure_wait_s':backpressure,'queue_capacity':24,'max_queue_depth':max_depth,'initial':initial,'final':evaluate(m),'initial_model_sha256':models[0],'final_model_sha256':model_hash(m)}
 return {'summary':summary,'source_hashes':{name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest() for name in ['model.py','planes.py','experiment.py']},'warmstart_loss':warmup,'updates':metrics,'groups':records,'discarded':discarded,'events':events,'model_hashes':models,'final_model':serialize(m),'protocol':{'workers':workers,'delay_scale_s_per_token':delay_scale,'artificial_overhead_s_per_update':.002,'rl_lr':.8,'optimizer_steps_per_batch':4,'clip_low':.2,'clip_high':.2,'reference_kl':.02,'task':'synthetic copy warm-start then symbol shift +1 modulo4; no human feedback','loss':'token-ratio clipped GRPO-like; no full-sequence IS claim','real_language_model':False}}

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/runs');p.add_argument('--updates',type=int,default=40);args=p.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True);summaries=[]
 for seed in [7,19,41]:
  for mode in MODES:
   path=out/f'{seed}-{mode}.json'
   if path.exists():raise FileExistsError(f'immutable results already exist: {path}')
   r=asyncio.run(run(seed,mode,args.updates));path.write_text(json.dumps(r,ensure_ascii=False,allow_nan=False));summaries.append(r['summary']);print(json.dumps(r['summary']),flush=True)
 (out/'summary.json').write_text(json.dumps({'runs':summaries,'environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__},'note':'Wall-clock includes explicitly injected I/O delays; illustrative controlled scheduling, not GPU benchmark.'},indent=2))
if __name__=='__main__':main()
