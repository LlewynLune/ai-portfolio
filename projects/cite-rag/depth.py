"""Depth: duplicate-resistant rank fusion and factual evidence export. No LLM."""
from pathlib import Path
import sys,importlib.util,math,re,hashlib
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('citerag_base',HERE/'app.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
def search(query,documents,deduplicate=True):
    if not isinstance(query,str) or not query.strip() or len(query)>2000:raise ValueError('query required')
    docs=[];seen=set()
    for d in documents:
        fingerprint=hashlib.sha256(' '.join(base.words(d['text'])).encode()).hexdigest()
        if deduplicate and fingerprint in seen:continue
        seen.add(fingerprint);docs.append(dict(d,fingerprint=fingerprint))
    if not docs:return []
    fs=[Counter(base.words(d['text'])) for d in docs];avg=sum(sum(f.values()) for f in fs)/len(fs);lex=[];ch=[];qg=base.grams(query)
    for d,f in zip(docs,fs):
        score=0
        for t in set(base.words(query)):
            tf=f[t];df=sum(t in z for z in fs)
            if tf:score+=math.log(1+(len(docs)-df+.5)/(df+.5))*tf*2.2/(tf+1.2*(.25+.75*sum(f.values())/avg))
        dg=base.grams(d['text']);norm=np.sqrt(sum(v*v for v in qg.values())*sum(v*v for v in dg.values()));cos=sum(v*dg[k] for k,v in qg.items())/norm if norm else 0;lex.append((d['id'],score));ch.append((d['id'],cos))
    score={d['id']:0. for d in docs}
    for r in [lex,ch]:
        for i,(id,v) in enumerate(sorted(r,key=lambda v:(-v[1],v[0]))):
            if v>0:score[id]+=1/(61+i)
    return [dict(d,score=score[d['id']],lexical=dict(lex)[d['id']],character=dict(ch)[d['id']]) for d in sorted(docs,key=lambda d:(-score[d['id']],d['id']))]
def main():
    clean=base.DOCS;duplicate=clean+[dict(d,id=d['id']+'-duplicate'+str(i)) for d in clean[:4] for i in range(5)];distractor=clean+[{'id':'irrelevant-'+str(i),'text':'unrelated botany chemistry music tourism.'} for i in range(20)]
    rows=[]
    for cond,docs in [('clean',clean),('duplicate_flood',duplicate),('irrelevant_flood',distractor)]:
        for dedup in [False,True]:
            for i,q in enumerate(base.QUERIES):
                hits=search(q['q'],docs,dedup);top=hits[:3];supported=bool(top) and (max(x['lexical'] for x in top)>=1.5 or max(x['character'] for x in top)>=.35);rel=set(q['relevant']);correct=any(h['id'].split('-duplicate')[0] in rel for h in top) if rel else not supported
                rows.append(dict(model='dedup_rrf' if dedup else 'raw_rrf',condition=cond,index=i,truth=int(bool(rel)),prediction=int(supported),confidence=float(min(1,top[0]['score']*30)) if top else 0,correct=bool(correct),loss=0.,metric_definition='answerable: relevant in top3; unanswerable: abstention',query=q['q'],top_ids=[x['id'] for x in top],evidence=[dict(id=x['id'],excerpt=x['text'],sha256=x['fingerprint']) for x in top]))
    save(HERE,'CiteRAG deduplication & evidence stress','25 authored queries × clean/duplicate/irrelevant corpora × raw/dedup RRF. Explicit supported/abstained state and content hashes. Correctness is top3 retrieval or refusal, not answer semantics.',rows,['Content fingerprint deduplication prevents exact duplicate results occupying all top-k slots.','RRF scores are not calibrated confidence; metric combines retrieval/refusal and is explicitly defined.','Distractors alter BM25 IDF; evidence IDs and hashes help auditing, not truth verification.'],sources=[HERE/'app.py'])
if __name__=='__main__':main()
