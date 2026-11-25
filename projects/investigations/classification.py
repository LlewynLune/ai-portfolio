"""Classification: prior shift, train-only covariance and validation conformal sets."""
from .common import *

def textguard():
 folder='textguard';p=PROJECTS/folder;protocol={'kind':'frozen_test_prediction_reweighting','target_prevalences':[.01,.05,.12,.3,.5],'assumption':'label shift p(x|y) unchanged; target prior is given, not estimated','threshold':'original validation-chosen threshold frozen','records_not_new_examples':True};freeze(folder,protocol)
 old=load(p/'artifacts/results.json');m=load(p/'artifacts/model.json');trainprior=next(r['probability'] for r in old['predictions'] if r['model']=='majority');rows=[];metrics=[]
 for target in protocol['target_prevalences']:
  for model in ['majority','multinomial_nb','tfidf_logistic']:
   rr=[r for r in old['predictions'] if r['model']==model]
   if not rr:continue
   y=np.array([r['label'] for r in rr]);prob=np.array([r['probability'] for r in rr]);testprior=float(y.mean());weight=np.where(y==1,target/testprior,(1-target)/(1-testprior));weight/=weight.sum()
   for mode in ['unchanged','prior_odds_adjusted']:
    pr=np.clip(prob,1e-9,1-1e-9)
    if mode=='prior_odds_adjusted':odds=pr/(1-pr)*(target/(1-target))/(trainprior/(1-trainprior));pr=odds/(1+odds)
    threshold=m['threshold'] if model=='tfidf_logistic' else .5;pred=pr>=threshold
    tp=float(weight[(y==1)&pred].sum());fp=float(weight[(y==0)&pred].sum());fn=float(weight[(y==1)&~pred].sum());tn=float(weight[(y==0)&~pred].sum());precision=tp/(tp+fp) if tp+fp else None;recall=tp/(tp+fn) if tp+fn else None
    metrics.append(dict(model=model,mode=mode,target_prior=target,n=len(rr),precision=precision,recall=recall,weighted_error=fp+fn,weighted_brier=float(np.sum(weight*(pr-y)**2)),weighted_nll=float(-np.sum(weight*np.log(np.where(y,pr,1-pr))))))
    rows.extend(dict(id=r['id'],model=model,mode=mode,target_prior=target,label=int(y[i]),original_probability=float(prob[i]),adjusted_probability=float(pr[i]),weight=float(weight[i]),prediction=int(pred[i])) for i,r in enumerate(rr))
 return save(folder,'TextGuard · 部署先验变化与误报成本','低发生率部署下，旧测试准确率是否掩盖精确率失效？',rows,metrics,['这是原测试预测的假设性重加权，不是新用户或真实部署数据。','先验校正依赖标签条件分布不变，不能纠正新词汇/语言/诈骗概念漂移。','测试重加权结果不用于重新选择阈值；全部目标先验同时报告。'],protocol,files=[Path(__file__),p/'artifacts/results.json',p/'artifacts/model.json'])

def novelty():
 from sklearn.datasets import load_wine
 folder='novelty-lab';p=PROJECTS/folder;protocol={'kind':'train_only_shrinkage_mahalanobis_baseline','shrinkage':[.1,.5,1.0],'threshold':'95th quantile of 12 normal validation rows, descriptive due tiny calibration','data':'same public Wine test IDs; class0 normal, other classes constructed shift','no_test_selection':True};freeze(folder,protocol)
 m=load(p/'artifacts/model.json');old=load(p/'artifacts/results.json');d=load_wine();tr=np.array(old['split']['train']);va=np.array(old['split']['validation']);te=np.array(old['split']['test']);z=(d.data-m['mean'])/m['scale'];center=z[tr].mean(0);cov=np.cov(z[tr].T);rows=[];metrics=[]
 for lam in protocol['shrinkage']:
  C=(1-lam)*cov+lam*np.eye(13)*np.trace(cov)/13;precision=np.linalg.inv(C);s=np.sqrt(np.maximum(np.einsum('ni,ij,nj->n',z-center,precision,z-center),0));threshold=float(np.quantile(s[va],.95));y=d.target[te]!=0;pred=s[te]>threshold
  metrics.append(dict(shrinkage=lam,n=len(te),condition_number=float(np.linalg.cond(C)),threshold=threshold,normal_false_positive=float(pred[~y].mean()),shift_detection=float(pred[y].mean()),accuracy=float((pred==y).mean())))
  rows+= [dict(id=int(i),shrinkage=lam,label=int(d.target[i]!=0),score=float(s[i]),prediction=int(s[i]>threshold),threshold=threshold) for i in te]
 return save(folder,'NoveltyLab · 相关特征与收缩协方差','忽略特征相关性的中心距离，和只在正常训练拟合的协方差基线有什么差异？',rows,metrics,['协方差只拟合35条正常训练，13维估计不稳定，condition number必须报告。','12条正常验证不足以支持高置信误报保证；95%经验分位数非认证。','Wine类别人为异常定义不能外推工业故障。'],protocol,files=[Path(__file__),p/'artifacts/model.json',p/'artifacts/results.json'])

def vision():
 from sklearn.datasets import load_digits
 folder='vision-cal';p=PROJECTS/folder;protocol={'kind':'validation_split_conformal_prediction_sets','alpha':[.05,.1,.2],'score':'1-p_true with finite-sample ceil((n+1)*(1-alpha)) rank','frozen_validation':359,'corruptions':['clean','gaussian_0.2','translation_1'],'seed':190901,'labels_not_used_for_test_sets':True};freeze(folder,protocol)
 m=load(p/'artifacts/model.json');old=load(p/'artifacts/results.json');d=load_digits();va=np.array(old['split']['validation']);te=np.array(old['split']['test']);cal=softmax(affine(d.data[va]/16,m)/m['temperature']);scores=1-cal[np.arange(len(va)),d.target[va]]
 x=d.data[te]/16;y=d.target[te];rng=np.random.default_rng(protocol['seed']);shift=np.roll(x.reshape(-1,8,8),1,2);shift[:,:,0]=0;conditions=[('clean',x),('gaussian_0.2',np.clip(x+rng.normal(0,.2,x.shape),0,1)),('translation_1',shift.reshape(-1,64))];rows=[];metrics=[]
 for alpha in protocol['alpha']:
  q,rank=finite_quantile(scores,alpha)
  for cond,xx in conditions:
   probs=softmax(affine(xx,m)/m['temperature']);sets=1-probs<=q;sizes=sets.sum(1);covered=sets[np.arange(len(y)),y]
   metrics.append(dict(condition=cond,alpha=alpha,n=len(y),quantile_rank=rank,threshold=q,coverage=float(covered.mean()),mean_set_size=float(sizes.mean()),singleton_rate=float((sizes==1).mean()),empty_rate=float((sizes==0).mean())))
   rows += [dict(id=int(te[i]),condition=cond,alpha=alpha,label=int(y[i]),probabilities=probs[i].tolist(),prediction_set=np.flatnonzero(sets[i]).tolist(),covered=bool(covered[i])) for i in range(len(y))]
 return save(folder,'VisionCal · 留出校准的预测集合与失效','不在测试上挑置信门槛，预测集合在干净和迁移图像上还能覆盖真值吗？',rows,metrics,['分位数仅从原验证集冻结，测试不选alpha或温度。','交换性是覆盖理论条件；噪声/平移迁移破坏它，不能用名义水平保证OOD。','集合大小、空集与单例一起报告，不用扩大集合隐藏低效。'],protocol,files=[Path(__file__),p/'artifacts/model.json',p/'artifacts/results.json'])
