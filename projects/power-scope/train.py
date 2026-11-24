"""PowerScope: offline one-step synthetic AI data-center power forecasting, never control."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interdisciplinary_support import save,linear_export,forward,regression
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
ROOT=Path(__file__).resolve().parent
FEATURES=['facility_now_kw','facility_lag1_kw','facility_lag12_kw','facility_lag288_kw','it_now_kw','outdoor_now_c','sin_day','cos_day','planned_it_next_kw']

def generate(days=36,seed=42,shift=False):
 rng=np.random.default_rng(seed);n=days*288;t=np.arange(n);phase=2*np.pi*t/288;outdoor=24+5*np.sin(phase-.8)+rng.normal(0,.6,n);work=np.zeros(n)
 for _ in range(days*8):
  start=int(rng.integers(0,n-48));duration=int(rng.integers(12,48));work[start:start+duration]+=rng.uniform(100,350)
 scheduled_it=350+60*np.sin(phase)+work
 it=scheduled_it+rng.normal(0,7,n)
 # Toy accounting assumptions only; not device electrical ratings or empirical PUE.
 cool=45+.12*it+.0025*it*np.maximum(outdoor-20,0);loss=.03*it+15;facility=it+cool+loss+rng.normal(0,6,n)
 if shift:facility+=.22*it+80*(outdoor>26)
 planned=np.concatenate([scheduled_it[1:],scheduled_it[-1:]])+rng.normal(0,35,n) # forecast known from authored job schedule, not measured future IT
 return {'time':t,'it':it,'outdoor':outdoor,'facility':facility,'planned_next_it':planned}
def design(series):
 p=series['facility'];t=np.arange(288,len(p)-1);phase=2*np.pi*t/288
 x=np.column_stack([p[t],p[t-1],p[t-12],p[t-288],series['it'][t],series['outdoor'][t],np.sin(phase),np.cos(phase),series['planned_next_it'][t]])
 y=p[t+1];return t,x,y

def main():
 s=generate();t,x,y=design(s);tr=t+1<20*288;va=(t>=20*288)&(t+1<26*288);te=t>=26*288
 sc=StandardScaler().fit(x[tr]);a=sc.transform(x[tr]);b=sc.transform(x[va]);c=sc.transform(x[te]);candidates=[Ridge(alpha=v).fit(a,y[tr]) for v in [.1,1,10,100]]
 est=min(candidates,key=lambda m:regression(y[va],m.predict(b))['mae']);model=linear_export(est,sc.mean_,sc.scale_);model.update({'features':FEATURES,'selected':'ridge_full','alpha':float(est.alpha),'prediction_unit':'kW at next5minute interval','capacity_scenario_kw':1200})
 no_plan=Ridge(alpha=10).fit(a[:,:-1],y[tr]);absres=abs(y[va]-est.predict(b));q=float(np.sort(absres)[min(len(absres)-1,int(np.ceil((len(absres)+1)*.9))-1)]);model['interval_abs_kw']=q
 shifted=generate(days=10,seed=99,shift=True);ot,ox,oy=design(shifted)
 rows=[];predictions=[];examples=[]
 for group,xx,yy,tt in [('chronological_test',x[te],y[te],t[te]),('cooling_drift_ood',ox,oy,ot)]:
  zz=sc.transform(xx);methods={'persistence':xx[:,0],'seasonal_lag288':xx[:,3],'ridge_no_plan':no_plan.predict(zz[:,:-1]),'ridge_full':est.predict(zz)}
  for name,p in methods.items():
   actual=yy>1200;flag=p+q>1200
   tp=int(np.sum(flag&actual));fp=int(np.sum(flag&~actual));fn=int(np.sum(~flag&actual))
   rows.append({'group':group,'model':name,**regression(yy,p),'interval90_coverage':float((abs(yy-p)<=q).mean()) if name=='ridge_full' else None,'flag_tp':tp,'flag_fp':fp,'flag_fn':fn})
   predictions.extend({'group':group,'time_index':int(i),'model':name,'actual_kw':float(v),'forecast_kw':float(pp)} for i,v,pp in zip(tt,yy,p))
  pred=methods['ridge_full'];worst=int(np.argmax(abs(yy-pred)))
  for i in dict.fromkeys([0,worst,100]):examples.append({'group':group,'time_index':int(tt[i]),'input':xx[i].tolist(),'truth':float(yy[i]),'output':[float(pred[i])],'interval_abs_kw':q})
 assert np.max(abs(forward(x[te][:20],model).reshape(-1)-est.predict(c[:20])))<1e-8
 # Annual energy PUE is not computed; this is a same-window synthetic ratio.
 kwh=s['facility'].sum()/12;itkwh=s['it'].sum()/12
 report={'title':'PowerScope','protocol':'Authored synthetic36days at5min; train first20days, validation next6days, test last10days; lag288 requires firstday warmup. One-step forecasts use known-now sensors and noisy planned-next-IT input, never measured future facility power. Fixed cooling-drift10day OOD independent seed.',
 'source':'https://www.energy.gov/cmei/femp/energy-efficiency-data-centers','split':{'train_target_before':20*288,'validation_target_before':26*288,'test_from':26*288,'embargo_note':'training rows whose next-step target crosses boundary removed below'},
 'metrics':rows,'predictions':predictions,'examples':examples,'series_summary':{'facility_energy_kwh':float(kwh),'it_energy_kwh':float(itkwh),'same_window_energy_ratio':float(kwh/itkwh)},
 'limits':['All traces/scheduler forecasts/cooling/loss factors are authored simulation, no real ByteDance or external facility telemetry.','5min interval average power; cannot evaluate subsecond electrical transients.','Toy1200kW threshold not equipment rating, redundancy margin or breaker limit.','Interval from chronological validation residuals; autocorrelation violates exchangeability, no guaranteed90% coverage.','Same-window ratio not audited annual PUE; no measured energy saving.','Forecast only: no control commands, switchgear/cooling setpoints, UPS/protection coordination or safety approvals.','AI assisted research prototype; offline only and human review required.']}
 save(ROOT,report,model)
if __name__=='__main__':main()
