"""Independent gradient, version, packing, immutability and restart contracts."""
import unittest,sys,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'projects/laminar-lab'))
try:
 import numpy as np
 from laminar_lab.model import init,group,objective_gradient,apply,model_hash
 from laminar_lab.planes import Relay,Pool,best_fit
except ImportError:
 np=None

@unittest.skipIf(np is None,'NumPy required; dependency-installed depth job executes these contracts')
class LaminarContracts(unittest.TestCase):
 def test_gradient_finite_difference(self):
  m=init(7);batch=[group(7,i,m,0) for i in range(3)];ref=init(8);loss,g,_=objective_gradient(m,ref,batch)
  for k,idx in [('w1',(2,3)),('w2',(3,1)),('b1',(3,)),('b2',(1,))]:
   orig=m[k][idx];eps=1e-5;m[k][idx]=orig+eps;plus=objective_gradient(m,ref,batch)[0];m[k][idx]=orig-eps;minus=objective_gradient(m,ref,batch)[0];m[k][idx]=orig
   self.assertAlmostEqual(g[k][idx],(plus-minus)/(2*eps),places=7)
 def test_immutable_relay(self):
  m=init(7);r=Relay(m);v,p,h=r.pull();p['w1'][:]=0;m['w1'][:]=1;self.assertEqual(r.pull(0)[2],h);self.assertEqual(model_hash(r.pull(0)[1]),h)
  with self.assertRaises(ValueError):r.publish(0,m)
 def test_single_version_sequence(self):
  r=Relay(init(7));v,m,h=r.pull();r.publish(1,init(8));g=group(7,10,m,v)
  self.assertEqual(g['behavior_model_sha256'],h);self.assertEqual({s['policy_version'] for s in g['samples']},{0})
 def test_partial_version_rejection(self):
  p=Pool();p.save_partial('x',0,[1,2]);p.save_partial('x',0,[1,2,3])
  with self.assertRaises(ValueError):p.save_partial('x',1,[1,2,3,4])
  with self.assertRaises(ValueError):p.save_partial('x',0,[4,2,3])
  p.close()
 def test_experience_idempotent(self):
  p=Pool();g=group(7,0,init(7),0);self.assertTrue(p.complete(g));self.assertFalse(p.complete(g));g['prompt']=[2]
  with self.assertRaises(ValueError):p.complete(g)
  p.close()
 def test_checkpoint_restart(self):
  with tempfile.TemporaryDirectory() as d:
   p=Pool(Path(d)/'pool.sqlite');p.checkpoint(2,init(7));p.close();p=Pool(Path(d)/'pool.sqlite');v,m=p.latest_checkpoint();self.assertEqual(v,2);self.assertEqual(model_hash(m),model_hash(init(7)));p.close()
 def test_packing_version_capacity(self):
  replicas=[{'id':i,'version':i%2,'cache':2+i%3,'requests':2,'ramp_down':True} for i in range(9)];plan,remaining=best_fit(replicas,12,8)
  self.assertTrue(plan)
  for move in plan:self.assertEqual(replicas[move['source']]['version'],replicas[move['destination']]['version'])
  self.assertEqual(sum(x['cache'] for x in remaining.values()),sum(x['cache'] for x in replicas));self.assertTrue(all(x['cache']<=12 and x['requests']<=8 for x in remaining.values()))
 def test_no_pack_rampup(self):
  rows=[{'id':i,'version':0,'cache':1,'requests':1,'ramp_down':False} for i in range(3)];self.assertEqual(best_fit(rows,20,10)[0],[])
 def test_current_ratio_at_start(self):
  m=init(7);_,_,d=objective_gradient(m,m,[group(7,0,m,0)]);self.assertAlmostEqual(d['ratio_mean'],1);self.assertEqual(d['clip_fraction'],0)
 def test_unratio_reinforce_gradient(self):
  m=init(7);batch=[group(7,i,m,0) for i in range(3)];_,g,_=objective_gradient(m,m,batch,correct=False);eps=1e-5;orig=m['w2'][3,1];m['w2'][3,1]=orig+eps;plus=objective_gradient(m,m,batch,correct=False)[0];m['w2'][3,1]=orig-eps;minus=objective_gradient(m,m,batch,correct=False)[0];m['w2'][3,1]=orig;self.assertAlmostEqual(g['w2'][3,1],(plus-minus)/(2*eps),places=6)
 def test_frozen_controlled_audit(self):
  from laminar_lab.study import audit
  root=Path(__file__).resolve().parents[1]/'projects/laminar-lab/artifacts';self.assertEqual(len(audit(root)),12)
 def test_length_ood_excludes_train_lengths(self):
  d=json.loads((Path(__file__).resolve().parents[1]/'projects/laminar-lab/artifacts/ood-length.json').read_text());self.assertEqual(len(d['runs']),12)
  for run in d['runs']:
   self.assertEqual(len(run['probes']),128);self.assertTrue(all(p['length']>8 for p in run['probes']))
 def test_durable_learner_actual_failures(self):
  root=Path(__file__).resolve().parents[1]/'projects/laminar-lab';d=json.loads((root/'artifacts/system/durable-learner.json').read_text());self.assertEqual(len(d['results']),9)
  for r in d['results']:
   self.assertTrue(r['exact_model_and_consumption_match']);self.assertEqual(r['recovered']['consumption_count'],72);self.assertEqual(r['baseline']['final_sha256'],r['recovered']['final_sha256']);self.assertIn(r['killed_returncode'],[81,82,83])
 def test_paired_frozen_ratio_reconstruction(self):
  root=Path(__file__).resolve().parents[1]/'projects/laminar-lab';d=json.loads((root/'artifacts/paired-replay.json').read_text());self.assertEqual(len(d['cases']),3)
  for c in d['cases']:self.assertTrue(c['ratio_matches_frozen_model']);self.assertTrue(c['same_fixed_samples']);self.assertEqual(len(c['updates']),40)
 def test_optimizer_really_changes_weights(self):
  m=init(7);_,g,_=objective_gradient(m,m,[group(7,i,m,0) for i in range(6)]);n,_=apply(m,g,.8);self.assertNotEqual(model_hash(m),model_hash(n))
if __name__=='__main__':unittest.main()
