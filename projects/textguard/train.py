"""Real train/validation/test TF-IDF logistic model; raw texts stay private."""
import hashlib,json,re,time,urllib.request,zipfile,io
from pathlib import Path
from collections import Counter
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split,StratifiedKFold,cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.metrics import confusion_matrix,precision_score,recall_score,f1_score,roc_auc_score,brier_score_loss
ROOT=Path(__file__).resolve().parent
SOURCE='https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip'
def normalize(t):
 if not isinstance(t,str):raise ValueError('text required')
 t=t.lower();t=re.sub(r'https?://\S+|www\.\S+',' urltoken ',t);t=re.sub(r'\S+@\S+',' emailtoken ',t);t=re.sub(r'\d+',' numbertoken ',t)
 return ' '.join(re.findall('[a-z]+',t))
def infer(t,m):
 words=normalize(t).split();terms=Counter(words+[' '.join(words[i:i+2]) for i in range(len(words)-1)])
 v={m['vocabulary'][t]:c*m['idf'][m['vocabulary'][t]] for t,c in terms.items() if t in m['vocabulary']};norm=sum(x*x for x in v.values())**.5
 z=m['intercept']+sum(x/norm*m['coef'][i] for i,x in v.items()) if norm else m['intercept'];p=1/(1+np.exp(-z))
 return {'probability':float(p),'decision':'spam' if p>=m['threshold'] else 'ham','known_terms':len(v),'review':not v or abs(float(p)-m['threshold'])<.15}
def metric(y,p,t=.5):
 pred=(np.asarray(p)>=t).astype(int)
 return {'precision':float(precision_score(y,pred,zero_division=0)),'recall':float(recall_score(y,pred,zero_division=0)),'f1':float(f1_score(y,pred,zero_division=0)),'roc_auc':float(roc_auc_score(y,p)),'brier':float(brier_score_loss(y,p)),'confusion_matrix':confusion_matrix(y,pred).tolist()}
def main():
 private=ROOT/'private';private.mkdir(exist_ok=True);path=private/'sms.zip'
 if not path.exists():path.write_bytes(urllib.request.urlopen(SOURCE,timeout=45).read())
 raw=path.read_bytes();content=zipfile.ZipFile(io.BytesIO(raw)).read('SMSSpamCollection').decode('utf-8');records={};conflicts=set();n=0
 for line in content.splitlines():
  lab,t=line.split('\t',1);n+=1;t=normalize(t);y=int(lab=='spam')
  if t in records and records[t]!=y:conflicts.add(t)
  records[t]=y
 for t in conflicts:records.pop(t)
 X=np.array(list(records));y=np.array(list(records.values()));idx=np.arange(len(y))
 tr,tmp=train_test_split(idx,test_size=.4,stratify=y,random_state=42);va,te=train_test_split(tmp,test_size=.5,stratify=y[tmp],random_state=43)
 v=TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=18000,token_pattern=r'(?u)\b[a-z]+\b');a=v.fit_transform(X[tr]);b=v.transform(X[va]);c=v.transform(X[te])
 start=time.perf_counter();lr=LogisticRegression(C=4,class_weight='balanced',max_iter=1000,random_state=42).fit(a,y[tr])
 thresholds=[float(x) for x in np.linspace(.1,.9,33)];pval=lr.predict_proba(b)[:,1]
 threshold=max(thresholds,key=lambda t:(metric(y[va],pval,t)['f1'],-abs(t-.5)))
 models={'majority':None,'multinomial_nb':MultinomialNB().fit(a,y[tr]),'tfidf_logistic':lr};results=[];predictions=[]
 for name,m in models.items():
  p=np.full(len(te),y[tr].mean()) if m is None else m.predict_proba(c)[:,1];t=threshold if name=='tfidf_logistic' else .5
  results.append({'model':name,'threshold':t,'test':metric(y[te],p,t)})
  predictions += [{'model':name,'id':hashlib.sha256(X[i].encode()).hexdigest(),'label':int(y[i]),'probability':float(prob),'prediction':int(prob>=t)} for i,prob in zip(te,p)]
 model={'kind':'tfidf_logistic_v1','vocabulary':{k:int(i) for k,i in v.vocabulary_.items()},'idf':v.idf_.tolist(),'coef':lr.coef_[0].tolist(),'intercept':float(lr.intercept_[0]),'threshold':threshold}
 # Exported inference is checked against the trained estimator on every held-out example.
 parity=max(abs(infer(str(X[i]),model)['probability']-float(p)) for i,p in zip(te,lr.predict_proba(c)[:,1]))
 assert parity<1e-10
 cv=cross_val_score(make_pipeline(TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=18000,token_pattern=r'(?u)\b[a-z]+\b'),LogisticRegression(C=4,class_weight='balanced',max_iter=1000,random_state=42)),X[tr],y[tr],cv=StratifiedKFold(3,shuffle=True,random_state=7),scoring='f1')
 out=ROOT/'artifacts';out.mkdir(exist_ok=True);(out/'model.json').write_text(json.dumps(model))
 probes=['We will meet at the library tomorrow','Claim your free prize now call this number','This lecture explains free software licensing','Please send the project report','你好明天开会','qwerty zxvbnm']
 split=lambda ids:[{'id':hashlib.sha256(X[i].encode()).hexdigest(),'label':int(y[i])} for i in ids]
 report={'project':'TextGuard','status':'trained_local_model','sklearn':sklearn.__version__,'source':SOURCE,'source_sha256':hashlib.sha256(raw).hexdigest(),'source_rows':n,'deduplicated_rows':len(y),'conflicts_removed':len(conflicts),
 'split':{'train':split(tr),'validation':split(va),'test':split(te)},'threshold_selection':'validation F1 only; test not used for tuning','validation':metric(y[va],pval,threshold),'train_cv_f1':cv.tolist(),
 'test_results':results,'predictions':predictions,'export_parity_max_error':parity,'training_ms':(time.perf_counter()-start)*1000,
 'examples':[{'text':t,**infer(t,model)} for t in probes], 'failure_ids':[r['id'] for r in predictions if r['model']=='tfidf_logistic' and r['label']!=r['prediction']],
 'limits':['old English SMS dataset, no current phishing claims','exact dedup cannot remove every semantic duplicate','probabilities uncalibrated','no raw SMS redistributed','unknown/Chinese input needs manual review']}
 (out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(out/'checksums.json').write_text(json.dumps({n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ('model.json','results.json')},indent=2))
 lines=['# TextGuard 实测','',f'解析 {n} 条；规范化去重 {len(y)} 条。训练/验证/测试 {len(tr)}/{len(va)}/{len(te)}。阈值仅验证集选择，词表仅训练集拟合。','', '|模型|Precision|Recall|F1|ROC-AUC|Brier|','|---|---:|---:|---:|---:|---:|']
 for r in results:
  m=r['test'];lines.append('|'+r['model']+'|'+ '|'.join(f"{m[k]:.4f}" for k in ['precision','recall','f1','roc_auc','brier'])+'|')
 lines += ['',f'导出推理最大误差 {parity:.2e}；误判数 {len(report["failure_ids"])}。仅记录哈希，不公开原短信。','[全部结果](results.json) · [模型参数](model.json) · [完整性](checksums.json)','旧英文研究数据不代表现代诈骗识别能力；未做真实用户验证。']
 (out/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps(results,indent=2))
if __name__=='__main__':main()
