"""Real numerical novelty models; Wine classes define artificial distribution shift."""
from pathlib import Path
import hashlib,json
import numpy as np
import sklearn
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.metrics import roc_auc_score,average_precision_score,precision_score,recall_score,f1_score,confusion_matrix
ROOT=Path(__file__).resolve().parent

def infer(values,m):
 x=np.asarray(values,dtype=float)
 if x.shape!=(13,) or not np.isfinite(x).all():raise ValueError('exactly 13 finite numeric features required')
 z=(x-m['mean'])/m['scale'];s=float(np.linalg.norm(z-m['center']))
 return {'score':s,'threshold':m['threshold'],'novel':s>m['threshold'],'top_features':np.argsort(np.abs(z))[-3:][::-1].tolist()}

def main():
 d=load_wine();X=d.data;y=d.target;norm=np.where(y==0)[0];shift=np.where(y!=0)[0]
 tr,tmp=train_test_split(norm,test_size=.4,random_state=42);va,tn=train_test_split(tmp,test_size=.5,random_state=43);te=np.concatenate([tn,shift]);truth=(y[te]!=0).astype(int)
 scaler=StandardScaler().fit(X[tr]);a=scaler.transform(X[tr]);b=scaler.transform(X[va]);c=scaler.transform(X[te]);center=a.mean(axis=0)
 models={'centroid_distance':None,'isolation_forest':IsolationForest(n_estimators=128,random_state=42,n_jobs=1).fit(a),'one_class_svm':OneClassSVM(nu=.05,gamma='scale').fit(a)}
 results=[];predictions=[];thresholds={}
 for name,m in models.items():
  s=np.linalg.norm(c-center,axis=1) if m is None else -m.score_samples(c);v=np.linalg.norm(b-center,axis=1) if m is None else -m.score_samples(b);threshold=float(np.quantile(v,.95));thresholds[name]=threshold;p=(s>threshold).astype(int)
  metric={'roc_auc':float(roc_auc_score(truth,s)),'average_precision':float(average_precision_score(truth,s)),'precision':float(precision_score(truth,p,zero_division=0)),'recall':float(recall_score(truth,p,zero_division=0)),'f1':float(f1_score(truth,p,zero_division=0)),'false_positive_rate':float(p[truth==0].mean()),'confusion_matrix':confusion_matrix(truth,p).tolist()}
  results.append({'model':name,'threshold':threshold,'test':metric});predictions += [{'model':name,'row':int(i),'label':int(t),'score':float(sv),'prediction':int(sv>threshold)} for i,t,sv in zip(te,truth,s)]
 m={'kind':'standardized_centroid_novelty','mean':scaler.mean_.tolist(),'scale':scaler.scale_.tolist(),'center':center.tolist(),'threshold':thresholds['centroid_distance'],'feature_names':d.feature_names}
 out=ROOT/'artifacts';out.mkdir(exist_ok=True);(out/'model.json').write_text(json.dumps(m,indent=2))
 report={'project':'NoveltyLab','status':'fitted_local_models','sklearn':sklearn.__version__,'source':'https://archive.ics.uci.edu/dataset/109/wine','data_sha256':hashlib.sha256(X.tobytes()+y.tobytes()).hexdigest(),
 'protocol':'normal=class0; shifted=class1/2. Fit scaler/model ONLY normal train; threshold ONLY normal validation 95th percentile.',
 'split':{'train':tr.tolist(),'validation':va.tolist(),'test':te.tolist()},'default_model_chosen':'centroid_distance fixed before test; not best-test selection',
 'results':results,'predictions':predictions,'examples':[{'row':int(i),'actual_class':int(y[i]),'values':X[i].tolist(),**infer(X[i],m)} for i in np.concatenate([tn[:5],shift[:5]])],
 'limits':['178-row classic benchmark, easy class separation','class shift is not real anomaly ground truth','not industrial fault/fraud detector','small normal validation/test causes uncertainty','score not calibrated probability']}
 (out/'results.json').write_text(json.dumps(report,indent=2));(out/'checksums.json').write_text(json.dumps({n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['model.json','results.json']},indent=2))
 lines=['# NoveltyLab 实测','',f'178 行 13 维；正常训练/验证/测试 {len(tr)}/{len(va)}/{len(tn)}，未知类别测试 {len(shift)}。类别迁移不等于故障标签。','', '|模型|ROC-AUC|PR-AUC|Precision|Recall|正常误报率|','|---|---:|---:|---:|---:|---:|']
 for r in results:
  mm=r['test'];lines.append('|'+r['model']+'|'+'|'.join(f"{mm[k]:.4f}" for k in ['roc_auc','average_precision','precision','recall','false_positive_rate'])+'|')
 lines+=['','默认模型预先固定，不按测试最高分选择。高分不等于工业异常检测效果。','[全部结果](results.json) · [部署参数](model.json) · [完整性](checksums.json)'];(out/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps(results,indent=2))
if __name__=='__main__':main()
