import unittest,importlib.util,hashlib,json,sys,re,subprocess,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=['tiny-attention','lora-lab','dpo-lab','moe-lab','spec-decode'];HAS_TORCH=importlib.util.find_spec('torch') is not None

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class FrozenTests(unittest.TestCase):
 def test_integrity(self):
  for p in P:
   f=ROOT/'projects'/p/'artifacts';r=json.loads((f/'results.json').read_text());self.assertEqual(r['code_sha256'],hashlib.sha256((f.parent/'train.py').read_bytes()).hexdigest());self.assertEqual(r['support_sha256'],hashlib.sha256((ROOT/'projects/frontier_support.py').read_bytes()).hexdigest())
   for n,h in json.loads((f/'checksums.json').read_text()).items():self.assertEqual(h,hashlib.sha256((f/n).read_bytes()).hexdigest())
 def test_base_dependencies(self):
  h=hashlib.sha256((ROOT/'projects/tiny-attention/artifacts/model.json').read_bytes()).hexdigest()
  for p in ['lora-lab','dpo-lab']:self.assertEqual(json.loads((ROOT/'projects'/p/'artifacts/results.json').read_text())['base_model_sha256'],h)
 def test_disjoint_prefixes(self):
  for p in ['tiny-attention','lora-lab','dpo-lab']:
   s=json.loads((ROOT/'projects'/p/'artifacts/results.json').read_text())['split_ids'];a,b,c=[set(s[k]) for k in ('train','validation','test')];self.assertFalse(a&b or a&c or b&c)
 def test_native_export_parity(self):
  js=(ROOT/'scripts/build_frontier_demos.py').read_text();engine=re.search("ENGINE='''(.*?)'''",js,re.S)[1];cases=[]
  for p in P:
   f=ROOT/'projects'/p/'artifacts';cases.append({'project':p,'model':json.loads((f/'model.json').read_text()),'examples':json.loads((f/'results.json').read_text())['examples']})
  script=engine+'const cases='+json.dumps(cases)+';cases.forEach(c=>c.examples.forEach(e=>{if(c.project==="moe-lab"){const r=moe(e.input,c.model);if(Math.abs(r.output-e.output[0])>1e-5||r.route!==e.route)throw Error("moe parity");}else if(c.project==="spec-decode"){const g=greedy(c.model.target,e.tokens),s=speculate(c.model.target,c.model.draft,e.tokens,e.group.endsWith("2")?2:4);if(JSON.stringify(g)!==JSON.stringify(e.baseline_output)||JSON.stringify(s.output)!==JSON.stringify(g))throw Error("spec parity");}else{const p=transformer(e.tokens,c.model).probabilities;p.forEach((v,i)=>{if(Math.abs(v-e.probabilities[i])>2e-5)throw Error(c.project+" parity");});}}));'
  subprocess.run(['node','--input-type=commonjs'],input=script,text=True,capture_output=True,check=True)
 def test_spec_records_exact_and_timing(self):
  r=json.loads((ROOT/'projects/spec-decode/artifacts/results.json').read_text());self.assertTrue(all(x['exact'] for x in r['timings']));self.assertTrue(all(x['baseline_ms']>0 and x['speculative_ms']>0 for x in r['timings']))
 def test_classification_and_preference_recompute(self):
  for project in ['tiny-attention','lora-lab','dpo-lab']:
   r=json.loads((ROOT/'projects'/project/'artifacts/results.json').read_text())
   for row in r['metrics']:
    ps=[x for x in r['predictions'] if x['group']==row['group'] and x['model']==row['model']]
    if project=='dpo-lab':
     win=sum(x['probabilities'][x['chosen']]>x['probabilities'][x['rejected']] for x in ps)/len(ps);top=sum(max(range(18),key=lambda i:x['probabilities'][i])==x['chosen'] for x in ps)/len(ps)
     self.assertAlmostEqual(win,row['pair_win_rate'],places=6);self.assertAlmostEqual(top,row['chosen_top1_accuracy'],places=6)
    else:
     accuracy=sum(max(range(18),key=lambda i:x['probabilities'][i])==x['truth'] for x in ps)/len(ps);self.assertAlmostEqual(accuracy,row['accuracy'],places=6)
 def test_moe_rmse_recompute(self):
  r=json.loads((ROOT/'projects/moe-lab/artifacts/results.json').read_text())
  for row in r['metrics']:
   ps=[x for x in r['predictions'] if x['group']==row['group'] and x['model']==row['model']];rmse=(sum((x['truth']-x['prediction'])**2 for x in ps)/len(ps))**.5;self.assertAlmostEqual(rmse,row['rmse'],places=6)
 def test_documents(self):
  for p in P:
   for n in ['README.md','METHOD.md','MODEL_CARD.md','demo.html']:self.assertTrue((ROOT/'projects'/p/n).is_file())

