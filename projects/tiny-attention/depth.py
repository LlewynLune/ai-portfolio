"""TinyAttention: independent float64 implementation, causal prefix and key/value robustness."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
def main():
    m=load(HERE/'artifacts/model.json');prior=load(HERE/'artifacts/results.json');exclude=sum(prior['split_ids'].values(),[]);a=Attention(m);rows=[];examples=[];parity=[]
    for pairs in [2,3,4,5,6,7]:
        x,y=generate_lookup(120,92000+pairs,pairs,exclude=exclude);p=softmax(a.forward(x)[:,-1]);rows+=cls_rows('tiny','frozen_attention',f'length_{pairs}',y,p)
        if pairs==3:
            changed=x.copy();changed[:,1]=8+(changed[:,1]-8+1)%8;missing=x.copy();missing[:,-1]=17
            rows+=cls_rows('tiny','frozen_attention','query_unknown',y,softmax(a.forward(missing)[:,-1]))
            swapped=x.copy();swapped[:,:6]=x[:,[4,5,2,3,0,1]];rows+=cls_rows('tiny','frozen_attention','pair_reorder',y,softmax(a.forward(swapped)[:,-1]))
            for i in range(5):
                full=a.forward(x[i])[0]
                for prefix in range(1,len(x[i])+1):parity.append(float(np.max(abs(full[prefix-1]-a.forward(x[i,:prefix])[0,-1]))))
                _,w=a.forward(x[i],True);examples.append(dict(tokens=x[i].tolist(),truth=int(y[i]),last_attention=w[0,:,-1,:].tolist(),output=p[i].tolist()))
    assert max(parity)<1e-10
    save(HERE,'TinyAttention causal prefix & length stress','Frozen single-block model; 120 newly authored prefixes at each length2–7, plus reorder and unknown-query stress. No test tuning or retraining. Causal prefix logits compared at every token.',rows,['Causal invariance is a correctness property, not proof of key-value task generalization.','Attention weights can be inspected but are not causal explanations.','Unknown key stress is deliberately out-of-vocabulary task semantics; reported accuracy is not deployment performance.'],extra=dict(causal_prefix_max_error=max(parity),examples=examples),sources=[HERE/'artifacts/model.json',HERE/'artifacts/results.json'])
if __name__=='__main__':main()
