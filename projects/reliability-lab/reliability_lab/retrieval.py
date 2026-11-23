"""Actual local BM25 retrieval with an authored fixture corpus; no LLM/network.
Corpus is deliberately small and is not an external standard benchmark.
"""
from collections import Counter
import hashlib
import json
import math
import re
import asyncio
from .engine import SyntheticWorker, RetryableError, PermanentError
from .config import fault_for

DOCUMENTS = [
    {'id':'timeout','text':'An attempt timeout stops a slow operation. A workflow deadline includes queue wait and retries.'},
    {'id':'retry','text':'Retry transient failures with bounded attempts and exponential backoff. Do not retry permanent validation errors.'},
    {'id':'idempotency','text':'Idempotency keys prevent duplicate local side effects after acknowledgement loss. This does not guarantee external exactly once.'},
    {'id':'checkpoint','text':'Checkpoints store successful stage output. Resume checks workload configuration version and code hashes before reuse.'},
    {'id':'budget','text':'Queue admission consumes the workflow budget. A queued task may expire before a worker starts.'},
    {'id':'cancel','text':'Async cancellation requires cooperative workers and resource cleanup in finally blocks. Blocking plugins need process isolation.'},
    {'id':'metrics','text':'Report all request latency and successful request latency separately. Fast failed requests must not be called quality improvements.'},
    {'id':'trace','text':'Trace events include task stage attempt status and monotonic timestamps. Preserve raw events to recompute experiment metrics.'},
    {'id':'fault','text':'Fixed fault manifests must be independent of policy. Timeout parameter changes must not alter injected slow operation duration.'},
    {'id':'quality','text':'Execution success is different from answer correctness. Retrieval quality needs relevance labels and held out questions.'},
    {'id':'crash','text':'A process crash after a durable commit but before its checkpoint can replay a side effect. Local idempotency should suppress it.'},
    {'id':'local','text':'A local experiment does not demonstrate distributed production reliability GPU inference or real API token cost.'},
]
QUESTIONS = [
    {'query':'attempt timeout slow operation','relevant':['timeout'],'split':'development'},
    {'query':'retry transient bounded attempts','relevant':['retry'],'split':'development'},
    {'query':'idempotency duplicate acknowledgement','relevant':['idempotency'],'split':'development'},
    {'query':'checkpoints configuration version reuse','relevant':['checkpoint'],'split':'development'},
    {'query':'queue budget worker expire','relevant':['budget'],'split':'development'},
    {'query':'async cooperative cancellation cleanup','relevant':['cancel'],'split':'development'},
    {'query':'request latency failed quality','relevant':['metrics'],'split':'evaluation'},
    {'query':'trace monotonic timestamp raw events','relevant':['trace'],'split':'evaluation'},
    {'query':'fixed fault policy duration','relevant':['fault'],'split':'evaluation'},
    {'query':'answer correctness relevance labels','relevant':['quality'],'split':'evaluation'},
    {'query':'process crash durable checkpoint replay','relevant':['crash'],'split':'evaluation'},
    {'query':'GPU production real token cost','relevant':['local'],'split':'evaluation'},
    {'query':'after commit before checkpoint crash','relevant':['crash'],'split':'evaluation'},
    {'query':'stop blocking plugin cleanup','relevant':['cancel'],'split':'evaluation'},
    {'query':'slow attempt queue workflow deadline','relevant':['timeout','budget'],'split':'evaluation'},
    {'query':'local side effects duplicate keys','relevant':['idempotency','crash'],'split':'evaluation'},
    # Deliberately harder paraphrases: the lexical retriever may fail without shared words.
    {'query':'deduplicate durable transaction when confirmation disappears','relevant':['idempotency','crash'],'split':'challenge'},
    {'query':'relaunch previously finished computation safely','relevant':['checkpoint'],'split':'challenge'},
    {'query':'endless waiting consumes entire allowance','relevant':['timeout','budget'],'split':'challenge'},
    {'query':'semantic evidence insufficient refuse fabricated answer','relevant':['quality'],'split':'challenge'},
]

