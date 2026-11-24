"""Shared lag-ranking MLP, trained with conditional cross entropy using NumPy.
Not a foundation model: the network sees 12 measured signal statistics per lag.
"""
import numpy as np


def softmax(z):
    z=z-z.max(axis=-1,keepdims=True)
    e=np.exp(z)
    return e/e.sum(axis=-1,keepdims=True)


def forward(X, p):
    Z=(X-np.asarray(p['mean']))/np.asarray(p['scale'])
    H=np.tanh(Z@np.asarray(p['w1'])+np.asarray(p['b1']))
    logits=(H@np.asarray(p['w2'])+np.asarray(p['b2']).reshape(-1)[0])[...,0]
    return logits,Z,H


def loss_grad(X, y, p, l2=.001):
    logits,Z,H=forward(X,p)
    probs=softmax(logits)
    n=len(y)
    loss=-np.log(probs[np.arange(n),y]+1e-12).mean()
    d=probs.copy();d[np.arange(n),y]-=1;d/=n
    w2=np.asarray(p['w2']);w1=np.asarray(p['w1'])
    dh=(d[...,None]*w2.T)*(1-H**2)
    grads={'w2':np.sum(H*d[...,None],axis=(0,1))[:,None]+l2*w2,
           'b2':np.array([d.sum()]),'w1':np.einsum('nki,nkj->ij',Z,dh)+l2*w1,
           'b1':dh.sum(axis=(0,1))}
    loss+=.5*l2*(np.sum(w1*w1)+np.sum(w2*w2))
    return float(loss),grads


def fit(X,y,V,vy,seed=7,epochs=180,hidden=16):
    rng=np.random.default_rng(seed)
    mean=X.mean(axis=(0,1));scale=np.maximum(X.std(axis=(0,1)),.05)
    p={'mean':mean,'scale':scale,'w1':rng.normal(0,.2,(X.shape[-1],hidden)),
       'b1':np.zeros(hidden),'w2':rng.normal(0,.2,(hidden,1)),'b2':np.zeros(1)}
    keys=['w1','b1','w2','b2'];m={k:np.zeros_like(p[k]) for k in keys};v={k:np.zeros_like(p[k]) for k in keys}
    log=[];best=1e9;bestp=None;step=0
    for epoch in range(epochs):
        order=rng.permutation(len(y));losses=[]
        for start in range(0,len(y),64):
            idx=order[start:start+64];loss,g=loss_grad(X[idx],y[idx],p)
            losses.append(loss);step+=1
            for k in keys:
                m[k]=.9*m[k]+.1*g[k];v[k]=.999*v[k]+.001*g[k]**2
                p[k]-=.008*(m[k]/(1-.9**step))/(np.sqrt(v[k]/(1-.999**step))+1e-8)
        vp=softmax(forward(V,p)[0]);vl=float(-np.log(vp[np.arange(len(vy)),vy]+1e-12).mean())
        if vl<best:
            best=vl;bestp={k:x.copy() for k,x in p.items()};best_epoch=epoch
        if epoch%10==0 or epoch==epochs-1:
            log.append({'epoch':epoch,'train_loss':float(np.mean(losses)),'validation_nll':vl,
                        'validation_accuracy':float(np.mean(vp.argmax(1)==vy))})
    return bestp,log,best_epoch


def temperature(logits,y):
    grid=np.exp(np.linspace(np.log(.3),np.log(5),101))
    nll=[-np.log(softmax(logits/t)[np.arange(len(y)),y]+1e-12).mean() for t in grid]
    return float(grid[np.argmin(nll)])


def predict(X,p,temp=1):
    return softmax(forward(X,p)[0]/temp)


def export(p):
    return {k:np.asarray(v).tolist() for k,v in p.items()}
