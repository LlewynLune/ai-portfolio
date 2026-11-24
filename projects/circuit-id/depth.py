"""CircuitID: nuisance-aware physics fit (gain/offset) vs prior fixed-unit fit and frozen learner."""
from pathlib import Path
import sys
from scipy.optimize import minimize_scalar
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
TIME=np.linspace(0,10,32)
def fit_curve(v,nuisance=True):
    def evaluate(logtau,return_params=False):
        curve=1-np.exp(-TIME/np.exp(logtau))
        if nuisance:
            design=np.column_stack([curve,np.ones(len(curve))]);theta=np.linalg.lstsq(design,v,rcond=None)[0];pred=design@theta
        else:theta=np.array([1.,0.]);pred=curve
        loss=float(np.mean((pred-v)**2));return (loss,theta) if return_params else loss
    z=minimize_scalar(evaluate,bounds=(np.log(.1),np.log(12)),method='bounded');loss,theta=evaluate(z.x,True);return float(np.exp(z.x)),theta.tolist(),loss

def main():
    m=load(HERE/'artifacts/model.json');rows=[];fits=[]
    for group,gain,offset in [('unit',1,0),('gain_shift',.75,0),('offset_shift',1,.15),('combined',.75,.15)]:
        rng=np.random.default_rng(97001);tau=rng.uniform(.5,6,100);x=gain*(1-np.exp(-TIME[None,:]/tau[:,None]))+offset+rng.normal(0,.02,(100,32));learn=np.exp(affine(x,m).reshape(-1))
        for i in range(100):
            a,theta,res=fit_curve(x[i],True);b,_,_=fit_curve(x[i],False)
            for name,pred in [('frozen_ridge',learn[i]),('unit_physics',b),('nuisance_physics',a)]:rows.append(dict(model=name,condition=group,index=i,truth=float(tau[i]),prediction=float(pred),error=float(pred-tau[i])))
            if i<4:fits.append(dict(condition=group,index=i,time_ms=TIME.tolist(),input=x[i].tolist(),tau=float(tau[i]),fit_tau=a,gain=theta[0],offset=theta[1],residual=res))
    save(HERE,'CircuitID gain/offset-aware physical inference','400 fresh32-point simulated step curves, tau0.5–6ms, unit/gain/offset/combined stress. Variable-projection fit estimates gain/offset at each tau; compare frozen Ridge and old unit physics.',rows,['Nuisance fitting addresses a missing assumption but can be ill-conditioned at long tau or weak signal.','Only tau=RC identifiable; fitted gain and offset are numerical nuisance terms, not measured devices.','No equipment control, hardware validation or electrical tolerance guarantee.'],extra=dict(fits=fits),sources=[HERE/'artifacts/model.json'])
if __name__=='__main__':main()
