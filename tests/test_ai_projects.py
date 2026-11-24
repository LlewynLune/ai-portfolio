import importlib.util,json,math,sys,hashlib,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HAS_ML=importlib.util.find_spec('sklearn') is not None

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

@unittest.skipUnless(HAS_ML,'Run ML tests with requirements-ml.txt installed')
class ModelTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.text=load('textguard_train',ROOT/'projects/textguard/train.py')
  cls.novelty=load('novelty_train',ROOT/'projects/novelty-lab/train.py')
 def test_text_split_is_disjoint(self):
  r=json.loads((ROOT/'projects/textguard/artifacts/results.json').read_text());s=r['split'];a,b,c=[{x['id'] for x in s[k]} for k in ('train','validation','test')]
  self.assertFalse(a&b or a&c or b&c);self.assertEqual(len(a)+len(b)+len(c),r['deduplicated_rows']);self.assertLess(r['export_parity_max_error'],1e-10)
 def test_text_unseen_and_chinese_review(self):
  m=json.loads((ROOT/'projects/textguard/artifacts/model.json').read_text())
  for t in ('你好明天开会','zxvcxz zxvbnm'):self.assertTrue(self.text.infer(t,m)['review'])
 def test_text_metrics_recomputed(self):
  r=json.loads((ROOT/'projects/textguard/artifacts/results.json').read_text())
  for m in r['test_results']:
   rows=[p for p in r['predictions'] if p['model']==m['model']];actual=self.text.metric([p['label'] for p in rows],[p['probability'] for p in rows],m['threshold'])
   self.assertEqual(actual['confusion_matrix'],m['test']['confusion_matrix'])
 def test_novelty_split(self):
  r=json.loads((ROOT/'projects/novelty-lab/artifacts/results.json').read_text());a,b,c=[set(r['split'][k]) for k in ('train','validation','test')];self.assertFalse(a&b or a&c or b&c)
 def test_novelty_export_parity(self):
  m=json.loads((ROOT/'projects/novelty-lab/artifacts/model.json').read_text());r=json.loads((ROOT/'projects/novelty-lab/artifacts/results.json').read_text())
  for e in r['examples']:self.assertAlmostEqual(self.novelty.infer(e['values'],m)['score'],e['score'],places=10)
 def test_novelty_invalid(self):
  m=json.loads((ROOT/'projects/novelty-lab/artifacts/model.json').read_text())
  for values in ([1,2],[float('nan')]*13):
   with self.assertRaises(ValueError):self.novelty.infer(values,m)

class RagTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  sys.path.insert(0,str(ROOT/'projects/cite-rag'))
  cls.app=load('citerag_app',ROOT/'projects/cite-rag/app.py')
  cls.adapter=load('rag_adapter',ROOT/'projects/cite-rag/llm_adapter.py')
 def test_invalid_query(self):
  for q in ('',' '*4,5):
   with self.assertRaises(ValueError):self.app.answer(q)
 def test_rank_is_deterministic(self):self.assertEqual(self.app.rank('retry transient failure'),self.app.rank('retry transient failure'))
 def test_actual_citation(self):
  r=self.app.answer('retry transient bounded attempts');self.assertTrue(r['citations']);self.assertFalse(r['llm_used'])
 def test_no_secret_config(self):
  with self.assertRaises(ValueError):self.adapter.LLMClient('http://example.org','x','key')
 def test_mock_is_only_contract_test(self):
  client=self.adapter.LLMClient('https://example.org/v1','contract-test-model','test-value',max_calls=1)
  def transport(req):
   # No network; fake response validates API contract only, not generation performance.
   return {'choices':[{'message':{'content':json.dumps({'answer':'bounded retries','citations':['retry'],'abstained':False})}}],'usage':{'total_tokens':20}}
  r=client.generate('retry transient bounded attempts',transport=transport);self.assertEqual(r['usage']['total_tokens'],20)
  with self.assertRaises(RuntimeError):client.generate('retry transient bounded attempts',transport=transport)
 def test_redirect_cannot_forward_key(self):
  handler=self.adapter.NoRedirect()
  with self.assertRaises(RuntimeError):handler.redirect_request(None,None,302,'found',{},'https://other.example')
 def test_endpoint_rejects_secret_query(self):
  for url in ('https://example.org/v1?api_key=test','https://user:test@example.org/v1','https://example.org/v1#key'):
   with self.assertRaises(ValueError):self.adapter.LLMClient(url,'contract-test-model','test-value')
 def test_fabricated_citation_rejected(self):
  c=self.adapter.LLMClient('https://example.org/v1','contract-test-model','test-value')
  with self.assertRaises(ValueError):c.generate('retry transient bounded attempts',transport=lambda req:{'choices':[{'message':{'content':json.dumps({'answer':'bad','citations':['not-in-evidence'],'abstained':False})}}]})

class ArtifactTests(unittest.TestCase):
 def test_project_checksums(self):
  for project in ['textguard','novelty-lab','cite-rag']:
   folder=ROOT/'projects'/project/'artifacts'
   for name,digest in json.loads((folder/'checksums.json').read_text()).items():self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),digest)
 def test_no_raw_sms_artifact(self):
  folder=ROOT/'projects/textguard/artifacts'
  self.assertFalse((folder/'SMSSpamCollection').exists())
  m=json.loads((folder/'model.json').read_text());self.assertTrue(all(not any(c.isdigit() for c in token) for token in m['vocabulary']))
if __name__=='__main__':unittest.main()
