"""Two independently learned temporal encoders with lag-wise InfoNCE.
This consumes measured visual/RMS sequences (NOT RGB tokens or pretrained CLIP).
The failed/limited baseline is reported, not promoted only when it wins.
"""
import numpy as np
from .features import normalize
from .data import LAGS
from .model import softmax


def temporal_inputs(signals):
    v=normalize(signals['visual']);a=normalize(signals['audio']);n=len(v)
    anchors=np.linspace(6,n-30,3).astype(int)
    V=np.array([v[i:i+24] for i in anchors])
    A=np.array([[a[i+int(k):i+int(k)+24] for i in anchors] for k in LAGS])
    return V,A


def encode(x,p,prefix):
    h=np.tanh(x@p[prefix+'w1']+p[prefix+'b1'])
    z=h@p[prefix+'w2']+p[prefix+'b2']
    norm=np.sqrt(np.sum(z*z,axis=-1,keepdims=True)+1e-8)
    return z/norm,(x,h,z,norm)


def back(d,cache,p,prefix):
    x,h,z,norm=cache;e=z/norm
    dz=(d-e*np.sum(d*e,axis=-1,keepdims=True))/norm
    dh=(dz@p[prefix+'w2'].T)*(1-h*h)
    return {prefix+'w2':h.reshape(-1,h.shape[-1]).T@dz.reshape(-1,dz.shape[-1]),
            prefix+'b2':dz.reshape(-1,dz.shape[-1]).sum(0),
            prefix+'w1':x.reshape(-1,x.shape[-1]).T@dh.reshape(-1,dh.shape[-1]),
            prefix+'b1':dh.reshape(-1,dh.shape[-1]).sum(0)}


def logits(V,A,p):
    v,vc=encode(V,p,'v');a,ac=encode(A,p,'a')
    return np.mean(np.sum(v[:,None,:,:]*a,axis=-1),axis=-1)/.15,(v,a,vc,ac)


def loss_grad(V,A,y,p):
    z,(v,a,vc,ac)=logits(V,A,p);pr=softmax(z);n=len(y)
    loss=-np.log(pr[np.arange(n),y]+1e-12).mean()
    d=pr.copy();d[np.arange(n),y]-=1;d/=n
    d=d[:,:,None,None]/(.15*V.shape[1])
    dv=np.sum(d*a,axis=1);da=d*v[:,None,:,:]
    g=back(dv,vc,p,'v');g.update(back(da,ac,p,'a'))
    return float(loss),g


def fit(V,A,y,vV,vA,vy,epochs=120,seed=43):
    rng=np.random.default_rng(seed);p={}
    for prefix in ['v','a']:
        p.update({prefix+'w1':rng.normal(0,.15,(24,32)),prefix+'b1':np.zeros(32),
                  prefix+'w2':rng.normal(0,.15,(32,8)),prefix+'b2':np.zeros(8)})
    m={k:np.zeros_like(x) for k,x in p.items()};w={k:np.zeros_like(x) for k,x in p.items()}
    best=1e9;bestp=None;log=[];step=0
    for ep in range(epochs):
        order=rng.permutation(len(y));losses=[]
        for i in range(0,len(y),64):
            idx=order[i:i+64];loss,g=loss_grad(V[idx],A[idx],y[idx],p);losses.append(loss);step+=1
            for k in p:
                grad=g[k]+.0001*p[k];m[k]=.9*m[k]+.1*grad;w[k]=.999*w[k]+.001*grad*grad
                p[k]-=.002*(m[k]/(1-.9**step))/(np.sqrt(w[k]/(1-.999**step))+1e-8)
        pr=softmax(logits(vV,vA,p)[0]);vl=float(-np.log(pr[np.arange(len(vy)),vy]+1e-12).mean())
        if vl<best:best=vl;bestp={k:x.copy() for k,x in p.items()};best_epoch=ep
        if ep%10==0 or ep==epochs-1:log.append({'epoch':ep,'loss':float(np.mean(losses)),'validation_nll':vl,'accuracy':float(np.mean(pr.argmax(1)==vy))})
    return bestp,log,best_epoch
