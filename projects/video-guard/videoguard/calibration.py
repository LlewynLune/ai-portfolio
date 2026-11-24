"""Calibration, uncertainty and paired bootstrap. Bounds are empirical, not guarantees."""
import numpy as np


def metrics(probs,y):
    p=np.asarray(probs);y=np.asarray(y,dtype=int)
    pred=p.argmax(1);conf=p.max(1);ok=pred==y
    one=np.eye(p.shape[1])[y]
    bins=[];ece=0.
    for a,b in zip(np.linspace(0,1,11)[:-1],np.linspace(0,1,11)[1:]):
        mask=(conf>=a)&(conf<b if b<1 else conf<=b)
        if mask.any():
            accuracy=float(ok[mask].mean());c=float(conf[mask].mean())
            ece+=mask.mean()*abs(accuracy-c)
            bins.append({'low':float(a),'high':float(b),'count':int(mask.sum()),'accuracy':accuracy,'confidence':c})
    return {'n':len(y),'accuracy':float(ok.mean()),'mae_frames':float(np.abs(pred-y).mean()),
            'nll':float(-np.log(p[np.arange(len(y)),y]+1e-12).mean()),
            'brier_multiclass':float(np.mean(np.sum((p-one)**2,axis=1))),
            'ece_10_equal_width':float(ece),'reliability_bins':bins}


def choose_threshold(probs,y,target_error=.05):
    """Empirical calibration-set precision constraint; no finite-sample risk guarantee."""
    conf=probs.max(1);ok=probs.argmax(1)==y
    options=[]
    for t in np.linspace(0,1,201):
        accept=conf>=t
        if accept.sum()>=20 and 1-ok[accept].mean()<=target_error:
            options.append((float(accept.mean()),float(t)))
    return min([t for cov,t in options if cov==max([x[0] for x in options])]) if options else 1.01


def selective(probs,y,threshold,scorable=None):
    accept=probs.max(1)>=threshold
    if scorable is not None:
        accept &= np.asarray(scorable)
    return {'threshold':float(threshold),'accepted':int(accept.sum()),'coverage':float(accept.mean()),
            'accepted_error':float(np.mean(probs.argmax(1)[accept]!=y[accept])) if accept.any() else None}


def conformal_q(probs,y,alpha=.1):
    scores=1-probs[np.arange(len(y)),y]
    rank=int(np.ceil((len(scores)+1)*(1-alpha)))
    return float(np.sort(scores)[min(rank,len(scores))-1])


def conformal_sets(probs,q):
    return probs >= (1-q-1e-12)


def bootstrap_difference(a,b,seed=8,repeats=1000):
    d=np.asarray(a,dtype=float)-np.asarray(b,dtype=float)
    rng=np.random.default_rng(seed)
    means=np.mean(d[rng.integers(0,len(d),(repeats,len(d)))],axis=1)
    return {'difference':float(d.mean()),'ci_95_percentile':np.quantile(means,[.025,.975]).tolist(),
            'unit':'paired clip','replicates':repeats}
