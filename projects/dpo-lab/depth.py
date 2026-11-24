"""DPO: output-head interpolation, preference/accuracy/KL separated on fresh prefixes."""
from pathlib import Path
import sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
def main():
    ref=load(HERE.parent/'tiny-attention/artifacts/model.json');policy=load(HERE/'artifacts/model.json');exclude=sum(load(HERE/'artifacts/results.json')['split_ids'].values(),[])+sum(load(HERE.parent/'tiny-attention/artifacts/results.json')['split_ids'].values(),[]);x,original=generate_lookup(180,94001,3,exclude=exclude);chosen=8+(original-8+2)%8;rprob=softmax(Attention(ref).forward(x)[:,-1]);rows=[];frontier=[]
    for strength in [0,.25,.5,.75,1,1.25]:
        m=copy.deepcopy(ref)
        for key in ['head.weight','head.bias']:m['state'][key]=(np.asarray(ref['state'][key])+strength*(np.asarray(policy['state'][key])-np.asarray(ref['state'][key]))).tolist()
        p=softmax(Attention(m).forward(x)[:,-1]);rr=cls_rows('dpo',f'alpha_{strength}','chosen_top1',chosen,p);rows+=rr
        kl=np.sum(p*np.log(np.maximum(p,1e-15)/np.maximum(rprob,1e-15)),axis=1);win=p[np.arange(len(x)),chosen]>p[np.arange(len(x)),original]
        for i,r in enumerate(rr):r.update(pair_win=bool(win[i]),reference_kl=float(kl[i]),original_correct=bool(p[i].argmax()==original[i]))
        frontier.append(dict(strength=strength,pair_win=float(win.mean()),chosen_top1=float((p.argmax(-1)==chosen).mean()),original_retention=float((p.argmax(-1)==original).mean()),kl=float(kl.mean())))
    save(HERE,'DPO preference / accuracy / KL frontier','Frozen head-only DPO policy and reference; interpolate output head over six strengths, fresh180 synthetic prefixes; chosen rule +2 and rejected original. No new optimizer training or test selection.',rows,['Pair wins and chosen top1 can move differently; both are explicitly computed.','Parameter interpolation is an inference diagnostic, not equivalent to retraining with a different beta.','KL and original-task loss remain visible; no human-alignment claim.'],extra=dict(frontier=frontier),sources=[HERE/'artifacts/model.json',HERE.parent/'tiny-attention/artifacts/model.json',HERE/'artifacts/results.json',HERE.parent/'tiny-attention/artifacts/results.json'])
if __name__=='__main__':main()
