"""User-facing finite settings query. Local model required; never simulated fallback.
Supports only frozen fictional namespaces/keys. Source replay + strict output guard.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from memory_agent.core import *
from memory_agent.local_model import LocalModel
from memory_agent.evaluate import SYSTEM,visible_ids
from memory_agent.release_guard import parse_v2,verify_v2,atomic_context

def deterministic_reference(sources,namespace,key):
 """Strong finite-schema no-LLM baseline. MUST report alongside LLM approaches."""
 rows=current_sources(sources,namespace,key)
 if key=='total_cost':
  a=current_sources(sources,namespace,'base_cost');b=current_sources(sources,namespace,'extra_cost')
  if len(a)==len(b)==1:
   return {'status':'answer','value':str(int(setting(a[0]))+int(setting(b[0]))),'citations':[a[0]['id'],b[0]['id']]}
 vals={setting(s) for s in rows}
 if not rows:return {'status':'abstain','value':None,'citations':[]}
 if len(vals)>1:return {'status':'review','value':None,'citations':[s['id'] for s in rows]}
 return {'status':'answer','value':next(iter(vals)),'citations':[s['id'] for s in rows]}

def main():
 p=argparse.ArgumentParser();p.add_argument('--model-path',required=True);p.add_argument('--namespace',required=True);p.add_argument('--key',required=True);p.add_argument('--question',required=True);p.add_argument('--budget',type=int,default=1600);a=p.parse_args()
 data=json.loads((ROOT/'data/memory/episodes.json').read_text());sources=data['sources']
 if a.namespace not in {s['namespace'] for s in sources}:p.error('unknown fictional namespace')
 if not 160<=a.budget<=1600:p.error('budget 160..1600 required')
 if len(a.question)>2000:p.error('question at most 2000 characters')
 model=LocalModel(a.model_path);notes,audit=replay_notes([],sources,a.namespace);ctx,admission=atomic_context(notes,a.question,a.key,a.budget,model.count)
 call=model.call(SYSTEM,json.dumps({'namespace':a.namespace,'key':a.key,'question':a.question,'evidence':ctx}),200)
 try:parsed,normalized=parse_v2(call['text'])
 except ValueError:parsed=None;normalized=False
 checked,reason=verify_v2(parsed,sources,a.namespace,a.key,visible_ids(ctx)) if parsed else (False,'invalid_schema')
 final=parsed if checked else {'status':'abstain','value':None,'citations':[]}
 print(json.dumps({'raw_model':call,'parsed':parsed,'verifier_pass':checked,'reason':reason,'intervened':not checked,'final':final,'admission':admission,'evidence':ctx,'boundary':'source replay checks finite Setting grammar, not arbitrary semantic entailment'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
