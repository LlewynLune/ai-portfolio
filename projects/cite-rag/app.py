"""Citation-first local QA: BM25/character retrieval/RRF + optional real LLM adapter."""
from pathlib import Path
import sys,json,math,re,hashlib
from collections import Counter
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'reliability-lab'))
from reliability_lab.retrieval import DOCUMENTS,QUESTIONS
DOCS=DOCUMENTS+[
 {'id':'api-budget','text':'Limit remote API calls and output tokens before execution. Monetary cost requires provider prices and measured usage. Credentials must remain outside browser code and Git.'},
 {'id':'split','text':'Fit vocabulary and model weights on training data. Use validation to select thresholds, not the final test set. Deduplicate records before splitting.'},
 {'id':'fusion','text':'Reciprocal rank fusion combines retrieval rankings. Character n-grams tolerate spelling variations but do not implement neural semantic embeddings.'},
]
QUERIES=[{'q':r['query'],'relevant':r['relevant'],'split':r['split']} for r in QUESTIONS]+[
 {'q':'api calls output tokens monetary cost credentials','relevant':['api-budget'],'split':'evaluation'},
 {'q':'training vocabulary validation thresholds deduplicate','relevant':['split'],'split':'evaluation'},
 {'q':'reciprocal rank fusion characters embeddings','relevant':['fusion'],'split':'evaluation'},
 {'q':'what is today weather in Paris','relevant':[],'split':'unanswerable'},
 {'q':'give me company private reimbursement standard','relevant':[],'split':'unanswerable'}]

def words(t):return re.findall('[a-z0-9]+',t.lower())
def grams(t):
 t=' '.join(words(t));return Counter(t[i:i+3] for i in range(max(0,len(t)-2)))
def rank(q,method='hybrid'):
 dfs=[Counter(words(d['text'])) for d in DOCS];avg=sum(sum(f.values()) for f in dfs)/len(dfs);cq=grams(q);lex=[];chars=[]
 for d,f in zip(DOCS,dfs):
  s=0.
  for t in set(words(q)):
   df=sum(t in x for x in dfs);tf=f[t]
   s+=math.log(1+(len(dfs)-df+.5)/(df+.5))*tf*2.2/(tf+1.2*(.25+.75*sum(f.values())/avg)) if tf else 0
  cd=grams(d['text']);norm=(sum(x*x for x in cq.values())*sum(x*x for x in cd.values()))**.5
  c=sum(v*cd[k] for k,v in cq.items())/norm if norm else 0
  lex.append((d['id'],s));chars.append((d['id'],c))
 l=sorted(lex,key=lambda x:(-x[1],x[0]));c=sorted(chars,key=lambda x:(-x[1],x[0]))
 if method=='bm25':scores=dict(l)
 elif method=='char':scores=dict(c)
 elif method=='hybrid':
  scores={d['id']:0 for d in DOCS}
  for ranking in (l,c):
   for i,(id,s) in enumerate(ranking):scores[id]+=1/(61+i) if s>0 else 0
 else:raise ValueError('unknown method')
 return sorted([dict(d,score=scores[d['id']],lexical=dict(l)[d['id']],char=dict(c)[d['id']]) for d in DOCS],key=lambda d:(-d['score'],d['id']))
def answer(q,method='hybrid'):
 if not isinstance(q,str) or not q.strip() or len(q)>2000:raise ValueError('query required max 2000 characters')
 hits=rank(q,method)[:3];supported=max(h['lexical'] for h in hits)>=1.5 or max(h['char'] for h in hits)>=.35
 return {'status':'extractive' if supported else 'abstained','answer':hits[0]['text'] if supported else 'Insufficient evidence in this knowledge pack.', 'citations':[hits[0]['id']] if supported else [],'hits':hits,'llm_used':False}
def main():
 out=ROOT/'artifacts';out.mkdir(exist_ok=True);metrics=[]
 for method in ['bm25','char','hybrid']:
  for split in ['development','evaluation','challenge','unanswerable']:
   cases=[]
   for q in QUERIES:
    if q['split']!=split:continue
    r=answer(q['q'],method);top=[h['id'] for h in r['hits']];rel=set(q['relevant'])
    cases.append(dict(q,**r,recall3=len(set(top)&rel)/len(rel) if rel else None,mrr3=next((1/(i+1) for i,t in enumerate(top) if t in rel),0) if rel else None,refusal_correct=r['status']=='abstained' if not rel else None))
   average=lambda key:sum(r[key] for r in cases)/len(cases) if cases and cases[0][key] is not None else None
   metrics.append({'method':method,'split':split,'count':len(cases),'recall3':average('recall3'),'mrr3':average('mrr3'),'refusal_accuracy':average('refusal_correct'),'cases':cases})
 report={'project':'CiteRAG','status':'local_extractive_evaluated_llm_not_run','documents':DOCS,'queries':QUERIES,'metrics':metrics,
 'corpus_sha256':hashlib.sha256(json.dumps(DOCS,sort_keys=True).encode()).hexdigest(),'shared_fixture':'FlowBench authored corpus plus 3 new snippets; shared corpus is disclosed, not independent public benchmark',
 'examples':[{'q':q['q'],**answer(q['q'])} for q in QUERIES], 'limits':['15 authored English snippets and 25 questions; author selection bias','character cosine is lexical, not embeddings','RRF not calibrated probability','local output is excerpt, not LLM generation','citation ID validity alone does not prove support','remote API not called']}
 (out/'results.json').write_text(json.dumps(report,indent=2));(out/'checksums.json').write_text(json.dumps({'results.json':hashlib.sha256((out/'results.json').read_bytes()).hexdigest()},indent=2))
 lines=['# CiteRAG 本地检索评测','',f'{len(DOCS)} 篇自建文档、{len(QUERIES)} 个问题；共享 FlowBench 样本来源明确披露。大模型未调用。','', '|方法|集合|问题|Recall@3|MRR@3|拒答正确率|','|---|---|---:|---:|---:|---:|']
 fmt=lambda v:'—' if v is None else f'{v:.3f}'
 for m in metrics:lines.append(f"|{m['method']}|{m['split']}|{m['count']}|{fmt(m['recall3'])}|{fmt(m['mrr3'])}|{fmt(m['refusal_accuracy'])}|")
 lines+=['','固定拒答门槛是启发式，会失败；所有病例逐条保留，引用有效不等于答案语义正确。','[全部结果](results.json) · [完整性](checksums.json)'];(out/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps([{k:v for k,v in m.items() if k!='cases'} for m in metrics],indent=2))
if __name__=='__main__':main()
