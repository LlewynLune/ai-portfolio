"""Finite-schema source replay and durable, namespace-scoped memory.
No query labels accepted. Quoted source values are parsed independently of model notes.
This validates authored Setting grammar, NOT arbitrary natural-language entailment.
"""
from __future__ import annotations
import hashlib,json,re,sqlite3
from collections import Counter
from pathlib import Path

def digest(x):
 return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def setting(s):
 m=re.search(r'Setting ([a-z_]+): ([^.]+)\.',s['text'])
 if not m or m[1]!=s['key']:raise ValueError('source does not match finite Setting grammar')
 return m[2]
def current_sources(sources,namespace,key=None):
 rows=[s for s in sources if s['namespace']==namespace and (key is None or s['key']==key)]
 latest={}
 for s in rows:latest[s['key']]=max(latest.get(s['key'],-1),s['revision'])
 return [s for s in rows if s['revision']==latest[s['key']] and s['state']=='active']
def validate_note(note,sources,namespace):
 if not isinstance(note,dict) or set(note)!={'key','value','source_ids','quotes'}:return False,'note_schema'
 if not all(isinstance(note[k],str) for k in ('key','value')) or not isinstance(note['source_ids'],list) or not isinstance(note['quotes'],list):return False,'note_types'
 active={s['id']:s for s in current_sources(sources,namespace,note['key'])}
 if not note['source_ids'] or len(note['source_ids'])!=len(note['quotes']):return False,'missing_provenance'
 for sid,quote in zip(note['source_ids'],note['quotes']):
  if not isinstance(sid,str) or sid not in active:return False,'stale_revoked_or_cross_namespace'
  if not isinstance(quote,str) or quote not in active[sid]['text'] or note['value']!=setting(active[sid]):return False,'quote_or_value_mismatch'
 return True,'verified_setting_grammar'
def replay_notes(proposals,sources,namespace):
 """Replay against sources; explicit repair to exact extraction, never invented facts."""
 audit=[];notes=[]
 for n in proposals:
  ok,reason=validate_note(n,sources,namespace);audit.append({'note':n,'accepted':ok,'reason':reason})
 # Current source records, not answer labels, are authoritative. Conflicts survive separately.
 for s in current_sources(sources,namespace):
  value=setting(s);quoted=f'Setting {s["key"]}: {value}.'
  notes.append(dict(key=s['key'],value=value,source_ids=[s['id']],quotes=[quoted],namespace=namespace,revision=s['revision'],source_sha256=digest(s),state='verified'))
 return notes,audit

def retrieve(rows,question,key,budget,count_tokens):
 """BM25-lite + explicit requested slot boost. Deterministic token admission.
 Slot is part of the query contract, not an answer label. No embedding claims.
 """
 query=Counter(re.findall(r'[a-z0-9_]+',question.lower()))
 def score(r):
  text=json.dumps(r,ensure_ascii=False).lower();tokens=Counter(re.findall(r'[a-z0-9_]+',text))
  return sum(min(tokens[k],2)*v for k,v in query.items())+(20 if r.get('key')==key else 0)+(12 if key=='total_cost' and r.get('key') in ('base_cost','extra_cost') else 0)
 chosen=[];used=0
 for r in sorted(rows,key=lambda r:(-score(r),r.get('key',''),json.dumps(r,sort_keys=True))):
  cost=count_tokens(json.dumps(r,ensure_ascii=False))
  if used+cost>budget:continue
  chosen.append(r);used+=cost
 return chosen,{'selected':len(chosen),'available':len(rows),'tokens':used,'budget':budget}

def parse_answer(text):
 # A fenced JSON response is allowed but prose/braces search is not.
 t=text.strip()
 if t.startswith('```json\n') and t.endswith('```'):t=t[8:-3].strip()
 elif t.startswith('```\n') and t.endswith('```'):t=t[4:-3].strip()
 x=json.loads(t)
 if not isinstance(x,dict) or set(x)!={'status','value','citations'}:raise ValueError('answer_schema')
 if x['status'] not in ('answer','abstain','review') or (x['value'] is not None and not isinstance(x['value'],str)) or not isinstance(x['citations'],list) or not all(isinstance(s,str) for s in x['citations']):raise ValueError('answer_types')
 if len(x['citations'])!=len(set(x['citations'])):raise ValueError('duplicate_citations')
 return x

