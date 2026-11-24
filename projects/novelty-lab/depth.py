"""NoveltyLab: single-feature sensitivity vs centroid-aware contribution; frozen scaler."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
def score(x,m):
    x=np.asarray(x,float)
    if x.shape[-1]!=13 or not np.isfinite(x).all():raise ValueError('13 finite features')
    z=(x-m['mean'])/m['scale']-m['center'];return np.linalg.norm(z,axis=-1),z*z

def main():
    from sklearn.datasets import load_wine
    m=load(HERE/'artifacts/model.json');old=load(HERE/'artifacts/results.json');d=load_wine();ids=np.array(old['split']['test']);x=d.data[ids];y=(d.target[ids]!=0).astype(int);rows=[];sensitivity=[]
    for amplitude in [0,.25,.5,1,2]:
        for feature in range(13):
            xx=x.copy();xx[:,feature]+=amplitude*m['scale'][feature];s,c=score(xx,m);pred=s>m['threshold']
            for i in range(len(ids)):rows.append(dict(model='centroid_distance',condition=f'zshift_{amplitude}',index=f'{ids[i]}:feature{feature}',truth=int(y[i]),prediction=int(pred[i]),confidence=0.,correct=bool(pred[i]==y[i]),loss=0.,feature=feature,score=float(s[i]),squared_contribution=float(c[i,feature])))
            sensitivity.append(dict(amplitude=amplitude,feature=feature,name=m['feature_names'][feature],flip_rate=float(np.mean(pred!=(score(x,m)[0]>m['threshold'])))))
    examples=[]
    for idx in ids[:8]:
        s,c=score(d.data[idx],m);examples.append(dict(row=int(idx),score=float(s),contributions=c.tolist(),top_features=np.argsort(c)[-3:][::-1].tolist()))
    save(HERE,'NoveltyLab feature sensitivity & attribution','Frozen centroid/scaler, 131 historical test rows × 13 single-feature shifts × 5 standardized amplitudes. Each shift is authored; correlations and class plausibility are not enforced.',rows,['Corrected attribution uses squared distance to fitted centroid, not distance to origin.','Repeated feature variants are correlated: intervals do not establish independent sample confidence.','High detection metrics on Wine classes do not represent industrial anomaly effectiveness.'],extra=dict(sensitivity=sensitivity,examples=examples),sources=[HERE/'artifacts/model.json',HERE/'artifacts/results.json'])
if __name__=='__main__':main()
