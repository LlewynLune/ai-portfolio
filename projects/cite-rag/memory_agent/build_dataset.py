"""Freeze authored synthetic episodes BEFORE inference. No company material.
Finite setting grammar provides executable checks, not general semantic entailment.
"""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def build():
 sources=[];queries=[]
 for i,name in enumerate(['Iris','Cobalt','Maple','Quartz','Linden','Saffron']):
  ns=name.lower();split='development' if i<2 else 'evaluation';t=10+i*3
  def source(suffix,key,version,value,state='active',day=1):
   sid=ns+'-'+suffix
   # Values exist only in source text; metadata never stores ground-truth values.
   text=f'{name} simulation note {suffix}. Setting {key}: {value}. Status: {state}. Revision {version}. This is a fictional software review exercise, not a physical engineering standard.'
   sources.append(dict(id=sid,namespace=ns,key=key,revision=version,event=day,state=state,text=text))
   return sid
  old=source('budget-old','review_budget',1,f'{t} minutes',day=1)
  new=source('budget-current','review_budget',2,f'{t+7} minutes',day=3)
  a=source('route-a','review_route',3,'route_alpha',day=4)
  b=source('route-b','review_route',3,'route_beta',day=4)
  retired=source('retired','legacy_mode',2,'enabled',state='revoked',day=4)
  loc=source('scope','region',1,['west','north','east','south','central','island'][i],day=1)
  late=source('late-old','queue_size',1,str(t),day=1)
  correction=source('late-new','queue_size',2,str(t+2),day=5)
  unit=source('units','latency_budget',1,f'{t*25} milliseconds',day=2)
  base=source('base','base_cost',1,str(t),day=2)
  extra=source('extra','extra_cost',1,str(t+3),day=2)
  source('noise','newsletter',1,'welcome',day=1)
  source('noise2','meeting',1,'rescheduled',day=4)
  tests=[
   ('revision', 'review_budget', 'What is the current review_budget setting?', 'answer',f'{t+7} minutes',[new]),
   ('conflict','review_route','What is review_route? Do not silently choose one of conflicting active revisions.','review',None,[a,b]),
   ('revocation','legacy_mode','What is legacy_mode now? Revoked evidence cannot authorize a setting.','abstain',None,[]),
   ('namespace','region','What is the region setting for this namespace only?','answer',['west','north','east','south','central','island'][i],[loc]),
   ('correction','queue_size','What is the most recent corrected queue_size?','answer',str(t+2),[correction]),
   ('missing','approval_limit','What is approval_limit? No supplied note states it.','abstain',None,[]),
   ('units','latency_budget','What is latency_budget? Preserve the exact unit; do not substitute seconds.','answer',f'{t*25} milliseconds',[unit]),
   ('multi_source','total_cost','What is total_cost, the integer sum of base_cost and extra_cost? Cite both sources.','answer',str(2*t+3),[base,extra])]
  for family,key,q,status,value,cites in tests:
   queries.append(dict(id=ns+'-'+family,namespace=ns,key=key,question=q,split=split,family=family,expected_status=status,expected_value=value,expected_sources=cites))
 dataset={'schema_version':1,'authored':True,'data_origin':'self-authored synthetic software review notes; no company documents, customer data or real engineering rules',
  'split_protocol':'Namespaces Iris/Cobalt are development; Maple/Quartz/Linden/Saffron are held out. Freeze before inference; no tuning on held-out results. Templates shared across splits: limited structural generalization only.',
  'sources':sources,'queries':queries}
 text=json.dumps(dataset,ensure_ascii=False,indent=2)+'\n'
 dest=ROOT/'data/memory/episodes.json'
 if dest.exists():raise RuntimeError('frozen dataset exists; do not overwrite')
 dest.write_text(text)
 manifest={'sha256':hashlib.sha256(text.encode()).hexdigest(),'queries':len(queries),'sources':len(sources),'development':16,'evaluation':32,'generated_before_inference':True}
 (ROOT/'data/memory/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(manifest)
if __name__=='__main__':build()
