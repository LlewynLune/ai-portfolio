"""Deterministic packing stress, pinned upstream planner contracts, evidence audit."""
import json,hashlib,sys,importlib.util
from pathlib import Path
import numpy as np
from .planes import best_fit
from .model import deserialize,model_hash,evaluate
REVISION='19333d00b8d794a145a07b6c082a1fa3cf84c42e'

def run(output,upstream=None):
 out=Path(output);out.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(811);records=[]
 for i in range(300):
  replicas=[{'id':j,'version':int(rng.integers(0,3)),'cache':float(rng.uniform(.01,.85)),'requests':int(rng.integers(1,8)),'ramp_down':bool(rng.integers(2))} for j in range(int(rng.integers(4,20)))];cap=1.;bc=16;plan,remaining=best_fit(replicas,cap,bc)
  assert abs(sum(r['cache'] for r in replicas)-sum(r['cache'] for r in remaining.values()))<1e-10
  assert sum(r['requests'] for r in replicas)==sum(r['requests'] for r in remaining.values())
  for p in plan:assert replicas[p['source']]['version']==replicas[p['destination']]['version']
  assert all(r['cache']<=cap+1e-10 and r['requests']<=bc for r in remaining.values())
  records.append({'case':i,'replicas':replicas,'plan':plan,'after':list(remaining.values()),'released':len(replicas)-len(remaining)})
 (out/'packing.json').write_text(json.dumps({'seed':811,'cases':records,'note':'Synthetic loads; planner only, no GPU KV movement or throughput inference.'}))
 if upstream:
  file=Path(upstream)/'src/laminar/multi_version_rollout/repack.py';spec=importlib.util.spec_from_file_location('pinned_laminar_repack',file);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);tests=[]
  for i in range(100):
   rows=[m._RepackServerView(str(j),int(rng.integers(0,3)),True,True,float(rng.uniform(.01,.7)),int(rng.integers(1,7))) for j in range(12)];plans=m._plan_repack_groups(rows,loadable_version=3,source_max_kv_cache_usage=.3,destination_max_kv_cache_usage=.9,excluded_servers=frozenset());byid={r.server_id:r for r in rows}
   for p in plans:
    assert all(byid[s].weight_version==p.weight_version for s in p.sources);assert byid[p.destination].weight_version==p.weight_version
    assert sum(byid[s].kv_cache_usage for s in p.sources)+byid[p.destination].kv_cache_usage<=.9+1e-10
   tests.append({'case':i,'groups':len(plans),'released':sum(len(p.sources) for p in plans)})
  (out/'upstream-contracts.json').write_text(json.dumps({'repo':'https://github.com/verl-project/laminar','revision':REVISION,'file':'src/laminar/multi_version_rollout/repack.py','sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'tests':tests,'execution':'Directly execute unmodified upstream pure planner via importlib; NOT run Laminar RL trainer, vLLM, CUDA, Ray, or official complete suite.'},indent=2))

def audit(root):
 root=Path(root);audits=[];rng=np.random.default_rng(8801);probes=[]
 for i in range(160):length=int(rng.choice([1,2,4,8]));probes.append(tuple(rng.integers(0,4,length).tolist()))
 for file in sorted((root/'controlled').glob('*-*.json')):
  d=json.loads(file.read_text());s=d['summary'];hashes=d['model_hashes'];ids=[];tokens=0;consumed={i for u in d['updates'] for i in u['groups']}
  for g in d['groups']:
   ids.append(g['gid']);assert g['behavior_model_sha256']==hashes[str(g['policy_version'])];assert g['inherent_staleness']==g['finish_version']-g['policy_version']
   for sample in g['samples']:
    assert sample['policy_version']==g['policy_version'];assert sample['behavior_model_sha256']==g['behavior_model_sha256'];assert sample['length']==len(sample['actions']);assert abs(sample['reward']-np.mean(np.array(sample['actions'])==sample['target']))<1e-12
   if g['gid'] in consumed:tokens+=4*g['length']
  assert len(ids)==len(set(ids));assert tokens==s['actual_sampled_tokens_consumed'];assert model_hash(deserialize(d['final_model']))==s['final_model_sha256'];assert evaluate(deserialize(d['final_model']))==s['final']
  for name,h in d['source_hashes'].items():assert hashlib.sha256((root.parent/'laminar_lab'/name).read_bytes()).hexdigest()==h
  training_prompts={tuple(g['prompt']) for g in d['groups'] if g['gid'] in consumed};overlap=sum(p in training_prompts for p in probes)
  audits.append({'file':file.name,'groups':len(ids),'consumed_tokens':tokens,'probe_exact_prompt_overlap':overlap,'probe_count':len(probes),'independent_holdout':False,'all_checks_passed':True})
 (root/'audit.json').write_text(json.dumps(audits,indent=2));return audits
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--upstream');p.add_argument('--output',default='artifacts/system');p.add_argument('--audit',default='artifacts');a=p.parse_args();run(a.output,a.upstream);print('verified',len(audit(a.audit)),'controlled runs')
