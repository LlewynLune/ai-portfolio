"""SpecDecode: real incremental KV cache vs full recompute; exact target path required."""
from pathlib import Path
import sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
def greedy(model,prefix,count=8,cached=False):
    seq=list(prefix);trace=[];cache=None
    if cached:
        for token in seq:logits,cache=model.step(token,cache)
    for i in range(count):
        if not cached:logits=model.forward(seq)[0,-1]
        token=int(np.argmax(logits));seq.append(token);trace.append(token)
        if cached and i<count-1:logits,cache=model.step(token,cache)
    return seq[len(prefix):],trace

def speculative(target,draft,prefix,count=8,k=4):
    seq=list(prefix);tc=dc=0;trace=[]
    while len(seq)-len(prefix)<count:
        length=min(k,count-(len(seq)-len(prefix)));tmp=list(seq);proposals=[]
        for _ in range(length):token=int(draft.forward(tmp)[0,-1].argmax());proposals.append(token);tmp.append(token);dc+=1
        logits=target.forward(seq+proposals)[0];tc+=1;offset=len(seq)-1;checks=[]
        for i,token in enumerate(proposals):
            actual=int(logits[offset+i].argmax());seq.append(actual);checks.append(dict(draft=token,target=actual,accepted=token==actual))
            if token!=actual:break
        if len(checks)==len(proposals) and all(c['accepted'] for c in checks) and len(seq)-len(prefix)<count:seq.append(int(logits[-1].argmax()))
        trace.append(dict(proposal=proposals,checks=checks,output=seq[len(prefix):]))
    return seq[len(prefix):],dict(target_calls=tc,draft_calls=dc,trace=trace)

def main():
    m=load(HERE/'artifacts/model.json');target=Attention(m['target']);draft=Attention(m['draft']);rng=np.random.default_rng(96001);prompts=rng.integers(0,8,(24,4));rows=[];maxerr=0.;traces=[]
    for p in prompts[:5]:
        full=target.forward(p)[0];cache=None
        for i,t in enumerate(p):z,cache=target.step(t,cache);maxerr=max(maxerr,float(np.max(abs(z-full[i]))))
    assert maxerr<1e-10
    for p in prompts[:2]:greedy(target,p);greedy(target,p,cached=True)
    for i,p in enumerate(prompts):
        baseline,_=greedy(target,p);cached,_=greedy(target,p,cached=True);assert baseline==cached
        for repeat in range(3):
            methods=[('full_recompute',False),('kv_cached',True)]
            for name,cached_flag in methods if (i+repeat)%2==0 else methods[::-1]:
                start=time.perf_counter();out,_=greedy(target,p,cached=cached_flag);ms=(time.perf_counter()-start)*1000;rows.append(dict(model=name,condition='decode8',index=f'{i}:{repeat}',correct=out==baseline,confidence=1.,loss=0.,elapsed_ms=ms,prefix=p.tolist(),output=out))
        for k in [1,2,4]:
            out,stats=speculative(target,draft,p,k=k);assert out==baseline;traces.append(dict(prompt=i,k=k,prefix=p.tolist(),output=out,**stats))
    times={n:[r['elapsed_ms'] for r in rows if r['model']==n] for n in ['full_recompute','kv_cached']}
    save(HERE,'SpecDecode incremental KV cache & exact paths','Two frozen tiny models,24 fresh4-token prefixes;8 greedy outputs;three repeats; full recompute vs real single-layer cached K/V. k1/2/4 speculative target-path verification retained.',rows,['K/V cache is exact per-layer inference, not caching final answers.','CPU timing only this environment; repeated timings are correlated and tiny models are overhead-sensitive.','Speculation remains deterministic greedy, not distribution-preserving random sampling.'],extra=dict(cache_max_logit_error=maxerr,timing={n:dict(median_ms=float(np.median(v)),p95_ms=float(np.quantile(v,.95))) for n,v in times.items()},speculative_traces=traces),sources=[HERE/'artifacts/model.json'])
if __name__=='__main__':main()
