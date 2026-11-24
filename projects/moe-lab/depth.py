"""SparseMoE finite-capacity dispatcher with drop and second-choice policies."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
def dispatch(x,m,capacity_factor=None,policy='drop'):
    x=np.asarray(x,float)
    if x.ndim!=2 or x.shape[1]!=2 or not np.isfinite(x).all():raise ValueError('finite Nx2 input')
    probs=softmax(x@np.array(m['router']['weight']).T+m['router']['bias']);rank=np.argsort(-probs,axis=1,kind='stable');routes=rank[:,0].copy();counts=np.zeros(4,int);admitted=np.ones(len(x),bool);cap=len(x) if capacity_factor is None else int(np.ceil(len(x)/4*capacity_factor))
    for i in range(len(x)):
        choices=rank[i,:2] if policy=='second' else rank[i,:1];dest=next((int(k) for k in choices if counts[k]<cap),None)
        if dest is None:admitted[i]=False;routes[i]=-1
        else:routes[i]=dest;counts[dest]+=1
    out=np.zeros(len(x))
    for k,e in enumerate(m['experts']):
        ix=np.where(routes==k)[0]
        if len(ix):out[ix]=(np.tanh(x[ix]@np.array(e['first']['weight']).T+e['first']['bias'])@np.array(e['last']['weight']).T+e['last']['bias']).reshape(-1)*probs[ix,k]
    return out,routes,admitted,counts,probs

def main():
    m=load(HERE/'artifacts/model.json');rows=[];capacity=[]
    for cond in ['uniform','skew']:
        rng=np.random.default_rng(95001 if cond=='uniform' else 95002);x=rng.uniform(-1,1,(256,2))
        if cond=='skew':x[:,0]=rng.uniform(.6,1,len(x))
        y=np.where(x[:,0]>=0,np.sin(3*x[:,1])+.5*x[:,0],np.cos(3*x[:,1])-.5*x[:,0])
        for factor in [None,.5,1,1.5]:
            for policy in ['drop','second']:
                out,routes,kept,counts,p=dispatch(x,m,factor,policy);name=f'{policy}_capacity{factor}';capacity.append(dict(condition=cond,model=name,counts=counts.tolist(),kept=int(kept.sum()),coverage=float(kept.mean()),all_rmse=float(np.sqrt(np.mean((out-y)**2))),admitted_rmse=float(np.sqrt(np.mean((out[kept]-y[kept])**2))) if kept.any() else None))
                rows += [dict(model=name,condition=cond,index=i,truth=float(y[i]),prediction=float(out[i]),error=float(out[i]-y[i]),admitted=bool(kept[i]),route=int(routes[i])) for i in range(len(y))]
    save(HERE,'SparseMoE capacity, overflow & second-choice routing','Frozen4-expert model; two fresh256-sample batches; capacities0.5/1/1.5 and unlimited; ordered dispatch, drop→zero vs second-ranked fallback. All-item and admitted-only RMSE both recorded.',rows,['Dropped items remain in all-item RMSE; coverage cannot be hidden by reporting admitted-only quality.','Second-choice routing changes probabilities and expert semantics; not guaranteed improvement.','Batch-order routing is deterministic but order-sensitive; not distributed AllToAll throughput.'],extra=dict(capacity=capacity),sources=[HERE/'artifacts/model.json'])
if __name__=='__main__':main()
