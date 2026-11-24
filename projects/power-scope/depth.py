"""PowerScope: prediction-only interval coverage and rolling error blocks; never device control."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
def main():
    old=load(HERE/'artifacts/results.json');m=load(HERE/'artifacts/model.json');rows=[];windows=[];curves=[]
    for group in ['chronological_test','cooling_drift_ood']:
        rr=[r for r in old['predictions'] if r['group']==group and r['model']=='ridge_full'];rr.sort(key=lambda r:r['time_index'])
        q=m['interval_abs_kw']
        for i,r in enumerate(rr):
            err=r['forecast_kw']-r['actual_kw'];rows.append(dict(model='frozen_ridge',condition=group,index=r['time_index'],truth=r['actual_kw'],prediction=r['forecast_kw'],error=err,covered=abs(err)<=q))
        for factor in [.5,1,1.5,2,3]:
            covered=sum(abs(r['forecast_kw']-r['actual_kw'])<=q*factor for r in rr);curves.append(dict(condition=group,interval_scale=factor,coverage=covered/len(rr),mean_width_kw=2*q*factor,n=len(rr)))
        for start in range(0,len(rr),288):
            block=rr[start:start+288];errs=np.array([r['forecast_kw']-r['actual_kw'] for r in block]);windows.append(dict(condition=group,start_index=block[0]['time_index'],n=len(block),mae=float(abs(errs).mean()),rmse=float(np.sqrt(np.mean(errs**2))),bias=float(errs.mean()),coverage=float((abs(errs)<=q).mean())))
    ex=old['examples'][0]['input'];contribution=((np.array(ex)-m['mean'])/m['scale'])*np.array(m['weights'])[0]
    save(HERE,'PowerScope rolling error & interval failure','Read-only reanalysis of frozen chronological and drift forecasts; daily288-point blocks, residual coverage vs width; no recalibration on test or model retraining. Counterfactual contributions from frozen linear weights.',rows,['Interval width / coverage trade-off is descriptive and not a certified protection margin.','Chronological residual dependence prevents independent-example binomial guarantees.','Drift cannot be fixed by silently widening an interval; bias, MAE and tail error stay visible.'],extra=dict(windows=windows,interval_curves=curves,linear_contributions=dict(features=m['features'],values=contribution.tolist(),sum_plus_bias=float(contribution.sum()+m['bias'][0]))),sources=[HERE/'artifacts/results.json',HERE/'artifacts/model.json'])
if __name__=='__main__':main()
