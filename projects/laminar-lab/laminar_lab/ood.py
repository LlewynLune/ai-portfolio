"""Length-OOD fixed-model probes; new lengths cannot duplicate <=8 training prompts.
Exploratory after initial results, same grammar; not semantic LLM generalization.
"""
import json
from pathlib import Path
import numpy as np
from .model import deserialize,forward,features

def main():
 out=Path('artifacts/ood-length.json')
 if out.exists():raise FileExistsError(out)
 records=[];rng=np.random.default_rng(9917);prompts=[rng.integers(0,4,length).tolist() for length in [12,16] for _ in range(64)]
 for file in sorted(Path('artifacts/controlled').glob('*-*.json')):
  d=json.loads(file.read_text());m=deserialize(d['final_model']);rows=[]
  for i,p in enumerate(prompts):
   previous=0;actions=[];pr=[]
   for pos in range(len(p)):
    prob,_=forward(features(p,pos,previous)[None],m);a=int(prob.argmax());actions.append(a);pr.append(prob[0].tolist());previous=a
   target=[(v+1)%4 for v in p];rows.append({'probe':i,'length':len(p),'prompt':p,'actions':actions,'target':target,'token_accuracy':float(np.mean(np.array(actions)==target)),'probabilities':pr})
  records.append({'run':file.name,'seed':d['summary']['seed'],'mode':d['summary']['mode'],'mean_token_accuracy':float(np.mean([r['token_accuracy'] for r in rows])),'exact_sequence_rate':float(np.mean([r['actions']==r['target'] for r in rows])),'no_exact_training_prompt_overlap':True,'deterministic_rule_baseline':1.,'probes':rows})
 out.write_text(json.dumps({'note':'Lengths12/16 vs train1/2/4/8; fixed identical prompts across policies, evaluated after initial results, same known synthetic grammar; not general language benchmark.','runs':records},allow_nan=False));print([(r['run'],round(r['mean_token_accuracy'],3)) for r in records])
if __name__=='__main__':main()
