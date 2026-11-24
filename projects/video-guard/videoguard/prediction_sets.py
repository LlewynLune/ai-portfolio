"""Set-valued inference and bounded-risk diagnostics, independent of v0.6 code.
Definitions are explicit: LAC, log-LAC, randomized APS, conservative APS with
crossing label, and LAC+top1 completion. All remain invalid as OOD guarantees.
"""
import math
import numpy as np


def check_probabilities(probs):
    p=np.asarray(probs,dtype=np.float64)
    if p.ndim!=2 or not len(p) or p.shape[1]<2 or not np.isfinite(p).all():
        raise ValueError('need finite N x K probabilities')
    if np.any(p<0) or np.any(p>1+1e-12) or not np.allclose(p.sum(1),1,atol=1e-9):
        raise ValueError('invalid probabilities')
    return p


def quantile(scores,alpha=.1):
    s=np.asarray(scores,dtype=np.float64)
    if s.ndim!=1 or not len(s) or not np.isfinite(s).all() or not 0<alpha<1:
        raise ValueError('invalid scores or alpha')
    rank=math.ceil((len(s)+1)*(1-alpha))
    # n+1 correction: if no observed rank can support the target, infinity.
    return float(np.sort(s)[rank-1]) if rank<=len(s) else float('inf')


def aps_scores(probs,u=None):
    p=check_probabilities(probs)
    # Stable class-index tie order; documented rather than claiming random ties.
    order=np.argsort(-p,axis=1,kind='stable')
    sorted_p=np.take_along_axis(p,order,axis=1)
    cumulative=np.cumsum(sorted_p,axis=1)
    score=cumulative if u is None else cumulative-np.asarray(u)[:,None]*sorted_p
    if u is not None and (np.asarray(u).shape!=(len(p),) or np.any(np.asarray(u)<0) or np.any(np.asarray(u)>1)):
        raise ValueError('invalid APS uniforms')
    out=np.empty_like(p)
    np.put_along_axis(out,order,score,axis=1)
    return out,order,cumulative,sorted_p


def fit_threshold(probs,y,method='lac',alpha=.1,u=None):
    p=check_probabilities(probs);y=np.asarray(y)
    if y.shape!=(len(p),) or y.dtype.kind not in 'iu' or np.any(y<0) or np.any(y>=p.shape[1]):
        raise ValueError('invalid labels')
    if method in {'lac','lac_top1'}:s=1-p[np.arange(len(y)),y]
    elif method=='log_lac':s=-np.log(np.maximum(p[np.arange(len(y)),y],np.finfo(float).tiny))
    elif method=='aps_randomized':
        if u is None:raise ValueError('randomized APS needs explicit independent uniforms')
        s=aps_scores(p,u)[0][np.arange(len(y)),y]
    elif method=='aps_crossing':s=aps_scores(p)[0][np.arange(len(y)),y]
    else:raise ValueError('unknown method')
    return quantile(s,alpha)


def predict_sets(probs,q,method='lac',u=None):
    p=check_probabilities(probs)
    if math.isnan(q):raise ValueError('invalid threshold')
    if method in {'lac','lac_top1'}:
        sets=1-p<=q+1e-12
        if method=='lac_top1':sets[np.arange(len(p)),p.argmax(1)]=True
    elif method=='log_lac':sets=-np.log(np.maximum(p,np.finfo(float).tiny))<=q+1e-12
    elif method=='aps_randomized':
        if u is None:raise ValueError('randomized APS needs uniforms')
        sets=aps_scores(p,u)[0]<=q+1e-12
    elif method=='aps_crossing':
        _,order,cumulative,sorted_p=aps_scores(p)
        # Prefix includes the first label whose cumulative mass crosses q.
        # This is a conservative SUPERSET, not exact-size randomized APS.
        keep=cumulative-sorted_p < q
        keep[:,0]=True
        sets=np.zeros_like(p,dtype=bool);np.put_along_axis(sets,order,keep,axis=1)
    else:raise ValueError('unknown method')
    return sets


def set_metrics(sets,y,probs):
    y=np.asarray(y);sizes=sets.sum(1);covered=sets[np.arange(len(y)),y]
    per_class=[]
    for k in range(sets.shape[1]):
        mask=y==k
        per_class.append({'delay_frames':k-6,'n':int(mask.sum()),'coverage':float(covered[mask].mean()) if mask.any() else None})
    singleton=sizes==1;correct=covered[singleton]
    return {'n':len(y),'coverage':float(covered.mean()),'mean_size':float(sizes.mean()),
            'empty_rate':float((sizes==0).mean()),'singleton_rate':float(singleton.mean()),
            'singleton_error':float(1-correct.mean()) if singleton.any() else None,
            'size_histogram':np.bincount(sizes,minlength=sets.shape[1]+1).tolist(),'per_class':per_class}


def log_binomial_cdf(k,n,p):
    if p<=0:return 0.
    if p>=1:return 0. if k>=n else -float('inf')
    terms=np.array([math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)+i*math.log(p)+(n-i)*math.log1p(-p) for i in range(k+1)])
    m=float(terms.max());return m+math.log(float(np.exp(terms-m).sum()))


def binomial_upper(k,n,delta=.05):
    """Exact one-sided Clopper-Pearson upper bound, no scipy dependency.
    If n=0, no evidence -> 1. Repeated/clustered observations invalidate IID use.
    """
    if not isinstance(k,(int,np.integer)) or not isinstance(n,(int,np.integer)) or not 0<=k<=n or not 0<delta<1:
        raise ValueError('invalid binomial counts')
    if n==0 or k==n:return 1.
    if k==0:return float(-math.expm1(math.log(delta)/n))
    lo,hi=k/n,1.
    for _ in range(65):
        mid=(lo+hi)/2
        if log_binomial_cdf(k,n,mid)>math.log(delta):lo=mid
        else:hi=mid
    return (lo+hi)/2


def risk_curve(probs,y,eligible=None,thresholds=None):
    p=check_probabilities(probs);y=np.asarray(y)
    eligible=np.ones(len(y),bool) if eligible is None else np.asarray(eligible,dtype=bool)
    thresholds=np.linspace(0,1,21) if thresholds is None else thresholds
    conf=p.max(1);wrong=p.argmax(1)!=y;rows=[]
    for t in thresholds:
        accepted=eligible & (conf>=t);n=int(accepted.sum());k=int(wrong[accepted].sum())
        rows.append({'threshold':float(t),'accepted':n,'coverage':n/len(y),'errors':k,
                     'error_rate':k/n if n else None,'upper95':binomial_upper(k,n),
                     'simultaneous_upper95':binomial_upper(k,n,.05/len(thresholds))})
    return rows
