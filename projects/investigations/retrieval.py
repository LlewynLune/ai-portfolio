"""New source IDs/namespaces and question wording; real offline model generation.
Still finite Setting grammar, not natural-language semantic entailment.
"""
from .common import *

def cite(model_path):
 folder='cite-rag';p=PROJECTS/folder;sys.path.insert(0,str(p))
 from memory_agent.local_model import LocalModel
 from memory_agent.core import replay_notes,retrieve,parse_answer,verify_answer
 from memory_agent.release_guard import parse_v2,verify_v2,atomic_context
 from memory_agent.evaluate import SYSTEM,score,visible_ids
 protocol={'kind':'fresh_namespace_transfer_after_v2','namespaces':8,'queries_per_namespace':6,'modes':['source_rag','release_v2'],'budget':800,'source_order':'current revision first, older event arrives last','new_source_ids':True,'grammar':'same explicit Setting grammar, not independent natural-language validation','not_tuning_after_results':True};freeze(folder,protocol)
 sources=[];queries=[]
 for i in range(8):
  ns=f'newteam_{i}';n=31+7*i
  defs=[('cur','window',3,f'{n} minutes','active'),('old','window',1,f'{n-9} minutes','active'),('gone','policy',2,'enabled','revoked'),('left','channel',4,'green','active'),('right','channel',4,'orange','active'),('base','base_cost',1,str(n),'active'),('extra','extra_cost',1,str(n+4),'active'),('region','region',1,f'zone_{i}','active')]
  for suffix,key,rev,val,state in defs:sources.append({'id':ns+'-'+suffix,'namespace':ns,'key':key,'revision':rev,'event':1 if suffix=='old' else 3,'state':state,'text':f'Fictional independent team log. Setting {key}: {val}. The setting belongs only to {ns}. Status {state}. Revision {rev}.'})
  specs=[('window','An older note arrived last. Which window is authoritative now?','answer',f'{n} minutes',[ns+'-cur']),('policy','May I use policy when the only policy record has been revoked?','abstain',None,[]),('channel','Two current entries disagree about channel. Do we have one defensible setting?','review',None,[ns+'-left',ns+'-right']),('total_cost','Please compute total_cost using base_cost and extra_cost, attach both references.','answer',str(2*n+4),[ns+'-base',ns+'-extra']),('region','Return region for this team; do not borrow a region from a different team.','answer',f'zone_{i}',[ns+'-region']),('quota','No provided entry states quota. What can we establish?','abstain',None,[])]
  for key,q,status,val,ids in specs:queries.append({'id':ns+'-'+key,'namespace':ns,'key':key,'question':q,'expected_status':status,'expected_value':val,'expected_sources':ids})
 out=p/'artifacts/investigation';(out/'dataset.json').write_text(json.dumps({'sources':sources,'queries':queries},ensure_ascii=False,indent=2)+'\n')
 model=LocalModel(model_path);warm=model.call('Respond {"ok":true}.','warmup',24);rows=[];metrics=[]
 with (out/'live-runs.jsonl').open('w') as log:
  for q in queries:
   notes,_=replay_notes([],sources,q['namespace'])
   for mode in protocol['modes']:
    if mode=='source_rag':context,admission=retrieve([s for s in sources if s['namespace']==q['namespace']],q['question'],q['key'],800,model.count)
    else:context,admission=atomic_context(notes,q['question'],q['key'],800,model.count)
    req={k:q[k] for k in ('namespace','key','question')};req['evidence']=context;call=model.call(SYSTEM,json.dumps(req),200)
    try:pred= parse_answer(call['text']) if mode=='source_rag' else parse_v2(call['text'])[0];error=None
    except ValueError as e:pred=None;error=str(e)
    ok,reason=(verify_answer if mode=='source_rag' else verify_v2)(pred,sources,q['namespace'],q['key'],visible_ids(context)) if pred else (False,'invalid_schema')
    final=pred if mode=='source_rag' or ok else {'status':'abstain','value':None,'citations':[]}
    row={'id':q['id'],'key':q['key'],'mode':mode,'context':context,'admission':admission,'call':call,'parsed':pred,'parse_error':error,'verifier_pass':ok,'reason':reason,'final':final,'score':score(final,q)};rows.append(row);log.write(json.dumps(row)+'\n');log.flush();print('fresh cite',q['id'],mode,row['score']['correct'],flush=True)
 for mode in protocol['modes']:
  rr=[r for r in rows if r['mode']==mode];metrics.append({'mode':mode,'n':len(rr),'correct':sum(r['score']['correct'] for r in rr),'parse_failures':sum(r['parsed'] is None for r in rr),'wrong_answers':sum(r['score']['wrong_answer'] for r in rr),'mean_prompt_tokens':float(np.mean([r['call']['prompt_tokens'] for r in rr]))})
 return save(folder,'CiteRAG · 新namespace与乱序修订迁移','在此前未出现的源ID、团队与措辞上，v2来源校验仍能处理修订、冲突和计算吗？',rows,metrics,['数据在首次本批推断前写入dataset.json；48新问题实例/8namespace不与原48题重合。','仍使用同一已知Setting语法；语言模板变化与新ID不是通用语义泛化。','source_rag保留v1严格字符串契约，release含整数适配与guard；差异为整系统而非单组件收益。'],protocol,details={'warmup':warm,'actual_calls':model.calls,'model_revision':warm['revision']},files=[Path(__file__),p/'memory_agent/release_guard.py',p/'memory_agent/core.py',p/'memory_agent/local_model.py'])
