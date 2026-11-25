"""Post-primary, predeclared controlled challenges and budget ablations.
Not an independent benchmark: reuse primary heldout source templates/questions.
Corrupt notes, NEVER source evidence or gold. Keep every real output.
"""
import argparse,json,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from memory_agent.core import *
from memory_agent.local_model import LocalModel
from memory_agent.evaluate import SYSTEM,score,visible_ids

def distort(kind,notes,sources,ns):
 notes=json.loads(json.dumps(notes));foreign=next(s for s in sources if s['namespace']!=ns and s['key']=='region')
 if kind=='stale':
  old=next(s for s in sources if s['namespace']==ns and s['id'].endswith('budget-old'))
  key='review_budget';new={'key':key,'value':setting(old),'source_ids':[old['id']],'quotes':[f'Setting {key}: {setting(old)}.']}
 elif kind=='cross_scope':
  key='region';new={'key':key,'value':setting(foreign),'source_ids':[foreign['id']],'quotes':[f'Setting {key}: {setting(foreign)}.']}
 elif kind=='wrong_value':
  key='queue_size';s=next(s for s in sources if s['namespace']==ns and s['id'].endswith('late-new'))
  new={'key':key,'value':'999','source_ids':[s['id']],'quotes':['Setting queue_size: 999.']}
 elif kind=='dropped_evidence':
  key='latency_budget';new=None
 else:raise ValueError('unknown distortion')
 notes=[n for n in notes if n.get('key')!=key]
 if new:notes.append(new)
 return notes,key

def main():
 p=argparse.ArgumentParser();p.add_argument('--model-path',required=True);p.add_argument('--primary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise RuntimeError('new immutable output required')
 a.output.mkdir(parents=True)
 protocol={'frozen_before_calls':True,'primary_dataset_unchanged':True,'challenge_kinds':['stale','cross_scope','wrong_value','dropped_evidence'],
  'challenge_modes':['unverified_notes','source_replay'],'budget_tokens':[160,400,800],'budget_modes':['source_rag','verified_replay'],
  'scope':'same 32 heldout queries; controlled metadata/value mutations, no arbitrary prompt attack or broad security claim; primary results never rescored'}
 (a.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 data=json.loads((ROOT/'data/memory/episodes.json').read_text());sources=data['sources'];queries=[q for q in data['queries'] if q['split']=='evaluation'];memo=json.loads((a.primary/'consolidations.json').read_text());model=LocalModel(a.model_path)
 warmup=model.call('Respond {"ok":true}.','warmup',24)
 with (a.output/'challenges.jsonl').open('w') as f:
  for ns in sorted({q['namespace'] for q in queries}):
   for kind in protocol['challenge_kinds']:
    corrupted,key=distort(kind,memo[ns]['proposals'],sources,ns);q=next(q for q in queries if q['namespace']==ns and q['key']==key)
    repaired,audit=replay_notes(corrupted,sources,ns)
    for mode in protocol['challenge_modes']:
     ctx,admission=retrieve(corrupted if mode=='unverified_notes' else repaired,q['question'],key,1600,model.count)
     req={k:q[k] for k in ('namespace','key','question')};req['evidence']=ctx;raw=model.call(SYSTEM,json.dumps(req),200)
     try:pred=parse_answer(raw['text']);error=None
     except ValueError as e:pred=None;error=str(e)
     ok,reason=verify_answer(pred,sources,ns,key,visible_ids(ctx)) if pred else (False,'invalid_json')
     final=pred if mode=='unverified_notes' or ok else {'status':'abstain','value':None,'citations':[]}
     row={'id':q['id'],'kind':kind,'mode':mode,'context':ctx,'audit':audit,'call':raw,'parsed':pred,'parse_error':error,'final':final,'verifier_pass':ok,'verifier_reason':reason,'score':score(final,q),'raw_score':score(pred,q)}
     f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno());print('challenge',ns,kind,mode,row['score']['correct'],flush=True)
 with (a.output/'budgets.jsonl').open('w') as f:
  for i,q in enumerate(queries):
   ns=q['namespace'];order=protocol['budget_tokens'] if i%2==0 else list(reversed(protocol['budget_tokens']))
   for budget in order:
    for mode in protocol['budget_modes'] if i%2==0 else list(reversed(protocol['budget_modes'])):
     rows=[s for s in sources if s['namespace']==ns] if mode=='source_rag' else memo[ns]['repaired']
     ctx,admission=retrieve(rows,q['question'],q['key'],budget,model.count);req={k:q[k] for k in ('namespace','key','question')};req['evidence']=ctx
     raw=model.call(SYSTEM,json.dumps(req),200)
     try:pred=parse_answer(raw['text']);error=None
     except ValueError as e:pred=None;error=str(e)
     ok,reason=verify_answer(pred,sources,ns,q['key'],visible_ids(ctx)) if pred else (False,'invalid_json')
     final=pred if mode=='source_rag' or ok else {'status':'abstain','value':None,'citations':[]}
     row={'id':q['id'],'family':q['family'],'mode':mode,'budget':budget,'admission':admission,'context':ctx,'call':raw,'parsed':pred,'parse_error':error,'final':final,'verifier_pass':ok,'verifier_reason':reason,'score':score(final,q),'raw_score':score(pred,q)}
     f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno());print('budget',q['id'],mode,budget,row['score']['correct'],flush=True)
 provenance={'real_local_llm':True,'model':warmup['model'],'revision':warmup['revision'],'calls':model.calls,'warmup':warmup,'primary_provenance_sha256':digest(json.loads((a.primary/'provenance.json').read_text())),'protocol_sha256':digest(protocol),'load_seconds':model.load_seconds,'paid_api_calls':0}
 (a.output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n');print('DONE challenge32 budget192',flush=True)
if __name__=='__main__':main()
