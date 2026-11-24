"""ChannelEst: missing-pilot handling and explicit LS validity, no retraining."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent
N=32;P=np.arange(0,N,4)
def synth(n,seed):
    r=np.random.default_rng(seed);power=np.exp(-np.arange(4)/2);power/=power.sum();h=(r.normal(size=(n,4))+1j*r.normal(size=(n,4)))*np.sqrt(power/2);H=np.fft.fft(h,n=N,axis=1);z=H[:,P]+(r.normal(size=(n,8))+1j*r.normal(size=(n,8)))*np.sqrt(.01/2);return H,z

def missing_ls(z,valid):
    if np.sum(valid)<4:raise ValueError('insufficient observed pilots for4-tap LS')
    F=np.exp(-2j*np.pi*np.arange(N)[:,None]*np.arange(4)[None,:]/N);a=F[P[valid]];h=np.linalg.lstsq(a,z[:,valid].T,rcond=None)[0].T;return h@F.T

def main():
    m=load(HERE/'artifacts/model.json');H,z=synth(160,98001);rows=[];cases=[]
    for missing in [0,1,2,4,6]:
        valid=np.ones(8,bool);valid[np.arange(missing)]=False;zz=z.copy();zz[:,~valid]=0;x=np.column_stack([zz.real,zz.imag]);pred=affine(x,m);learner=pred[:,:32]+1j*pred[:,32:]
        estimates={'zero_imputed_frozen':learner}
        if valid.sum()>=4:estimates['observed_pilot_ls']=missing_ls(z,valid)
        for name,est in estimates.items():
            nm=np.sum(abs(est-H)**2,axis=1)/np.sum(abs(H)**2,axis=1)
            for i in range(len(H)):rows.append(dict(model=name,condition=f'missing_{missing}',index=i,error=float(np.sqrt(nm[i])),nmse=float(nm[i]),observed_pilots=int(valid.sum()),valid=bool(valid.sum()>=4)))
        cases.append(dict(missing=missing,valid_indices=P[valid].tolist(),ls_status='fit' if valid.sum()>=4 else 'abstained_underdetermined'))
    save(HERE,'ChannelEst missing pilots & abstention','Frozen learned16→64 estimator vs observed-pilot4-tap least-squares;160 fresh channels at20dB and0/1/2/4/6 missing pilots. NMSE per frame; LS refuses fewer than4 measurements.',rows,['Zero-imputing unavailable pilots changes input distribution and may silently corrupt learning.','Four-tap LS has privileged model-order assumption; not universal best or a5G/6G product.','Metrics include NMSE; generic error column sqrt(NMSE) is not physical-unit MAE.'],extra=dict(cases=cases),sources=[HERE/'artifacts/model.json'])
if __name__=='__main__':main()
