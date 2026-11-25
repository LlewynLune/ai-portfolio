"""v2 fresh real-model runs, exploratory on already examined heldout templates.
Preserve all previous outputs; do NOT claim new independent test accuracy.
"""
import argparse,json,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from memory_agent.core import replay_notes
from memory_agent.release_guard import atomic_context,parse_v2,verify_v2
from memory_agent.local_model import LocalModel
from memory_agent.evaluate import SYSTEM,visible_ids,score

def main():
 p=argparse.ArgumentParser();p.add_argument('--model-path',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise RuntimeError('new immutable output required')
 a.output.mkdir(parents=True)
 protocol={'phase':'post-primary exploratory v2','not_independent_holdout':True,'changes':['atomic key context grouping','source-wide conflict guard','explicit integer-to-string normalization'],'budgets':[160,400,1600],'frozen_before_v2_calls':True}
 (a.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 data=json.loads((ROOT/'data/memory/episodes.json').read_text());sources=data['sources'];queries=[q for q in data['queries'] if q['split']=='evaluation'];model=LocalModel(a.model_path)
 warmup=model.call('Respond {"ok":true}.','warmup',24)
 with (a.output/'runs.jsonl').open('w') as f:
  for q in queries:
   notes,_=replay_notes([],sources,q['namespace'])
   for b in protocol['budgets']:
    context,admission=atomic_context(notes,q['question'],q['key'],b,model.count);req={k:q[k] for k in ('namespace','key','question')};req['evidence']=context
    raw=model.call(SYSTEM,json.dumps(req),200)
    try:pred,normalized=parse_v2(raw['text']);error=None
    except ValueError as e:pred=None;normalized=False;error=str(e)
    ok,reason=verify_v2(pred,sources,q['namespace'],q['key'],visible_ids(context)) if pred else (False,'invalid_schema')
    final=pred if ok else {'status':'abstain','value':None,'citations':[]}
    row={'id':q['id'],'family':q['family'],'budget':b,'mode':'release_guard_v2','context':context,'admission':admission,'call':raw,'parsed':pred,'normalized_integer':normalized,'parse_error':error,'verifier_pass':ok,'verifier_reason':reason,'final':final,'score':score(final,q),'raw_score':score(pred,q)}
    f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno());print('v2',q['id'],b,row['score']['correct'],reason,flush=True)
 (a.output/'provenance.json').write_text(json.dumps({'model':warmup['model'],'revision':warmup['revision'],'calls':model.calls,'warmup':warmup,'real_local_llm':True,'paid_api_calls':0,'not_independent_holdout':True},indent=2)+'\n')
 print('DONE 96 fresh v2 calls',flush=True)
if __name__=='__main__':main()
