"""CircuitID: system identification from noisy ideal low-voltage RC step simulations."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interdisciplinary_support import save,linear_export,mlp_export,forward,regression
import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
ROOT=Path(__file__).resolve().parent
TIME=np.linspace(0,10,32) # milliseconds, unit step normalized to1

def generate(n,seed,group='id'):
 r=np.random.default_rng(seed);tau=r.uniform(.5,3,n) if group!='slow_ood' else r.uniform(4,6,n)
 clean=1-np.exp(-TIME[None,:]/tau[:,None]);sig=r.uniform(.005,.025,(n,1)) if group!='noisy_ood' else np.full((n,1),.08)
 offset=np.full((n,1),.10) if group=='offset_ood' else np.zeros((n,1));gain=r.uniform(.98,1.02,(n,1))
 x=gain*clean+offset+r.normal(size=(n,len(TIME)))*sig
 return x,tau,clean

def physical(x):
 return np.array([np.exp(minimize_scalar(lambda logt:np.mean((1-np.exp(-TIME/np.exp(logt))-v)**2),bounds=(np.log(.1),np.log(12)),method='bounded').x) for v in x])
def crossing(x):
 out=[]
 for v in x:
  idx=np.where(v>=1-np.exp(-1))[0];out.append(float(TIME[idx[0]]) if len(idx) else 10.)
 return np.array(out)

def main():
 tr,yt,_=generate(1800,10);va,yv,_=generate(400,20);sc=StandardScaler().fit(tr);a=sc.transform(tr);b=sc.transform(va)
 candidates=[Ridge(alpha=c).fit(a,np.log(yt)) for c in [.1,1,10]];ridge=min(candidates,key=lambda m:regression(yv,np.exp(m.predict(b)))['mae'])
 net=MLPRegressor(hidden_layer_sizes=(48,),activation='tanh',alpha=.01,max_iter=350,random_state=42).fit(a,np.log(yt))
 models={'ridge':ridge,'mlp':net};chosen=min(models,key=lambda n:regression(yv,np.exp(models[n].predict(b)))['mae']);est=models[chosen]
 model=linear_export(est,sc.mean_,sc.scale_) if chosen=='ridge' else mlp_export(est,sc.mean_,sc.scale_)
 model['target_transform']='exp(log_tau_ms)';model['time_ms']=TIME.tolist();model['selected']=chosen
 residual=np.abs(yv-np.exp(est.predict(b)));q=float(np.sort(residual)[min(len(residual)-1,int(np.ceil((len(residual)+1)*.9))-1)]);model['interval_abs_ms']=q
 rows=[];predictions=[];examples=[]
 for group in ['id','noisy_ood','offset_ood','slow_ood']:
  for seed in [31,32,33]:
   x,y,clean=generate(160,seed,group);scores={'crossing63':crossing(x),'physical_curve_fit':physical(x),**{n:np.exp(m.predict(sc.transform(x))) for n,m in models.items()}}
   for name,p in scores.items():
    rows.append({'group':group,'seed':seed,'model':name,**regression(y,p),'coverage90':float((np.abs(y-p)<=q).mean()) if name==chosen else None})
    predictions.extend({'group':group,'seed':seed,'sample':i,'model':name,'truth_tau_ms':float(t),'pred_tau_ms':float(v)} for i,(t,v) in enumerate(zip(y,p)))
   if seed==31:
    pp=scores[chosen];worst=int(np.argmax(np.abs(y-pp)))
    for i in dict.fromkeys([0,worst]):examples.append({'group':group,'input':x[i].tolist(),'clean':clean[i].tolist(),'truth':float(y[i]),'output':[float(pp[i])],'interval_abs_ms':q})
 assert np.max(np.abs(np.exp(forward(va[:10],model).reshape(-1))-np.exp(est.predict(b[:10]))))<1e-9
 report={'title':'CircuitID','protocol':'Independent synthetic RC step waveforms: train1800, validation400, 4 test groups x3 seeds x160. Tau0.5–3ms train; slow OOD4–6ms. Ridge alpha and default model chosen only validation; physical solver does not train.',
 'source':'https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits',
 'split':{'train_seed':10,'validation_seed':20,'test_seeds':[31,32,33]},'metrics':rows,'predictions':predictions,'examples':examples,
 'selected':chosen,'validation_interval_q_ms':q,'loss_curve':net.loss_curve_,
 'limits':['All ideal analytic RC simulations; no measured board/oscilloscope/hardware validation.','Only tau=RC identifiable from normalized step; cannot identify R and C separately.','Known unit input assumption; gain drift/offset break model and physical baseline.','Sampling fixed10ms/32points; no parasitics, inductance, temperature or device aging modeled.','Validation residual interval coverage has no guarantee for OOD; not certified tolerance.','No physical device control or high-voltage actions. AI assisted learning prototype.']}
 save(ROOT,report,model)
if __name__=='__main__':main()