@unittest.skipUnless(HAS_TORCH,'requires CPU torch')
class AlgorithmTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  sys.path.insert(0,str(ROOT/'projects'));cls.s=load('frontier_test_support',ROOT/'projects/frontier_support.py');cls.dpo=load('frontier_dpo',ROOT/'projects/dpo-lab/train.py');cls.moe=load('frontier_moe',ROOT/'projects/moe-lab/train.py');cls.spec=load('frontier_spec',ROOT/'projects/spec-decode/train.py')
 def test_causal_future_mask(self):
  import torch
  m=self.s.TinyAttention().eval();a=torch.tensor([[1,2,3,4]]);b=torch.tensor([[1,2,7,8]])
  with torch.no_grad():self.assertLess(float((m(a)[:,:2]-m(b)[:,:2]).abs().max()),1e-6)
 def test_lora_initial_identity(self):
  import torch
  base=torch.nn.Linear(4,5);l=self.s.LowRankLinear(base,2);x=torch.randn(8,4);self.assertTrue(torch.equal(l(x),base(x)))
 def test_lora_merge_parity(self):
  import torch
  base=torch.nn.Linear(4,5);l=self.s.LowRankLinear(base,2)
  with torch.no_grad():l.B.normal_()
  x=torch.randn(8,4);self.assertLess(float((l(x)-torch.nn.functional.linear(x,l.merged(),base.bias)).abs().max()),1e-5)
 def test_lora_base_gradient_frozen(self):
  import torch
  l=self.s.LowRankLinear(torch.nn.Linear(4,5),2);l(torch.randn(8,4)).sum().backward();self.assertIsNone(l.base.weight.grad);self.assertIsNotNone(l.B.grad)
 def test_dpo_reference_identity_log2(self):
  import torch
  p=torch.randn(4,18).log_softmax(-1);loss=self.dpo.dpo_loss(p,p,torch.tensor([1,2,3,4]),torch.tensor([2,3,4,5]),.1);self.assertAlmostEqual(float(loss),math.log(2),places=6)
 def test_dpo_gradient_direction(self):
  import torch
  logits=torch.zeros(1,18,requires_grad=True);lp=logits.log_softmax(-1);loss=self.dpo.dpo_loss(lp,lp.detach(),torch.tensor([1]),torch.tensor([2]),.5);loss.backward();self.assertLess(float(logits.grad[0,1]),0);self.assertGreater(float(logits.grad[0,2]),0)
 def test_moe_executes_only_routed_examples(self):
  import torch
  m=self.moe.SparseMoE();sizes=[0]*4;hooks=[]
  for i,e in enumerate(m.experts):hooks.append(e.register_forward_hook(lambda module,args,out,i=i:sizes.__setitem__(i,len(args[0]))))
  _,ids,p,lb,c=m(torch.randn(40,2));self.assertEqual(sum(sizes),40);self.assertEqual(sizes,c)
  for h in hooks:h.remove()
 def test_moe_balance_finite_grad(self):
  import torch
  m=self.moe.SparseMoE();p,ids,prob,lb,c=m(torch.randn(32,2));(p.square().mean()+.03*lb).backward();self.assertTrue(torch.isfinite(m.router.weight.grad).all())
 def test_spec_random_target_draft_exact(self):
  import torch
  torch.manual_seed(13);t=self.s.TinyAttention();d=self.s.TinyAttention(d=16)
  for k in [1,2,4]:
   g,c=self.spec.greedy(t,[1,2,3,4]);s,stats=self.spec.speculative(t,d,[1,2,3,4],k=k);self.assertEqual(g,s)
 def test_spec_identical_draft_fewer_calls(self):
  import torch
  m=self.s.TinyAttention();g,c=self.spec.greedy(m,[1,2,3,4]);s,stats=self.spec.speculative(m,m,[1,2,3,4],k=4);self.assertEqual(g,s);self.assertLess(stats['target_calls'],c)
if __name__=='__main__':unittest.main()
