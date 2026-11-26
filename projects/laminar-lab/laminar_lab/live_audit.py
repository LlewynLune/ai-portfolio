"""Independent live evidence validator and exact optimizer replay.
Hash chain is tamper evidence, not a signature or third-party attestation.
"""
import copy,json,hashlib
from pathlib import Path
import numpy as np
from .live import digest,canonical,adam_init,adam_unpack,optimize,prompt_for
from .model import deserialize,model_hash,rollout

def audit(data,replay=True):
 cfg=data['protocol'];policies={p['version']:p for p in data['policies']};work={w['gid']:w for w in data['work']};prev='0'*64
 assert sorted(policies)==list(range(cfg['updates']+1)),'missing policy version'
 for p in policies.values():assert model_hash(deserialize(p['model']))==p['model_sha256'],'weight hash mismatch'
 for e in data['events']:
  assert e['prev_hash']==prev,'audit chain predecessor';assert digest({'session':e['session'],'kind':e['kind'],'body':e['body'],'prev_hash':prev})==e['event_hash'],'audit hash mismatch';prev=e['event_hash']
 independently_scored=0;recovered_prefixes=0
 for w in work.values():
  assert w['prompt']==prompt_for(cfg['seed'],w['gid']),'prompt mismatch';v=w['policy_version'];m=deserialize(policies[v]['model']);state=w['state']
  for j,sample in enumerate(state['samples']):
   full=rollout(w['prompt'],m,v,cfg['seed']*1000000+w['gid']*10+j)
   assert sample['actions']==full['actions'],'trajectory version/RNG action mismatch';np.testing.assert_allclose(sample['behavior_logp'],full['behavior_logp'],rtol=0,atol=1e-12)
   correct=sum(int(a)==(int(x)+1)%4 for a,x in zip(sample['actions'],w['prompt']))/len(w['prompt']);assert abs(correct-sample['reward'])<1e-12,'independent reward mismatch';assert sample['policy_version']==v and sample['behavior_model_sha256']==policies[v]['model_sha256'],'mixed policy';independently_scored+=1
  if state['actions']:
   full=rollout(w['prompt'],m,v,cfg['seed']*1000000+w['gid']*10+state['sample_index']);assert state['actions']==full['actions'][:len(state['actions'])],'saved partial mismatch'
  if w['group']:
   g=w['group'];assert g['samples']==state['samples'] and len(g['samples'])==4,'partial group admitted';assert g['scorer_sha256']==digest(g['scorer']),'scorer manifest mismatch'
 for e in data['events']:
  if e['kind']=='resume_prefix' and e['body']['saved_tokens']>0:recovered_prefixes+=1
 ledger=data['commit_ledger'];assert len({r['gid'] for r in ledger})==len(ledger),'duplicate consumption';assert len(ledger)==cfg['updates']*cfg['batch_groups'],'consumption count';assert sum(data['counts'].values())==len(work),'inventory not conserved'
 for row in ledger:assert work[row['gid']]['status']=='consumed','ledger status mismatch'
 ref=deserialize(policies[0]['model']);m=deserialize(policies[0]['model']);opt=adam_unpack(policies[0]['optimizer']);replayed=0
 for v in range(1,cfg['updates']+1):
  p=policies[v];u=p['update'];gids=u['gids'];groups=[work[i]['group'] for i in gids];assert len(gids)==cfg['batch_groups'];assert u['consume_staleness']==[v-1-g['policy_version'] for g in groups]
  if cfg['staleness_bound'] is not None:assert max(u['consume_staleness'])<=cfg['staleness_bound'],'staleness violation'
  assert p['optimizer']['step']==v*cfg['gradient_steps'],'Adam step mismatch'
  if replay:
   m,opt,diagnostics=optimize(m,opt,ref,groups,cfg['gradient_steps']);assert model_hash(m)==p['model_sha256'],'exact learner replay mismatch';assert canonical(opt['step'])==canonical(p['optimizer']['step']);assert digest({'first':{k:x.tolist() for k,x in opt['first'].items()},'second':{k:x.tolist() for k,x in opt['second'].items()}})==digest({'first':p['optimizer']['first'],'second':p['optimizer']['second']}),'Adam state mismatch';replayed+=1
 return {'all_checks_passed':True,'independent_trajectory_rewards':independently_scored,'replayed_adam_updates':replayed,'consumed_groups':len(ledger),'events_verified':len(data['events']),'sessions':len(data['sessions']),'restored_nonempty_prefixes':recovered_prefixes,'no_duplicate_consumption':True,'version_consistent':True,'inventory_conserved':True,'hash_chain_not_signature':True}

def tamper_checks(data):
 attacks=[]
 for name in ['reward','logprob','version','event_hash','optimizer']:
  d=copy.deepcopy(data);item=next(w for w in d['work'] if w['group']);s=item['state']['samples'][0]
  if name=='reward':s['reward']+=.01
  elif name=='logprob':s['behavior_logp'][0]+=.1
  elif name=='version':s['policy_version']+=1
  elif name=='event_hash':d['events'][0]['event_hash']='f'*64
  else:d['policies'][-1]['optimizer']['step']+=1
  rejected=False
  try:audit(d,replay=False)
  except (AssertionError,ValueError,KeyError):rejected=True
  assert rejected,'tamper accepted';attacks.append({'kind':name,'detected':rejected,'scope':'offline independent replay audit, not cryptographic authenticity'})
 return attacks
