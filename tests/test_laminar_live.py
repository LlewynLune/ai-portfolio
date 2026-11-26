"""Live asynchronous RL evidence and unit contracts; not model quality validation."""
import unittest,sys,json,tempfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT/'projects/laminar-lab';sys.path.insert(0,str(PROJECT))
try:
 import numpy as np
 from laminar_lab.live import Ledger,adam_init,adam_step,adam_pack,adam_unpack,canonical,prompt_for
 from laminar_lab.live_audit import audit,tamper_checks
 from laminar_lab.model import init,model_hash
except ImportError:np=None

@unittest.skipIf(np is None,'Dependency-installed depth CI runs live numerical contracts')
class LiveTests(unittest.TestCase):
 def test_adam_first_step_independent(self):
  m=init(7);g={k:np.full_like(v,.3) for k,v in m.items()};new,opt,norm=adam_step(m,g,adam_init(m),lr=.02)
  self.assertEqual(opt['step'],1)
  # Norm clipping is part of the optimizer; independently calculate its scalar.
  clipped=.3*min(1.,5/np.sqrt(sum(v.size for v in m.values())*.3**2))
  for k in m:np.testing.assert_allclose(new[k],m[k]-.02*clipped/(clipped+1e-8),rtol=0,atol=1e-12)
 def test_adam_restore_exact_continuation(self):
  m=init(7);g={k:np.full_like(v,.1) for k,v in m.items()};m,o,_=adam_step(m,g,adam_init(m));packed=json.loads(canonical(adam_pack(o)));a,oa,_=adam_step(m,g,o);b,ob,_=adam_step(m,g,adam_unpack(packed));self.assertEqual(model_hash(a),model_hash(b));self.assertEqual(canonical(adam_pack(oa)),canonical(adam_pack(ob)))
 def test_capacity_is_hard_inventory_bound(self):
  with tempfile.TemporaryDirectory() as d:
   c={'seed':7,'capacity':2};l=Ledger(Path(d)/'x.sqlite',c);self.assertIsNotNone(l.claim());self.assertIsNotNone(l.claim());self.assertIsNone(l.claim());l.conn.close()
 def test_resume_rejects_config_change(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.sqlite';l=Ledger(p,{'seed':7,'capacity':2});l.conn.close()
   with self.assertRaises(ValueError):Ledger(p,{'seed':7,'capacity':3})
 def test_restart_claims_old_version(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.sqlite';l=Ledger(p,{'seed':7,'capacity':2});gid,v,prompt,state=l.claim();l.conn.close();l=Ledger(p,{'seed':7,'capacity':2});i,v2,p2,s2=l.claim();self.assertEqual((gid,v,prompt,state),(i,v2,p2,s2));l.conn.close()
 def test_all_live_runs_reward_and_optimizer_replay(self):
  files=[p for p in (PROJECT/'artifacts/live-system').glob('*.json') if p.name not in ['protocol.json','summary.json'] and not p.name.endswith('-config.json')];self.assertEqual(len(files),20)
  for p in files:
   d=json.loads(p.read_text());self.assertEqual(audit(d,replay=False)['consumed_groups'],d['audit']['consumed_groups'])
   from laminar_lab.portable_replay import verify
   self.assertEqual(verify(d)['numerical_replayed_updates'],20)
   for name,h in d['source_hashes'].items():self.assertEqual(hashlib.sha256((PROJECT/'laminar_lab'/name).read_bytes()).hexdigest(),h)
 def test_tamper_is_detected_not_authenticity_claim(self):
  d=json.loads((PROJECT/'artifacts/live-system/7-none.json').read_text());self.assertEqual(len(tamper_checks(d)),5);self.assertTrue(all(x['detected'] for x in d['tamper_checks']))
 def test_crash_snapshot_atomicity(self):
  d=json.loads((PROJECT/'artifacts/live-crash-boundaries/summary.json').read_text());self.assertEqual(len(d['runs']),4)
  for r in d['runs']:
   b=r['before_restart']
   if r['fault'] in ['before_commit','inside_commit']:self.assertEqual(b['latest_committed_version'],4);self.assertEqual(b['consumption_rows'],24);self.assertEqual(b['committed_adam_step'],16)
   if r['fault']=='after_commit':self.assertEqual(b['latest_committed_version'],5);self.assertEqual(b['consumption_rows'],30);self.assertEqual(b['committed_adam_step'],20);self.assertEqual(b['pending_batches'],[])
 def test_boundary_runs_replay_after_restart(self):
  for p in (PROJECT/'artifacts/live-crash-boundaries').glob('*.json'):
   if p.name in ['protocol.json','summary.json'] or p.name.endswith('-config.json'):continue
   from laminar_lab.portable_replay import verify
   d=json.loads(p.read_text());self.assertTrue(verify(d)['all_checks_passed']);self.assertEqual(d['summary']['adam_step'],80)
 def test_all_saved_rng_states(self):
  from laminar_lab.verify_rng import verify
  rows=verify(PROJECT/'artifacts');self.assertEqual(len(rows),24);self.assertTrue(all(r['all_passed'] for r in rows))
 def test_no_duplicate_consumption_at_crashes(self):
  d=json.loads((PROJECT/'artifacts/live-system/summary.json').read_text());self.assertEqual(d['total_real_process_crashes'],12)
  for r in d['runs']:self.assertTrue(r['audit']['no_duplicate_consumption']);self.assertEqual(r['audit']['consumed_groups'],120)
if __name__=='__main__':unittest.main()
