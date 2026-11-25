"""Streaming prefix invariance and actual subprocess crash/recovery."""
import asyncio,subprocess,tempfile
from .common import *

def video():
 folder='video-guard';p=PROJECTS/folder;protocol={'kind':'prefix_causality_and_observation_dropout','groups':['step','multiple','quiet_gap','stable'],'clips_per_group':30,'methods':['raw','onset','mlp'],'drop_every':[0,3,5],'event_delay_frames':20,'tolerance_frames':16,'original_configs_frozen':True,'kind_of_evidence':'historical trajectories, no new media'};freeze(folder,protocol)
 sys.path.insert(0,str(p));from videoguard.drift import detect
 matcher=module(folder).latency_match;config=load(p/'artifacts/drift-localization/results.json')['configs'];rows=[];metrics=[];prefix_errors=[]
 for group in protocol['groups']:
  records=load(p/f'artifacts/drift-localization/{group}-records.json')[:30]
  for method in protocol['methods']:
   for every in protocol['drop_every']:
    counts=[]
    for r in records:
     traj=[v for j,v in enumerate(r['trajectory']) if every==0 or (j+1)%every!=0];alarms=detect(traj,method,**config[method]);stats=matcher(r['changes'],alarms,16,20)
     # Full run's already-emitted alarms must exactly match every truncated prefix's emissions.
     for end in range(1,len(traj)+1):
      partial=detect(traj[:end],method,**config[method]);expected=[a for a in alarms if a['alarm_frame']<=traj[end-1]['end']];prefix_errors.append(partial!=expected)
     counts.append(stats);rows.append(dict(condition=group,method=method,drop_every=every,seed=r['seed'],retained_windows=len(traj),alarms=alarms,**stats))
    tp=sum(s['tp'] for s in counts);fp=sum(s['fp'] for s in counts);fn=sum(s['fn'] for s in counts);metrics.append(dict(condition=group,method=method,drop_every=every,n=len(records),tp=tp,fp=fp,fn=fn,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0))
 assert not any(prefix_errors)
 return save(folder,'VideoGuard · 流式因果验证与观测丢失','未来窗口是否改变已经发出的报警？少量观测窗口丢失会损害及时检测吗？',rows,metrics,['逐前缀重新检测与完整运行已发报警精确一致，测试的是无未来信息正确性。','观测丢失固定跳过窗口，时间戳不重写；报警错过时限不补信用。','历史媒体轨迹再分析，不是新增真实视频；不重选阈值。'],protocol,details={'prefix_comparisons':len(prefix_errors),'prefix_mismatch':sum(prefix_errors)},files=[Path(__file__),p/'videoguard/drift.py',p/'depth.py'])

CRASH_CODE='''import os,sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from reliability_lab.store import Store
path,mode,point=sys.argv[2:5]
s=Store(path);s.bind("crash", "frozen-workload-v1")
output={"task":0,"stage":"commit","valid":True,"content":"constant"}
if point=="before_effect":os._exit(73)
s.commit("crash",0,output,mode=="resilient")
if point=="after_effect_before_checkpoint":os._exit(73)
s.save("crash",0,"commit",output)
if point=="after_checkpoint":os._exit(73)
s.close()
'''
async def load_budget():
 p=PROJECTS/'reliability-lab';sys.path.insert(0,str(p));from reliability_lab.config import Config;from reliability_lab.engine import run_experiment
 records=[];metrics=[]
 for budget in [30,80,200]:
  for concurrency in [1,4]:
   for seed in [198001,198002,198003]:
    for policy in ['retry','resilient']:
     cfg=Config(count=12,concurrency=concurrency,seed=seed,profile='mixed',timeout_ms=20,budget_ms=budget,base_ms=3,backoff_ms=2);r=await run_experiment(cfg,policy);records.append({'budget_ms':budget,'concurrency':concurrency,'seed':seed,'policy':policy,'tasks':r['tasks'],'summary':r['summary'],'manifest_hash':r['manifest_hash']});metrics.append({'kind':'deadline_load','policy':policy,'budget_ms':budget,'concurrency':concurrency,'seed':seed,**{k:r['summary'][k] for k in ['succeeded','count','p95_ms','retries','duplicate_effects']}})
 return records,metrics

def reliability():
 folder='reliability-lab';p=PROJECTS/folder;protocol={'kind':'real_process_abrupt_exit_and_queue_deadline','crash_points':['before_effect','after_effect_before_checkpoint','after_checkpoint'],'strategies':['retry','resilient'],'repeats':3,'subprocess_exit':73,'effects':'local SQLite only','deadline_budget_ms':[30,80,200],'concurrency':[1,4]};freeze(folder,protocol)
 sys.path.insert(0,str(p));from reliability_lab.store import Store
 rows,metrics=asyncio.run(load_budget())
 with tempfile.TemporaryDirectory() as tmp:
  for strategy in protocol['strategies']:
   for point in protocol['crash_points']:
    for repeat in range(3):
     path=Path(tmp)/f'{strategy}-{point}-{repeat}.db';r=subprocess.run([sys.executable,'-c',CRASH_CODE,str(p),str(path),strategy,point],capture_output=True,text=True);assert r.returncode==73,(r.returncode,r.stderr)
     s=Store(path);s.bind('crash','frozen-workload-v1');out={'task':0,'stage':'commit','valid':True,'content':'constant'};cached=s.get('crash',0,'commit')
     if strategy!='resilient' or cached is None:s.commit('crash',0,out,strategy=='resilient');s.save('crash',0,'commit',out)
     stats=s.stats('crash');s.close();rows.append({'kind':'abrupt_exit','strategy':strategy,'point':point,'repeat':repeat,'exit_code':r.returncode,'checkpoint_present':cached is not None,**stats});metrics.append({'kind':'abrupt_exit','policy':strategy,'budget_ms':None,'concurrency':None,'seed':repeat,'succeeded':1,'count':1,'p95_ms':None,'retries':None,'duplicate_effects':stats['duplicate_effects'],'crash_point':point})
 return save(folder,'FlowBench · 崩溃窗口与端到端期限','真正进程退出发生在提交与检查点之间时，重启会重复副作用吗？',rows,metrics,['子进程真实os._exit，在SQLite commit与checkpoint边界注入退出，恢复重新打开数据库。','幂等仅此单数据库范围，不代表分布式exactly-once或外部API保护。','排队期限含等待/重试/失败，短期限结果不只统计成功延迟；异步IO负载非模型推断。'],protocol,files=[Path(__file__),p/'reliability_lab/engine.py',p/'reliability_lab/store.py',p/'reliability_lab/config.py'])
