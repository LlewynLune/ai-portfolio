import importlib.util,json,hashlib,sys,unittest,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECTS=['vision-cal','circuit-id','channel-est','power-scope']
HAS_ML=importlib.util.find_spec('sklearn') is not None

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class FrozenEvidenceTests(unittest.TestCase):
 def test_hashes(self):
  for p in PROJECTS:
   folder=ROOT/'projects'/p/'artifacts';r=json.loads((folder/'results.json').read_text())
   self.assertEqual(r['code_sha256'],hashlib.sha256((folder.parent/'train.py').read_bytes()).hexdigest())
   self.assertEqual(r['support_sha256'],hashlib.sha256((ROOT/'projects/interdisciplinary_support.py').read_bytes()).hexdigest())
   for n,h in json.loads((folder/'checksums.json').read_text()).items():self.assertEqual(h,hashlib.sha256((folder/n).read_bytes()).hexdigest())
 def test_no_hidden_ood(self):
  for p in PROJECTS:
   r=json.loads((ROOT/'projects'/p/'artifacts/results.json').read_text());self.assertGreater(len({x['group'] for x in r['metrics']}),1);self.assertTrue(r['limits']);self.assertTrue(r['predictions'])
 def test_documents_and_demo(self):
  for p in PROJECTS:
   for n in ['README.md','METHOD.md','MODEL_CARD.md','demo.html']:self.assertTrue((ROOT/'projects'/p/n).is_file())
 def test_native_js_python_export_parity(self):
  js=(ROOT/'scripts/build_cross_demos.py').read_text();engine=re.search("ENGINE='''(.*?)'''",js,re.S)[1]
  data=[]
  for p in PROJECTS:
   folder=ROOT/'projects'/p/'artifacts';m=json.loads((folder/'model.json').read_text());r=json.loads((folder/'results.json').read_text());data.append({'project':p,'model':m,'examples':r['examples']})
  script=engine+'const cases='+json.dumps(data)+';cases.forEach(c=>c.examples.forEach(e=>{const p=modelPredict(e.input,c.model);p.forEach((v,i)=>{if(Math.abs(v-e.output[i])>1e-8)throw Error(c.project+" export mismatch");});}));'
  subprocess.run(['node','--input-type=commonjs'],input=script,text=True,capture_output=True,check=True)

