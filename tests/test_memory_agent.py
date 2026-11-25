import unittest,sys,tempfile,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'projects/cite-rag';sys.path.insert(0,str(R))
from memory_agent.core import *
from memory_agent.evaluate import prepare_context,score
class MemoryTests(unittest.TestCase):
 def setUp(self):
  self.sources=json.loads((R/'data/memory/episodes.json').read_text())['sources']
 def test_frozen_before_inference(self):
  m=json.loads((R/'data/memory/manifest.json').read_text());self.assertEqual(hashlib.sha256((R/'data/memory/episodes.json').read_bytes()).hexdigest(),m['sha256']);self.assertTrue(m['generated_before_inference'])
 def test_latest_version_and_revocation(self):
  s=current_sources(self.sources,'iris','review_budget');self.assertEqual([r['id'] for r in s],['iris-budget-current']);self.assertFalse(current_sources(self.sources,'iris','legacy_mode'))
 def test_conflicts_survive(self):
  s=current_sources(self.sources,'iris','review_route');self.assertEqual(len({setting(r) for r in s}),2)
 def test_invalid_memory_is_audited(self):
  n={'key':'review_budget','value':'10 minutes','source_ids':['iris-budget-old'],'quotes':['Setting review_budget: 10 minutes.']}
  notes,audit=replay_notes([n],self.sources,'iris');self.assertFalse(audit[0]['accepted']);self.assertEqual([n['value'] for n in notes if n['key']=='review_budget'],['17 minutes'])
 def test_cross_namespace_note_rejected(self):
  n={'key':'region','value':'north','source_ids':['cobalt-scope'],'quotes':['Setting region: north.']};self.assertFalse(validate_note(n,self.sources,'iris')[0])
 def test_citation_existence_not_sufficient(self):
  p={'status':'answer','value':'999 minutes','citations':['iris-budget-current']};self.assertFalse(verify_answer(p,self.sources,'iris','review_budget',{'iris-budget-current'})[0])
 def test_invisible_source_cannot_support_answer(self):
  p={'status':'answer','value':'17 minutes','citations':['iris-budget-current']};self.assertFalse(verify_answer(p,self.sources,'iris','review_budget',set())[0])
 def test_units_exact(self):
  p={'status':'answer','value':'250 seconds','citations':['iris-units']};self.assertFalse(verify_answer(p,self.sources,'iris','latency_budget',{'iris-units'})[0])
 def test_integer_sum_requires_both(self):
  p={'status':'answer','value':'23','citations':['iris-base','iris-extra']};self.assertTrue(verify_answer(p,self.sources,'iris','total_cost',set(p['citations']))[0]);p['citations']=['iris-base'];self.assertFalse(verify_answer(p,self.sources,'iris','total_cost',{'iris-base','iris-extra'})[0])
 def test_json_schema(self):
  self.assertEqual(parse_answer('{"status":"abstain","value":null,"citations":[]}')['status'],'abstain')
  for s in ['prefix {"status":"answer"}', '{"status":"answer","value":"v","citations":["a","a"]}', '{"status":"answer","value":"v","citations":[],"bonus":1}']:
   with self.assertRaises(ValueError):parse_answer(s)
 def test_durable_idempotent_sources_and_audit(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'memory.db';s=MemoryStore(path);src=self.sources[0];s.ingest(src);s.ingest(src);notes,_=replay_notes([],self.sources,'iris');s.replace_notes('iris',notes);self.assertTrue(s.audit_valid());s.close();s=MemoryStore(path);self.assertEqual(s.notes('iris'),notes);self.assertEqual(len(s.sources('iris')),1)
   with self.assertRaises(ValueError):s.ingest(dict(src,text='changed'))
   s.db.execute('UPDATE audit SET payload=?',(json.dumps({'corrupt':True}),));self.assertFalse(s.audit_valid());s.close()
 def test_gold_never_used_for_context(self):
  q={'namespace':'iris','key':'region','question':'What is region?','expected_value':'SECRET_LABEL'}
  notes,_=replay_notes([],self.sources,'iris')
  a,_=prepare_context('verified_replay',self.sources,[],notes,q,len);q['expected_value']='DIFFERENT';b,_=prepare_context('verified_replay',self.sources,[],notes,q,len);self.assertEqual(a,b);self.assertNotIn('SECRET_LABEL',json.dumps(a))
 def test_token_budget_never_exceeded(self):
  rows,_=replay_notes([],self.sources,'iris');r,m=retrieve(rows,'review_budget','review_budget',300,len);self.assertLessEqual(m['tokens'],300)
 def test_v2_source_wide_conflict(self):
  from memory_agent.release_guard import verify_v2
  p={'status':'answer','value':'route_alpha','citations':['iris-route-a']}
  self.assertFalse(verify_v2(p,self.sources,'iris','review_route',{'iris-route-a'})[0])
 def test_v2_integer_adapter(self):
  from memory_agent.release_guard import parse_v2
  x,adapted=parse_v2('{"status":"answer","value":23,"citations":["iris-base","iris-extra"]}');self.assertEqual(x['value'],'23');self.assertTrue(adapted)
  with self.assertRaises(ValueError):parse_v2('{"status":"answer","value":true,"citations":[]}')
 def test_v2_atomic_groups(self):
  from memory_agent.release_guard import atomic_context
  notes,_=replay_notes([],self.sources,'iris');r,m=atomic_context(notes,'review_route','review_route',350,len)
  self.assertNotEqual(sum(n['key']=='review_route' for n in r),1);self.assertLessEqual(m['tokens'],350)
 def test_frozen_real_generation_count(self):
  a=R/'artifacts/memory';s=json.loads((a/'summary.json').read_text());self.assertEqual(s['total_actual_llm_calls'],521)
  expected={'run-primary/runs.jsonl':192,'run-challenges/challenges.jsonl':32,'run-challenges/budgets.jsonl':192,'run-v2/runs.jsonl':96}
  for path,n in expected.items():
   rows=[json.loads(line) for line in (a/path).read_text().splitlines()];self.assertEqual(len(rows),n)
   for row in rows:self.assertTrue(row['call']['llm_used']);self.assertEqual(hashlib.sha256(row['call']['text'].encode()).hexdigest(),row['call']['raw_output_sha256'])
 def test_v2_keeps_failures_and_no_conflict_answers(self):
  rows=[json.loads(line) for line in (R/'artifacts/memory/run-v2/runs.jsonl').read_text().splitlines()]
  self.assertEqual(sum(not r['score']['correct'] for r in rows),8)
  self.assertEqual(sum(r['score']['wrong_answer'] for r in rows),0)
  for r in rows:
   if r['family']=='conflict':self.assertNotEqual(r['final']['status'],'answer')
 def test_evidence_viewer_matches_actual_rows(self):
  import re
  text=(R/'memory-demo.html').read_text();embedded=json.loads(re.search(r'const DATA=(.*?);\n const',text,re.S)[1]);self.assertEqual(len(embedded['rows']),512)
  self.assertEqual(embedded['sources'],self.sources);self.assertIn('非在线模型聊天',text)
 def test_wrong_answer_not_hidden(self):
  q={'expected_status':'answer','expected_value':'a','expected_sources':['s']};self.assertTrue(score({'status':'answer','value':'bad','citations':['s']},q)['wrong_answer'])
if __name__=='__main__':unittest.main()
