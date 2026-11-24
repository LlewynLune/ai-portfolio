"""LoRA strength sweep: reconstructed low-rank delta vs merged export; no retraining."""
from pathlib import Path
import sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
def interpolate(base,adapted,strength):
    out=copy.deepcopy(base)
    for layer in ['q','v','head']:
        A=np.array(adapted['adapter_state'][layer+'.A']);B=np.array(adapted['adapter_state'][layer+'.B']);rank=A.shape[0];out['state'][layer+'.weight']=(np.array(base['state'][layer+'.weight'])+strength*B@A/rank).tolist()
    return out

def main():
    base=load(HERE.parent/'tiny-attention/artifacts/model.json');adapt=load(HERE/'artifacts/model.json');exclude=sum(load(HERE/'artifacts/results.json')['split_ids'].values(),[])+sum(load(HERE.parent/'tiny-attention/artifacts/results.json')['split_ids'].values(),[]);rows=[];parity=[]
    for strength in [0,.25,.5,.75,1,1.5]:
        a=Attention(interpolate(base,adapt,strength))
        for cond,shift in [('new_rule',1),('old_rule',0)]:
            x,y=generate_lookup(160,93001,3,shift,exclude=exclude);p=softmax(a.forward(x)[:,-1]);rows+=cls_rows('lora',f'alpha_{strength}',cond,y,p)
        if strength==1:parity.append(float(np.max(abs(a.forward(x)-Attention(adapt).forward(x)))))
    assert max(parity)<3e-5
    save(HERE,'LoRA adapter strength & retention frontier','Fixed rank4 q/v/head adapter delta, six strength settings. Same newly authored160 prefixes evaluated under old/new rules separately. Strength sweep not selected on test.',rows,['Adapter strength is a trade-off surface, not a free improvement.','Reconstructed low-rank delta and merged export agree within float32 export tolerance.','Original task and new-rule task share prefixes; not independent benchmarks.'],extra=dict(merge_max_logit_error=max(parity),strengths=[0,.25,.5,.75,1,1.5]),sources=[HERE/'artifacts/model.json',HERE.parent/'tiny-attention/artifacts/model.json',HERE/'artifacts/results.json',HERE.parent/'tiny-attention/artifacts/results.json'])
if __name__=='__main__':main()
