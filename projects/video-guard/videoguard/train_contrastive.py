from pathlib import Path
import time,json
import numpy as np
from .data import make_clip
from .features import extract
from .contrastive import temporal_inputs,fit,logits
from .model import softmax,temperature
from .calibration import metrics
from .experiment import write_json,ROOT


def pack(start,n,condition='id'):
    V=[];A=[];y=[]
    for seed in range(start,start+n):
        c=make_clip(seed,condition=condition);s=extract(c.frames,c.audio,20,8000)
        v,a=temporal_inputs(s);V.append(v);A.append(a);y.append(c.delay+6)
    return np.array(V),np.array(A),np.array(y)


def run():
    out=ROOT/'artifacts';start=time.perf_counter()
    tr=pack(110000,1600);va=pack(120000,400);ca=pack(130000,250)
    results={'type':'two-tower temporal InfoNCE','training_samples':1600,'seeds':[]}
    for seed in [43,57,71]:
        print('Contrastive seed',seed,flush=True)
        p,log,epoch=fit(*tr,*va,seed=seed)
        temp=temperature(logits(ca[0],ca[1],p)[0],ca[2]);conditions={}
        for j,name in enumerate(['id','noise','periodic','silent','distractor','drift','missing','long']):
            v,a,y=pack(140000 if name=='id' else 150000+j*1000,600 if name=='id' else 240,name)
            conditions[name]=metrics(softmax(logits(v,a,p)[0]/temp),y)
        results['seeds'].append({'seed':seed,'selected_epoch':epoch,'temperature':temp,'conditions':conditions})
        write_json(out/f'contrastive-training-{seed}.json',log)
        if seed==43:write_json(out/'contrastive-model.json',{'parameters':{k:v.tolist() for k,v in p.items()},'temperature':temp,'architecture':'24→32→8 dual tower','seed':seed})
    results['wall_seconds']=time.perf_counter()-start;write_json(out/'contrastive-results.json',results)
    print(json.dumps({k:r['accuracy'] for k,r in results['seeds'][0]['conditions'].items()},indent=2),flush=True)

if __name__=='__main__':run()
