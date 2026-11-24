"""VisionCal: real small neural net, calibration and corruption robustness."""
from pathlib import Path
import sys,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interdisciplinary_support import save,mlp_export,softmax,forward
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score,log_loss
ROOT=Path(__file__).resolve().parent

def metrics(y,p):
 conf=p.max(axis=1);pred=p.argmax(axis=1);correct=pred==y;ece=0
 for lo,hi in zip(np.linspace(0,1,11)[:-1],np.linspace(0,1,11)[1:]):
  mask=(conf>lo)&(conf<=hi)
  if mask.any():ece+=mask.mean()*abs(correct[mask].mean()-conf[mask].mean())
 mask=conf>=.9
 return {'accuracy':float(correct.mean()),'nll':float(log_loss(y,p,labels=np.arange(10))),'ece10':float(ece),'coverage90':float(mask.mean()),'selective_error90':float(1-correct[mask].mean()) if mask.any() else None}

def main():
 d=load_digits();X=d.data/16;y=d.target;ids=np.arange(len(y));tr,tmp=train_test_split(ids,test_size=.4,stratify=y,random_state=42);va,te=train_test_split(tmp,test_size=.5,stratify=y[tmp],random_state=43)
 logistic=LogisticRegression(C=1,max_iter=1000).fit(X[tr],y[tr])
 net=MLPClassifier(hidden_layer_sizes=(48,),activation='relu',alpha=.001,max_iter=350,random_state=42,early_stopping=False).fit(X[tr],y[tr])
 model=mlp_export(net,np.zeros(64),np.ones(64));model['input_domain']='8x8 pixels divided by16';model['classes']=list(range(10))
 val_logits=forward(X[va],model);temps=np.linspace(.5,3,51);temp=float(min(temps,key=lambda t:log_loss(y[va],softmax(val_logits,t),labels=np.arange(10))));model['temperature']=temp
 assert np.max(np.abs(softmax(forward(X[te],model))-net.predict_proba(X[te])))<1e-10
 rng=np.random.default_rng(700);noise=np.clip(X[te]+rng.normal(0,.25,X[te].shape),0,1);shift=np.roll(X[te].reshape(-1,8,8),1,axis=2);shift[:,:,0]=0;shift=shift.reshape(-1,64)
 rows=[];predictions=[];examples=[]
 for group,xx in [('clean',X[te]),('noise_sigma0.25',noise),('shift_right1px',shift)]:
  for name,p in [('logistic',logistic.predict_proba(xx)),('mlp_raw',net.predict_proba(xx)),('mlp_temperature',softmax(forward(xx,model),temp))]:
   rows.append({'group':group,'model':name,**metrics(y[te],p)})
   predictions += [{'group':group,'model':name,'row':int(i),'label':int(l),'probabilities':v.tolist()} for i,l,v in zip(te,y[te],p)]
  p=softmax(forward(xx,model),temp);wrong=np.where(p.argmax(axis=1)!=y[te])[0]
  chosen=list(wrong[:3])+list(range(3))
  for j in dict.fromkeys(chosen):examples.append({'group':group,'row':int(te[j]),'label':int(y[te[j]]),'input':xx[j].tolist(),'output':p[j].tolist()})
 report={'title':'VisionCal','protocol':'1797 public 8x8 images; fixed 60/20/20 stratified split. MLP trained only train; temperature minimizes validation NLL only; clean and corrupted test share held-out image IDs.',
 'source':'https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html','data_sha256':hashlib.sha256(d.data.tobytes()+y.tobytes()).hexdigest(),
 'split':{'train':tr.tolist(),'validation':va.tolist(),'test':te.tolist()},'temperature':temp,'loss_curve':net.loss_curve_,'iterations':int(net.n_iter_),
 'metrics':rows,'predictions':predictions,'examples':examples,
 'limits':['Not MNIST, CNN, foundation model or real OCR; small sklearn MLP.','Digits split has no writer IDs; writer leakage cannot be ruled out.','Temperature can improve NLL without raising accuracy; ECE bins arbitrary.','Corruptions are authored tests, not real deployment distribution.','Confidence0.9 is a fixed demo threshold, not a safety guarantee.','AI assisted; no prior personal research or production achievement implied.']}
 save(ROOT,report,model)
if __name__=='__main__':main()
