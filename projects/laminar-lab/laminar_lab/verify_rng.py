"""Additional independent persisted RNG-state check, without changing frozen runtime."""
import json
from pathlib import Path
import numpy as np
from .model import deserialize,features,forward
from .live import canonical

def verify(root):
 rows=[]
 for dirname in ['live-system','live-crash-boundaries']:
  for file in sorted((Path(root)/dirname).glob('*.json')):
   if file.name in ['protocol.json','summary.json'] or file.name.endswith('-config.json'):continue
   d=json.loads(file.read_text());policies={p['version']:deserialize(p['model']) for p in d['policies']};checks=0
   for w in d['work']:
    state=w['state'];j=state['sample_index'];rng=np.random.default_rng(d['protocol']['seed']*1000000+w['gid']*10+j);m=policies[w['policy_version']];previous=0
    for pos,a in enumerate(state['actions']):
     pr,_=forward(features(w['prompt'],pos,previous)[None],m);draw=int(rng.choice(4,p=pr[0]));assert draw==a,'saved draw changed';previous=draw
    assert canonical(rng.bit_generator.state)==canonical(state['rng']),'saved RNG state mismatch';checks+=1
   rows.append({'file':str(file.relative_to(root)),'saved_rng_states_recomputed':checks,'all_passed':True})
 return rows
if __name__=='__main__':
 root=Path('artifacts');out=root/'live-rng-audit.json'
 if out.exists():raise FileExistsError(out)
 rows=verify(root);out.write_text(json.dumps(rows,indent=2));print('Independent persisted RNG-state checks',sum(r['saved_rng_states_recomputed'] for r in rows))