def tokens(text): return re.findall(r'[a-z0-9]+',text.lower())

def rank(query, method='bm25'):
    terms=Counter(tokens(query)); docs=[Counter(tokens(d['text'])) for d in DOCUMENTS]
    average=sum(sum(d.values()) for d in docs)/len(docs)
    scores=[]
    for doc,freq in zip(DOCUMENTS,docs):
        score=0.
        for term in terms:
            tf=freq[term]
            if method=='overlap': score+=bool(tf)
            elif method=='bm25':
                df=sum(term in d for d in docs)
                idf=math.log(1+(len(docs)-df+.5)/(df+.5))
                score+=idf*tf*2.2/(tf+1.2*(.25+.75*sum(freq.values())/average)) if tf else 0
            else: raise ValueError('unknown retrieval method')
        scores.append({'id':doc['id'],'text':doc['text'],'score':score})
    return sorted(scores,key=lambda d:(-d['score'],d['id']))

def quality_report():
    rows=[]
    for split in ('development','evaluation','challenge'):
        for method in ('overlap','bm25'):
            cases=[]
            for q in QUESTIONS:
                if q['split']!=split: continue
                ranking=[d for d in rank(q['query'],method) if d['score']>0]
                rel=set(q['relevant']); top=[d['id'] for d in ranking[:3]]
                rr=next((1/(i+1) for i,d in enumerate(ranking) if d['id'] in rel),0)
                cases.append({**q,'top3':top,'recall3':len(rel.intersection(top))/len(rel),'reciprocal_rank':rr})
            rows.append({'split':split,'method':method,'count':len(cases),
                         'recall3':sum(c['recall3'] for c in cases)/len(cases),
                         'mrr':sum(c['reciprocal_rank'] for c in cases)/len(cases),'cases':cases})
    return {'workload':'authored_local_retrieval','documents':DOCUMENTS,'questions':QUESTIONS,'metrics':rows,
            'limits':['tiny authored English fixture, not public benchmark','questions directly related to document wording',
                      'held-out labels do not remove author selection bias','no LLM reasoning or answer evaluation']}

class RetrievalWorker(SyntheticWorker):
    corpus_hash=hashlib.sha256(json.dumps([DOCUMENTS,QUESTIONS],sort_keys=True).encode()).hexdigest()
    @property
    def workload_id(self):
        from pathlib import Path
        return 'authored_local_bm25:'+self.corpus_hash+':'+hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    async def execute(self,task,stage,attempt,previous):
        if stage!='commit':
            await super().execute(task,stage,attempt,previous)  # deterministic timing/fault injection
        if stage=='ingest':
            return {'valid':True,'query':QUESTIONS[task%len(QUESTIONS)]['query']}
        if stage=='retrieve':
            hits=[d for d in rank(previous['query']) if d['score']>0][:3]
            if not hits:
                raise PermanentError('no lexical evidence; abstain rather than fabricate')
            return {**previous,'hits':hits}
        if stage=='analyze':
            hit=previous['hits'][0]
            return {**previous,'answer':hit['text'],'citations':[hit['id']]}
        if stage=='validate':
            ids={d['id'] for d in DOCUMENTS}
            if not previous.get('citations') or not set(previous['citations'])<=ids:
                raise PermanentError('unknown citation')
            return {**previous,'citation_valid':True}
        if stage=='commit':
            await asyncio.sleep(self.config.base_ms/1000)
            output={**previous,'task':task,'stage':'commit'}
            self.store.commit(self.scope,task,output,self.idempotent)
            if fault_for(self.config,task,stage)=='ack_lost' and attempt==1:
                raise RetryableError('local retrieval result committed; acknowledgement lost')
            return output
        raise ValueError('unknown stage')
