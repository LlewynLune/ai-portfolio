"""Exploratory v2 after primary budget failures. No retrospective rescore.
Adds whole-source conflict check, atomic context groups and explicit integer adapter.
Finite integers become decimal strings; booleans/floats remain invalid.
"""
import json
from .core import current_sources,setting,retrieve,verify_answer,parse_answer

def parse_v2(text):
 t=text.strip()
 if t.startswith('```json\n') and t.endswith('```'):t=t[8:-3].strip()
 x=json.loads(t)
 normalized=False
 if isinstance(x,dict) and type(x.get('value')) is int:
  if abs(x['value'])>10**12:raise ValueError('integer_out_of_bound')
  x['value']=str(x['value']);normalized=True
 return parse_answer(json.dumps(x)),normalized

def verify_v2(answer,sources,namespace,key,visible_ids):
 # Check source-wide conflict BEFORE restricting to selected evidence.
 relevant=current_sources(sources,namespace,key)
 if key=='total_cost':relevant=current_sources(sources,namespace,'base_cost')+current_sources(sources,namespace,'extra_cost')
 if key!='total_cost' and len({setting(s) for s in relevant})>1:
  if answer['status']=='answer':return False,'source_wide_conflict'
  if answer['status']=='review' and not {s['id'] for s in relevant}<=visible_ids:return False,'conflict_evidence_incomplete'
 return verify_answer(answer,sources,namespace,key,visible_ids)

def atomic_context(notes,question,key,budget,count):
 """Admit complete key groups or nothing. No selective loss of conflicting notes."""
 ranking,_=retrieve(notes,question,key,100000,count);groups={}
 for r in ranking:groups.setdefault(r['key'],[]).append(r)
 selected=[];used=0;dropped=[]
 # Total-cost sources also form a joint atomic group.
 if key=='total_cost':
  calc=groups.pop('base_cost',[])+groups.pop('extra_cost',[])
  groups={'total_cost':calc,**groups}
 for group,rows in groups.items():
  cost=sum(count(json.dumps(r,ensure_ascii=False)) for r in rows)
  if used+cost<=budget:selected+=rows;used+=cost
  else:dropped.append(group)
 return selected,{'tokens':used,'budget':budget,'selected':len(selected),'available':len(notes),'atomic_groups_dropped':dropped}
