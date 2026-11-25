"""Independent numerical/contract tests, no MLX/GPU required."""
import unittest,json,sys,hashlib,tempfile
from pathlib import Path
try:
 import numpy as np
except ImportError:
 np=None
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'projects'))
if np is not None:
 from investigations.common import Attention,load,hidden,finite_quantile
 from investigations.algorithms import acceptance_distribution
@unittest.skipIf(np is None,'NumPy required; full verification runs in dependency-installed job')
class InvestigationTests(unittest.TestCase):
 def test_fourteen_frozen_packages(self):
  files=list((ROOT/'projects').glob('*/artifacts/investigation/results.json'));self.assertEqual(len(files),14)
  for path in files:
   d=json.loads(path.read_text());self.assertTrue(d['records']);self.assertTrue(d['metrics']);self.assertEqual(d['project'],path.parent.parent.parent.name)
   checks=json.loads((path.parent/'checksums.json').read_text())
   for name,h in checks.items():self.assertEqual(hashlib.sha256((path.parent/name).read_bytes()).hexdigest(),h)
 def test_original_evidence_remains(self):
  # Old Depth protocols retained, new investigation resides in another directory.
  for path in (ROOT/'projects').glob('*/artifacts/investigation/results.json'):
   self.assertTrue((path.parents[1]/'depth/results.json').is_file())
 def test_conformal_finite_rank(self):
  q,k=finite_quantile([.1,.2,.3,.4],.2);self.assertEqual(k,4);self.assertEqual(q,.4)
  q,k=finite_quantile([.1,.2],.05);self.assertIsNone(q)
 def test_hidden_state_export_parity(self):
  m=load(ROOT/'projects/tiny-attention/artifacts/model.json');x=np.array([[0,8,1,9,2,10,16,1],[3,12,4,15,2,9,16,2]])
  h=hidden(x,m);actual=h@np.array(m['state']['head.weight']).T+m['state']['head.bias'];expected=Attention(m).forward(x)[:,-1];self.assertLess(np.max(abs(actual-expected)),1e-10)
 def test_dpo_gradient_finite_difference(self):
  rng=np.random.default_rng(209);h=rng.normal(size=(5,3));W=rng.normal(size=(4,3));chosen=np.array([0,1,2,3,0]);rejected=(chosen+1)%4;reference=rng.normal(size=5);beta=.5
  def loss(w):
   z=h@w.T;delta=z[np.arange(5),chosen]-z[np.arange(5),rejected];return np.logaddexp(0,-beta*(delta-reference)).mean()
  z=h@W.T;delta=z[np.arange(5),chosen]-z[np.arange(5),rejected];c=-beta/(1+np.exp(beta*(delta-reference)))/5;g=np.zeros((5,4));g[np.arange(5),chosen]=c;g[np.arange(5),rejected]=-c;analytic=g.T@h
  eps=1e-6
  for i in range(4):
   for j in range(3):
    a=W.copy();b=W.copy();a[i,j]+=eps;b[i,j]-=eps;self.assertAlmostEqual((loss(a)-loss(b))/(2*eps),analytic[i,j],places=7)
 def test_dpo_all_training_runs_loss_reduced(self):
  d=load(ROOT/'projects/dpo-lab/artifacts/investigation/results.json');self.assertEqual(len(d['details']['loss_curves']),9)
  for c in d['details']['loss_curves'].values():self.assertLess(c[-1]['loss'],c[0]['loss'])
 def test_sampling_recovers_target_distribution(self):
  p=np.array([.2,.3,.5]);q=np.array([.6,.1,.3]);actual,accept=acceptance_distribution(p,q);np.testing.assert_allclose(actual,p,atol=1e-14);self.assertAlmostEqual(accept,.6)
  actual,_=acceptance_distribution(p,p);np.testing.assert_allclose(actual,p)
 def test_sampling_analytic_all_contexts(self):
  d=load(ROOT/'projects/spec-decode/artifacts/investigation/results.json')
  for r in d['records']:np.testing.assert_allclose(r['analytic_probabilities'],r['target_probabilities'],atol=1e-12)
 def test_moe_capacity_not_hidden(self):
  d=load(ROOT/'projects/moe-lab/artifacts/investigation/results.json')
  groups={}
  for r in d['records']:groups.setdefault((r['seed'],r['capacity'],r['policy'],r['order']),[]).append(r)
  for key,rows in groups.items():
   cap=int(np.ceil(256/4*key[1]))
   for expert in range(4):self.assertLessEqual(sum(r['route']==expert for r in rows),cap)
   self.assertEqual(len(rows),256)
 def test_process_crash_recovery(self):
  d=load(ROOT/'projects/reliability-lab/artifacts/investigation/results.json');rows=[r for r in d['records'] if r.get('kind')=='abrupt_exit'];self.assertEqual(len(rows),18)
  for r in rows:self.assertEqual(r['exit_code'],73)
  self.assertTrue(all(r['duplicate_effects']==0 for r in rows if r['strategy']=='resilient'))
  self.assertTrue(any(r['duplicate_effects']>0 for r in rows if r['strategy']=='retry' and r['point']=='after_effect_before_checkpoint'))
 def test_prequential_update_does_not_see_current_error(self):
  d=load(ROOT/'projects/power-scope/artifacts/investigation/results.json');groups={}
  for r in d['records']:
   if r['method']=='past_residual_quantile':groups.setdefault(r['condition'],[]).append(r)
  for rr in groups.values():
   hist=[]
   for r in rr:
    if len(hist)>=32:self.assertAlmostEqual(r['radius_kw'],np.quantile(hist[-288:],.9))
    hist.append(r['error_kw'])
 def test_video_prefix_causality(self):
  d=load(ROOT/'projects/video-guard/artifacts/investigation/results.json');self.assertGreater(d['details']['prefix_comparisons'],10000);self.assertEqual(d['details']['prefix_mismatch'],0)
 def test_new_cite_queries_and_raw_outputs(self):
  p=ROOT/'projects/cite-rag';old=load(p/'data/memory/episodes.json');new=load(p/'artifacts/investigation/dataset.json');self.assertFalse({q['id'] for q in old['queries']}&{q['id'] for q in new['queries']});d=load(p/'artifacts/investigation/results.json');self.assertEqual(d['details']['actual_calls'],97)
  for r in d['records']:self.assertTrue(r['call']['llm_used']);self.assertEqual(hashlib.sha256(r['call']['text'].encode()).hexdigest(),r['call']['raw_output_sha256'])
 def test_channel_geometry_rank(self):
  d=load(ROOT/'projects/channel-est/artifacts/investigation/results.json');full=[r for r in d['metrics'] if r['geometry']=='full'];self.assertTrue(all(r['rank']==4 for r in full));cluster=[r for r in d['metrics'] if r['geometry']=='clustered'];spread=[r for r in d['metrics'] if r['geometry']=='spread'];self.assertGreater(cluster[0]['condition_number'],spread[0]['condition_number'])
 def test_fourteen_viewers_match_real_evidence(self):
  import re
  for path in (ROOT/'projects').glob('*/deep-study.html'):
   text=path.read_text();embedded=json.loads(re.search(r'const DATA=(.*?);const',text,re.S)[1]);source=load(path.parent/'artifacts/investigation/results.json');self.assertEqual(embedded,source['records']);self.assertIn('Next Uncompleted Work',text)
 def test_dpo_split_audit_exists_and_disjoint(self):
  d=load(ROOT/'projects/dpo-lab/artifacts/investigation/split-audit.json');self.assertEqual(len(d),3)
  for r in d.values():self.assertEqual(r['within_seed_overlap'],0);self.assertEqual(r['prior_overlap'],0);self.assertEqual(r['test'],192)
 def test_business_analysis_no_added_facts(self):
  d=load(ROOT/'profile/resume.json')
  for c in d['cases']:
   p=ROOT/'business-cases'/c['id']/'PRODUCT_ANALYSIS.md';text=p.read_text();self.assertIn('建议测试，不声称',text);self.assertIn(c['overview'],text);self.assertIn(c['evidence'],text)
if __name__=='__main__':unittest.main()
