"""VisionCal: fresh public held-out pixels, corruption sweep, selective-risk curves."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
def main():
    from sklearn.datasets import load_digits
    old=load(HERE/'artifacts/results.json');m=load(HERE/'artifacts/model.json');d=load_digits();ids=np.array(old['split']['test']);x=d.data[ids]/16;y=d.target[ids];rows=[];rng=np.random.default_rng(91003)
    configs=[('clean',x)]
    for sigma in [.05,.15,.3,.5]:configs.append(('noise_'+str(sigma),np.clip(x+rng.normal(0,sigma,x.shape),0,1)))
    for shift in [1,2]:
        a=np.roll(x.reshape(-1,8,8),shift,axis=2);a[:,:,:shift]=0;configs.append(('shift_'+str(shift),a.reshape(-1,64)))
    mask=x.reshape(-1,8,8).copy();mask[:,3:5,3:5]=0;configs.append(('center_occluded',mask.reshape(-1,64)));curves=[]
    for group,xx in configs:
        logits=affine(xx,m)
        for name,t in [('raw',1),('temperature',m['temperature'])]:
            p=softmax(logits/t);rr=cls_rows('vision',name,group,y,p,ids);rows.extend(rr)
            for threshold in [.5,.7,.8,.9,.95,.99]:
                keep=[r for r in rr if r['confidence']>=threshold];err=sum(not r['correct'] for r in keep);curves.append(dict(model=name,condition=group,threshold=threshold,n=len(keep),coverage=len(keep)/len(rr),error=err/len(keep) if keep else None,error_interval=wilson(err,len(keep))))
    # pixel gradients are measured perturbations, not saliency proof.
    save(HERE,'VisionCal corruption surface & selective risk','Frozen 64→48→10 MLP; same 360 historical held-out IDs, new fixed-seed corruptions, 8 conditions. Temperature frozen on prior validation. Test sweeps descriptive, not safety threshold selection.',rows,['Temperature changes probabilities, not argmax accuracy.','Increasing noise/occlusion/translation tests brittleness without claiming real OCR robustness.','Coverage/error must be read together; writer isolation remains unavailable.'],extra=dict(curves=curves,seed=91003),sources=[HERE/'artifacts/model.json',HERE/'artifacts/results.json'])
if __name__=='__main__':main()
