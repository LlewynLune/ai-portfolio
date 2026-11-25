"""Verify published experiment aggregates against immutable raw traces.
No model required. Use after artifacts are generated and before packaging.
"""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from memory_agent.evaluate import score

def main():
 a=ROOT/'artifacts/memory';data=json.loads((ROOT/'data/memory/episodes.json').read_text());gold={q['id']:q for q in data['queries']};s=json.loads((a/'summary.json').read_text())
 specs={'run-primary/runs.jsonl':192,'run-challenges/challenges.jsonl':32,'run-challenges/budgets.jsonl':192,'run-v2/runs.jsonl':96};count=0
 for path,n in specs.items():
  rows=[json.loads(line) for line in (a/path).read_text().splitlines()];assert len(rows)==n,path
  for r in rows:
   assert r['score']==score(r['final'],gold[r['id']]),(path,r['id'],'final score')
   assert r['raw_score']==score(r['parsed'],gold[r['id']]),(path,r['id'],'raw score')
   c=r['call'];assert c['llm_used'];assert hashlib.sha256(c['text'].encode()).hexdigest()==c['raw_output_sha256']
   assert c['prompt_tokens']<=8192 and c['completion_tokens']<=c['max_tokens']
  count+=len(rows)
 assert count==512 and s['total_actual_llm_calls']==521
 assert s['deterministic_reference']['correct']==32
 manifest=json.loads((ROOT/'data/memory/manifest.json').read_text());assert hashlib.sha256((ROOT/'data/memory/episodes.json').read_bytes()).hexdigest()==manifest['sha256']
 checks={str(p.relative_to(a)):hashlib.sha256(p.read_bytes()).hexdigest() for p in a.rglob('*') if p.is_file() and 'private' not in p.parts and p.name!='checksums.json'}
 (a/'checksums.json').write_text(json.dumps(checks,indent=2)+'\n')
 print('PASS frozen data, 512 real output hashes, score recomputation, token caps, 521 total model calls;',len(checks),'artifact hashes')
if __name__=='__main__':main()