def verify_answer(answer,sources,namespace,key,visible_ids):
 """Executable finite-schema checks, separate from LLM. No expected labels."""
 relevant=current_sources(sources,namespace,key)
 if key=='total_cost':relevant=current_sources(sources,namespace,'base_cost')+current_sources(sources,namespace,'extra_cost')
 allowed={s['id']:s for s in relevant if s['id'] in visible_ids}
 cited=answer['citations'];status=answer['status']
 if any(s not in allowed for s in cited):return False,'citation_not_current_visible_or_in_scope'
 if status=='abstain':return (answer['value'] is None and not cited),'abstention_contract'
 if status=='review':
  vals={setting(s) for s in allowed.values()}
  return (answer['value'] is None and len(vals)>1 and set(cited)==set(allowed)),'conflict_contract'
 if not cited or answer['value'] is None:return False,'unsupported_answer'
 vals={setting(s) for s in allowed.values()}
 if key=='total_cost':
  bykey={s['key']:s for s in allowed.values()}
  if set(bykey)!={'base_cost','extra_cost'} or set(cited)!={s['id'] for s in bykey.values()}:return False,'incomplete_calculation_evidence'
  try:v=str(sum(int(setting(s)) for s in bykey.values()))
  except ValueError:return False,'non_integer_calculation'
  return answer['value']==v,'integer_sum_check'
 if len(vals)!=1:return False,'conflict_or_no_evidence'
 return answer['value'] in vals,'exact_setting_value_check'

class MemoryStore:
 """SQLite durability, bounded namespaces, append-only audit chain, no arbitrary SQL."""
 def __init__(self,path):
  self.db=sqlite3.connect(path);self.db.execute('PRAGMA foreign_keys=ON')
  self.db.executescript('CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY, namespace TEXT NOT NULL, payload TEXT NOT NULL, hash TEXT NOT NULL); CREATE TABLE IF NOT EXISTS notes (namespace TEXT NOT NULL, ordinal INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(namespace,ordinal)); CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY, previous TEXT NOT NULL, payload TEXT NOT NULL, hash TEXT NOT NULL);')
 def ingest(self,source):
  h=digest(source);old=self.db.execute('SELECT hash FROM sources WHERE id=?',(source['id'],)).fetchone()
  if old and old[0]!=h:raise ValueError('immutable source id changed')
  self.db.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',(source['id'],source['namespace'],json.dumps(source),h));self.db.commit()
 def sources(self,namespace):return [json.loads(r[0]) for r in self.db.execute('SELECT payload FROM sources WHERE namespace=? ORDER BY id',(namespace,))]
 def replace_notes(self,namespace,notes):
  if any(n.get('namespace')!=namespace for n in notes):raise ValueError('namespace mismatch')
  with self.db:
   self.db.execute('DELETE FROM notes WHERE namespace=?',(namespace,))
   self.db.executemany('INSERT INTO notes VALUES (?,?,?)',[(namespace,i,json.dumps(n)) for i,n in enumerate(notes)])
   self.append_audit({'event':'source_replay','namespace':namespace,'notes_hash':digest(notes)})
 def notes(self,namespace):return [json.loads(r[0]) for r in self.db.execute('SELECT payload FROM notes WHERE namespace=? ORDER BY ordinal',(namespace,))]
 def append_audit(self,event):
  previous=self.db.execute('SELECT hash FROM audit ORDER BY seq DESC LIMIT 1').fetchone();p=previous[0] if previous else '0'*64
  self.db.execute('INSERT INTO audit(previous,payload,hash) VALUES (?,?,?)',(p,json.dumps(event),digest({'previous':p,'event':event})))
 def audit_valid(self):
  p='0'*64
  for previous,payload,h in self.db.execute('SELECT previous,payload,hash FROM audit ORDER BY seq'):
   if previous!=p or h!=digest({'previous':previous,'event':json.loads(payload)}):return False
   p=h
  return True
 def close(self):self.db.close()
