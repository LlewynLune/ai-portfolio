"""Strong deterministic baselines for explicitly synthetic key/value grammar.
Runs on frozen investigation prefixes; no effect on model outputs.
"""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def lookup(tokens,shift):
 pairs={tokens[i]:tokens[i+1] for i in range(0,len(tokens)-2,2)}
 q=tokens[-1]
 if q not in pairs:return None
 return 8+(pairs[q]-8+shift)%8

def build():
 for folder in ['tiny-attention','lora-lab','dpo-lab']:
  p=ROOT/'projects'/folder/'artifacts/investigation';d=json.loads((p/'results.json').read_text());rows=[]
  for r in d['records']:
   if folder=='tiny-attention':tokens=r['counterfactual'];target=r['target'];shift=0
   elif folder=='lora-lab':tokens=None;continue
   else:tokens=r['prefix'];target=r['chosen'];shift=2
   pred=lookup(tokens,shift);rows.append({'record_key':str(r.get('seed'))+':'+str(r.get('id',r.get('index')))+':'+str(r.get('policy',r.get('intervention'))),'truth':target,'prediction':pred,'correct':pred==target})
  if folder=='lora-lab':
   # Original exporter retained only predictions, not prefixes. Regenerate deterministic new set.
   import sys;sys.path.insert(0,str(ROOT/'projects'));from depth_support import load,generate_lookup
   excluded=sum(load(ROOT/'projects/lora-lab/artifacts/results.json')['split_ids'].values(),[])+sum(load(ROOT/'projects/tiny-attention/artifacts/results.json')['split_ids'].values(),[])
   for seed in [192001,192002,192003]:
    x,y=generate_lookup(128,seed,3,exclude=excluded)
    for i,t in enumerate(x.tolist()):
     for shift in [0,1]:rows.append({'record_key':f'{seed}:{i}:shift{shift}','truth':int(8+(y[i]-8+shift)%8),'prediction':lookup(t,shift),'correct':lookup(t,shift)==int(8+(y[i]-8+shift)%8)})
  baseline={'kind':'deterministic_finite_keyvalue_parser','llm_used':False,'training_used':False,'scope':'Privileged exact task grammar and synthetic rule shift known. Appropriate strong baseline, not language understanding. Correlated repeated conditions not independent test instances.','n':len(rows),'correct':sum(r['correct'] for r in rows),'records':rows,'source_sha256':hashlib.sha256((p/'results.json').read_bytes()).hexdigest()}
  (p/'rule-baseline.json').write_text(json.dumps(baseline,indent=2)+'\n');print(folder,'rule baseline',baseline['correct'], '/',len(rows))
if __name__=='__main__':build()
