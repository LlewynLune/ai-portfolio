"""Additional audit of full implementation chain and generated-data separation.
No old result overwrite; hash all currently used investigation code and artifacts.
"""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'projects'))
from depth_support import generate_lookup,load

def build():
 manifest={'source_code_sha256':{},'artifact_sha256':{},'original_evidence_sha256':{},'scope':'integrity only, not signed proof, independent model eval or confidentiality audit'}
 for p in list((ROOT/'projects/investigations').glob('*.py'))+[ROOT/'projects/depth_support.py']+list((ROOT/'scripts').glob('*investigation*.py')):
  manifest['source_code_sha256'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 for p in (ROOT/'projects').glob('*/artifacts/investigation/*'):
  if p.is_file():manifest['artifact_sha256'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 for p in (ROOT/'projects').glob('*/artifacts/*'):
  if p.is_file() and p.name in ['model.json','results.json','REPORT.md']:manifest['original_evidence_sha256'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 splits={}
 excluded=sum(load(ROOT/'projects/dpo-lab/artifacts/results.json')['split_ids'].values(),[])+sum(load(ROOT/'projects/tiny-attention/artifacts/results.json')['split_ids'].values(),[])
 prior={tuple(json.loads(s)) if isinstance(s,str) else tuple(s) for s in excluded}
 for seed in [193001,193002,193003]:
  x,y=generate_lookup(832,seed,3,exclude=excluded);tr={tuple(v) for v in x[:512]};va={tuple(v) for v in x[512:640]};te={tuple(v) for v in x[640:]};assert not tr&va and not tr&te and not va&te and not (tr|va|te)&prior
  splits[str(seed)]={'train_sha256':hashlib.sha256(x[:512].tobytes()).hexdigest(),'validation_sha256':hashlib.sha256(x[512:640].tobytes()).hexdigest(),'test_sha256':hashlib.sha256(x[640:].tobytes()).hexdigest(),'train':512,'validation':128,'test':192,'within_seed_overlap':0,'prior_overlap':0,'cross_seed_overlap_not_claimed_absent':True}
 (ROOT/'docs/investigation-audit.json').write_text(json.dumps(manifest,indent=2)+'\n');(ROOT/'projects/dpo-lab/artifacts/investigation/split-audit.json').write_text(json.dumps(splits,indent=2)+'\n')
 print('source/audit',len(manifest['source_code_sha256']),len(manifest['artifact_sha256']),'DPO splits within/prior disjoint')
if __name__=='__main__':build()