@unittest.skipUnless(HAS_ML,'requires ML dependencies')
class NumericalProtocolTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  sys.path.insert(0,str(ROOT/'projects'));cls.support=load('cross_support',ROOT/'projects/interdisciplinary_support.py')
  cls.vision=load('vision_train',ROOT/'projects/vision-cal/train.py');cls.rc=load('rc_train',ROOT/'projects/circuit-id/train.py');cls.channel=load('channel_train',ROOT/'projects/channel-est/train.py');cls.power=load('power_train',ROOT/'projects/power-scope/train.py')
 def test_vision_split_disjoint(self):
  r=json.loads((ROOT/'projects/vision-cal/artifacts/results.json').read_text());a,b,c=[set(r['split'][k]) for k in ('train','validation','test')];self.assertFalse(a&b or a&c or b&c);self.assertEqual(len(a|b|c),1797)
 def test_temperature_preserves_argmax(self):
  import numpy as np
  r=json.loads((ROOT/'projects/vision-cal/artifacts/results.json').read_text());rows=r['metrics']
  for group in {x['group'] for x in rows}:
   a=next(x for x in rows if x['group']==group and x['model']=='mlp_raw');b=next(x for x in rows if x['group']==group and x['model']=='mlp_temperature');self.assertEqual(a['accuracy'],b['accuracy'])
 def test_vision_metrics_recomputed(self):
  import numpy as np
  r=json.loads((ROOT/'projects/vision-cal/artifacts/results.json').read_text())
  for row in r['metrics']:
   ps=[p for p in r['predictions'] if p['group']==row['group'] and p['model']==row['model']];m=self.vision.metrics(np.array([p['label'] for p in ps]),np.array([p['probabilities'] for p in ps]))
   for k in ['accuracy','nll','ece10']:self.assertAlmostEqual(m[k],row[k],places=10)
 def test_rc_clean_physical_identifiable_tau(self):
  import numpy as np
  for tau in [.5,1,3,5]:
   y=1-np.exp(-self.rc.TIME/tau);pred=self.rc.physical(np.array([y]))[0];self.assertAlmostEqual(pred,tau,places=4)
 def test_rc_generator_independence(self):
  import numpy as np
  a=self.rc.generate(10,10)[0];b=self.rc.generate(10,20)[0];self.assertFalse(np.array_equal(a,b));self.assertTrue(np.array_equal(a,self.rc.generate(10,10)[0]))
 def test_rc_recompute(self):
  import numpy as np
  r=json.loads((ROOT/'projects/circuit-id/artifacts/results.json').read_text())
  for row in r['metrics']:
   ps=[p for p in r['predictions'] if p['group']==row['group'] and p['seed']==row['seed'] and p['model']==row['model']];m=self.support.regression([p['truth_tau_ms'] for p in ps],[p['pred_tau_ms'] for p in ps]);self.assertAlmostEqual(m['mae'],row['mae'],places=10)
 def test_channel_clean_interpolation_pilots(self):
  import numpy as np
  x=self.channel.generate(12,55)[0];h=self.channel.interpolation(x);L=len(self.channel.PILOTS);self.assertLess(np.max(abs(h[:,self.channel.PILOTS]-(x[:,:L]+1j*x[:,L:]))),1e-12)
 def test_channel_lmmse_noise_free(self):
  import numpy as np
  F=np.exp(-2j*np.pi*np.arange(32)[:,None]*np.arange(4)[None,:]/32);h=np.array([1+1j,.2,.1j,.1]);H=F@h;z=H[self.channel.PILOTS];x=np.concatenate([z.real,z.imag])[None,:];pred=self.channel.lmmse(x,1e-9)[0];self.assertLess(np.mean(abs(pred-H)**2),1e-10)
 def test_channel_noiseless_perfect_csi_bits(self):
  import numpy as np
  _,_,H,_,s,bits,_=self.channel.generate(20,44);nm,err,n=self.channel.score(H,H,H*s,bits);self.assertEqual(int(err.sum()),0);self.assertEqual(float(nm.sum()),0)
 def test_channel_ber_recompute(self):
  r=json.loads((ROOT/'projects/channel-est/artifacts/results.json').read_text())
  for row in r['metrics']:
   ps=[p for p in r['predictions'] if p['group']==row['group'] and p['seed']==row['seed'] and p['model']==row['model']];self.assertEqual(sum(p['bit_errors'] for p in ps),row['bit_errors']);self.assertEqual(sum(p['bits'] for p in ps),row['bits']);self.assertAlmostEqual(row['ber'],row['bit_errors']/row['bits'])
 def test_power_features_are_past_only(self):
  import numpy as np
  s=self.power.generate();t,x,y=self.power.design(s);self.assertTrue(np.array_equal(x[:,0],s['facility'][t]));self.assertTrue(np.array_equal(x[:,3],s['facility'][t-288]));self.assertTrue(np.array_equal(y,s['facility'][t+1]))
  self.assertLess(int((t[(t+1)<20*288]+1).max()),20*288)
 def test_power_scaler_train_only(self):
  import numpy as np
  s=self.power.generate();t,x,y=self.power.design(s);m=json.loads((ROOT/'projects/power-scope/artifacts/model.json').read_text());self.assertLess(np.max(abs(x[t+1<20*288].mean(axis=0)-m['mean'])),1e-9)
 def test_power_recompute(self):
  r=json.loads((ROOT/'projects/power-scope/artifacts/results.json').read_text())
  for row in r['metrics']:
   ps=[p for p in r['predictions'] if p['group']==row['group'] and p['model']==row['model']];m=self.support.regression([p['actual_kw'] for p in ps],[p['forecast_kw'] for p in ps]);self.assertAlmostEqual(m['mae'],row['mae'],places=10)
if __name__=='__main__':unittest.main()
