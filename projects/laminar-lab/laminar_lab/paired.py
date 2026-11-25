"""Deterministic same-condition replay to isolate stale behavior-ratio ablation.
Saved samples + behavior logp held identical; sequential real updates, not live async.
"""
import json,hashlib
from pathlib import Path
import numpy as np
from .model import pretrain,features,objective_gradient,apply,evaluate,model_hash

def main():
 out=Path('artifacts/paired-replay.json')
 if out.exists():raise FileExistsError(out)
 cases=[]
 for seed in [7,19,41]:
  source=Path(f'artifacts/controlled/{seed}-async_ratio.json');d=json.loads(source.read_text());byid={g['gid']:g for g in d['groups']};initial,_=pretrain(seed);models={'ratio':{k:v.copy() for k,v in initial.items()},'no_ratio':{k:v.copy() for k,v in initial.items()}};records=[]
  for u in d['updates']:
   groups=[]
   for gid in u['groups']:
    raw=byid[gid];g=dict(raw);g['samples']=[]
    for s in raw['samples']:
     q=dict(s);q['features']=[features(raw['prompt'],pos,0 if pos==0 else s['actions'][pos-1]).tolist() for pos in range(s['length'])];g['samples'].append(q)
    groups.append(g)
   metrics={}
   for mode,m in models.items():
    for _ in range(4):loss,grad,diag=objective_gradient(m,initial,groups,correct=mode=='ratio');m,_=apply(m,grad,.8)
    models[mode]=m;metrics[mode]={'loss':loss,**diag,**evaluate(m),'model_sha256':model_hash(m)}
   records.append({'update':u['update'],'fixed_group_ids':u['groups'],'fixed_behavior_versions':[g['policy_version'] for g in groups],'metrics':metrics})
  # The ratio path must reconstruct the exact frozen control update chain.
  assert model_hash(models['ratio'])==d['summary']['final_model_sha256']
  cases.append({'seed':seed,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'same_fixed_samples':True,'ratio_matches_frozen_model':True,'ratio_final':evaluate(models['ratio']),'no_ratio_final':evaluate(models['no_ratio']),'updates':records})
 out.write_text(json.dumps({'protocol':'Off-policy replay on identical frozen ordered samples and behavior logprobs; isolates token-ratio choice, not live scheduling or on-policy counterfactual. Fixed toy probes with known overlap, no independent test claim.','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':cases},allow_nan=False));print('Paired replay exact reconstruction for',len(cases),'seeds')
if __name__=='__main__':main()
