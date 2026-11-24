"""ChannelEst: learned linear channel estimator vs interpolation and prior-aware LMMSE."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interdisciplinary_support import save,linear_export,forward
import numpy as np
from sklearn.linear_model import Ridge
ROOT=Path(__file__).resolve().parent
N=32;PILOTS=np.arange(0,N,4);DATA=np.array([k for k in range(N) if k not in PILOTS])

def generate(n,seed,snr_db=15,taps=4):
 r=np.random.default_rng(seed);power=np.exp(-np.arange(taps)/2);power/=power.sum()
 h=(r.normal(size=(n,taps))+1j*r.normal(size=(n,taps)))*np.sqrt(power/2)
 H=np.fft.fft(h,n=N,axis=1);bits=r.integers(0,2,(n,N,2));s=((2*bits[:,:,0]-1)+1j*(2*bits[:,:,1]-1))/np.sqrt(2);s[:,PILOTS]=1
 noise_var=10**(-snr_db/10);w=(r.normal(size=(n,N))+1j*r.normal(size=(n,N)))*np.sqrt(noise_var/2);Y=H*s+w
 Z=Y[:,PILOTS];X=np.concatenate([Z.real,Z.imag],axis=1);target=np.concatenate([H.real,H.imag],axis=1)
 return X,target,H,Y,s,bits,noise_var

def complex_output(a):return a[:,:N]+1j*a[:,N:]
def interpolation(x):
 z=x[:,:len(PILOTS)]+1j*x[:,len(PILOTS):];out=[]
 # Circular endpoint treats frequency response as periodic.
 for v in z:
  xx=np.append(PILOTS,N);vv=np.append(v,v[0]);out.append(np.interp(np.arange(N),xx,vv.real)+1j*np.interp(np.arange(N),xx,vv.imag))
 return np.array(out)
def lmmse(x,noise_var,taps=4):
 power=np.exp(-np.arange(taps)/2);power/=power.sum();F=np.exp(-2j*np.pi*np.arange(N)[:,None]*np.arange(taps)[None,:]/N);R=(F*power)@F.conj().T
 W=np.linalg.solve(R[np.ix_(PILOTS,PILOTS)]+noise_var*np.eye(len(PILOTS)),R[:,PILOTS].conj().T).conj().T
 z=x[:,:len(PILOTS)]+1j*x[:,len(PILOTS):];return z@W.T

def score(H,est,Y,bits):
 nmse=np.sum(abs(H-est)**2,axis=1)/np.sum(abs(H)**2,axis=1)
 # ZF-like equalizer with fixed numerical regularizer; no coding or CFO.
 eq=Y[:,DATA]*est[:,DATA].conj()/(abs(est[:,DATA])**2+1e-6)
 pred=np.stack([eq.real>0,eq.imag>0],axis=-1);error=np.sum(pred!=bits[:,DATA],axis=(1,2));total=len(DATA)*2
 return nmse,error,total

def main():
 train=[generate(1200,10+i,s) for i,s in enumerate([5,15,25])];X=np.concatenate([v[0] for v in train]);target=np.concatenate([v[1] for v in train]);val=generate(600,20,15)
 candidates=[Ridge(alpha=a).fit(X,target) for a in [.01,1,10,100]];est=min(candidates,key=lambda m:np.mean((m.predict(val[0])-val[1])**2));model=linear_export(est,np.zeros(X.shape[1]),np.ones(X.shape[1]))
 model.update({'selected':'learned_ridge','pilot_indices':PILOTS.tolist(),'subcarriers':N,'input_format':'pilot real then imaginary, known unit pilot','alpha':float(est.alpha)})
 rows=[];predictions=[];examples=[]
 for group,snr,taps in [('snr5',5,4),('snr15',15,4),('snr25',25,4),('long_delay_ood',15,10)]:
  for seed in [31,32,33]:
   x,_,H,Y,s,bits,nv=generate(220,seed,snr,taps)
   estimates={'linear_interpolation':interpolation(x),'learned_ridge':complex_output(est.predict(x)), 'known_prior_lmmse4':lmmse(x,nv,4),'perfect_CSI_oracle':H}
   for name,h in estimates.items():
    nmse,err,total=score(H,h,Y,bits);rows.append({'group':group,'seed':seed,'model':name,'nmse':float(nmse.mean()),'ber':float(err.sum()/(len(err)*total)),'bit_errors':int(err.sum()),'bits':len(err)*total})
    predictions.extend({'group':group,'seed':seed,'frame':i,'model':name,'nmse':float(nm),'bit_errors':int(e),'bits':total} for i,(nm,e) in enumerate(zip(nmse,err)))
   if seed==31:
    h=estimates['learned_ridge'];nm,_,_=score(H,h,Y,bits)
    for i in dict.fromkeys([0,int(np.argmax(nm))]):examples.append({'group':group,'snr_db':snr,'true_taps':taps,'input':x[i].tolist(),'truth_real':H[i].real.tolist(),'truth_imag':H[i].imag.tolist(),'output':np.concatenate([h[i].real,h[i].imag]).tolist()})
 assert np.max(abs(forward(val[0],model)-est.predict(val[0])))<1e-10
 report={'title':'ChannelEst','protocol':'Ideal frequency-domain OFDM-equivalent:32 subcarriers,8 unit pilots,24 QPSK data tones; AWGN complex variance=10^(-SNR/10), block-static channel. Train3600 frames at5/15/25dB, validation600 at15dB. Test4groups x3seeds x220 paired frames.',
 'source':'https://wirelesspi.com/channel-estimation-in-ofdm-systems/','split':{'train_seeds':[10,11,12],'validation_seed':20,'test_seeds':[31,32,33]},
 'metrics':rows,'predictions':predictions,'examples':examples,'selected_alpha':float(est.alpha),
 'limits':['Frequency-domain idealization; no actual radio, antenna, SDR, CP timing/CFO/ICI/channel coding simulation.','Known_prior_lmmse4 receives true noise variance and assumed4-tap prior; privileged comparator, not a learned method.','Perfect CSI is an oracle upper reference; noise still causes bit errors.','Training/test taps from authored exponential power profile; not standardized3GPP channels.','10-tap OOD violates training prior and pilot alias constraints; learned method can fail.','No claim of5G/6G product or original algorithm. AI assisted independent learning implementation.']}
 save(ROOT,report,model)
if __name__=='__main__':main()
