"""Cross-platform replay: numerical tolerance, not cross-host hash identity.
Original on-host audit results retain exact hashes; Linux CI reports numerical parity.
"""
from .live_audit import audit
from .live import optimize,adam_unpack
from .model import deserialize
import numpy as np

def verify(data,atol=1e-9):
 base=audit(data,replay=False);work={w['gid']:w['group'] for w in data['work'] if w['group']};ref=deserialize(data['policies'][0]['model']);model=deserialize(data['policies'][0]['model']);opt=adam_unpack(data['policies'][0]['optimizer']);max_error=0.
 for p in data['policies'][1:]:
  model,opt,_=optimize(model,opt,ref,[work[i] for i in p['update']['gids']],data['protocol']['gradient_steps']);target=deserialize(p['model']);expected=adam_unpack(p['optimizer'])
  for k in model:
   max_error=max(max_error,float(np.max(np.abs(model[k]-target[k]))));np.testing.assert_allclose(model[k],target[k],rtol=1e-9,atol=atol)
   np.testing.assert_allclose(opt['first'][k],expected['first'][k],rtol=1e-9,atol=atol);np.testing.assert_allclose(opt['second'][k],expected['second'][k],rtol=1e-9,atol=atol)
 return {**base,'numerical_replayed_updates':len(data['policies'])-1,'max_model_absolute_error':max_error,'cross_platform_exact_hash_claim':False,'tolerance_atol':atol}
