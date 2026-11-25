"""Algorithm-specific interventions, head-only optimization and stochastic decoding."""
import copy,itertools
from .common import *

def tiny():
 folder='tiny-attention';p=PROJECTS/folder;protocol={'kind':'causal_counterfactual_interventions','seeds':[191001,191002,191003],'pairs':3,'n_per_seed':128,'interventions':['query_value_change','irrelevant_value_change'],'excludes_original_split_ids':True};freeze(folder,protocol)
 m=load(p/'artifacts/model.json');excluded=sum(load(p/'artifacts/results.json')['split_ids'].values(),[]);a=Attention(m);rows=[];metrics=[]
 for seed in protocol['seeds']:
  x,y=generate_lookup(128,seed,3,exclude=excluded);base=softmax(a.forward(x)[:,-1]);loc=np.argmax(x[:,:6:2]==x[:,-1,None],1)
  for kind in protocol['interventions']:
   xx=x.copy();j=loc if kind=='query_value_change' else (loc+1)%3;xx[np.arange(len(x)),2*j+1]=8+(xx[np.arange(len(x)),2*j+1]-8+1)%8;newy=8+(y-8+1)%8 if kind=='query_value_change' else y;probs=softmax(a.forward(xx)[:,-1]);kl=np.sum(base*np.log(np.maximum(base,1e-15)/np.maximum(probs,1e-15)),1)
   metrics.append(dict(seed=seed,intervention=kind,n=len(y),baseline_accuracy=float((base.argmax(1)==y).mean()),intervened_accuracy=float((probs.argmax(1)==newy).mean()),output_flip=float((base.argmax(1)!=probs.argmax(1)).mean()),mean_kl=float(kl.mean())))
   rows.extend(dict(seed=seed,id=i,intervention=kind,prefix=x[i].tolist(),counterfactual=xx[i].tolist(),target=int(newy[i]),before=base[i].tolist(),after=probs[i].tolist(),kl=float(kl[i])) for i in range(len(y)))
 return save(folder,'TinyAttention · 相关与无关信息的因果干预','改变被查询值和无关值，模型是否只对真正相关的信息做出响应？',rows,metrics,['直接修改输入值、按生成规则重算真值，是受控任务干预，不把attention权重当因果解释。','新前缀排除原训练/验证/测试ID；共享语法不等于自然语言泛化。','输出翻转不总是错误：相关值改变应翻转，无关值改变不应翻转。'],protocol,files=[Path(__file__),p/'artifacts/model.json',p/'artifacts/results.json'])

def lora():
 folder='lora-lab';p=PROJECTS/folder;protocol={'kind':'layer_factorial_ablation','layers':['q','v','head'],'all_8_subsets':True,'seeds':[192001,192002,192003],'n_per_seed':128,'no_retraining':True};freeze(folder,protocol)
 base=load(PROJECTS/'tiny-attention/artifacts/model.json');adapt=load(p/'artifacts/model.json');excluded=sum(load(p/'artifacts/results.json')['split_ids'].values(),[])+sum(load(PROJECTS/'tiny-attention/artifacts/results.json')['split_ids'].values(),[]);rows=[];metrics=[];singular={}
 for layer in protocol['layers']:
  A=np.array(adapt['adapter_state'][layer+'.A']);B=np.array(adapt['adapter_state'][layer+'.B']);sv=np.linalg.svd(B@A/A.shape[0],compute_uv=False);singular[layer]=sv.tolist()
 for bits in itertools.product([0,1],repeat=3):
  subset=[l for l,b in zip(protocol['layers'],bits) if b];m=copy.deepcopy(base)
  for l in subset:
   A=np.array(adapt['adapter_state'][l+'.A']);B=np.array(adapt['adapter_state'][l+'.B']);m['state'][l+'.weight']=(np.array(base['state'][l+'.weight'])+B@A/A.shape[0]).tolist()
  a=Attention(m)
  for seed in protocol['seeds']:
   x,old=generate_lookup(128,seed,3,exclude=excluded);new=8+(old-8+1)%8;prob=softmax(a.forward(x)[:,-1]);pred=prob.argmax(1)
   metrics.append(dict(subset='+'.join(subset) or 'base',seed=seed,n=len(old),old_accuracy=float((pred==old).mean()),new_accuracy=float((pred==new).mean())))
   rows.extend(dict(subset='+'.join(subset) or 'base',seed=seed,id=i,old_target=int(old[i]),new_target=int(new[i]),prediction=int(pred[i]),probabilities=prob[i].tolist()) for i in range(len(x)))
 return save(folder,'LoRA-Lab · 层级增量全因子消融','适配收益究竟来自query、value还是输出头？哪些组合破坏旧任务？',rows,metrics,['8种层组合全部报告，不在测试上选最佳子集。','低秩奇异值解释参数增量的有效秩，不证明通用语义结构。','从已训练adapter屏蔽层，不等于独立训练每个结构，因果范围限冻结权重干预。'],protocol,details={'singular_values':singular},files=[Path(__file__),p/'artifacts/model.json',PROJECTS/'tiny-attention/artifacts/model.json'])

def dpo():
 folder='dpo-lab';p=PROJECTS/folder;protocol={'kind':'new_numpy_head_only_DPO_training','seeds':[193001,193002,193003],'train':512,'validation':128,'test':192,'steps':160,'learning_rate':.02,'beta':[.1,.5],'policies':['sft','dpo_0.1','dpo_0.5'],'chosen_rule':'original+2','labels':'synthetic one-token preference; not human alignment','excluded_prior_ids':True};freeze(folder,protocol)
 base=load(PROJECTS/'tiny-attention/artifacts/model.json');W0=np.array(base['state']['head.weight']);b0=np.array(base['state']['head.bias']);excluded=sum(load(p/'artifacts/results.json')['split_ids'].values(),[])+sum(load(PROJECTS/'tiny-attention/artifacts/results.json')['split_ids'].values(),[]);rows=[];metrics=[];losses={};exports={}
 for seed in protocol['seeds']:
  x,rej=generate_lookup(832,seed,3,exclude=excluded);chosen=8+(rej-8+2)%8;h=hidden(x,base);ref=softmax(h@W0.T+b0);assert np.max(abs(ref-softmax(Attention(base).forward(x)[:,-1])))<1e-10
  train=np.arange(512);test=np.arange(640,832);ref_delta=np.log(ref[train,chosen[train]])-np.log(ref[train,rej[train]])
  for policy in protocol['policies']:
   W=W0.copy();b=b0.copy();curve=[]
   for step in range(protocol['steps']):
    pr=softmax(h[train]@W.T+b)
    if policy=='sft':
     grad=pr.copy();grad[np.arange(512),chosen[train]]-=1;grad/=512;loss=float(-np.log(np.maximum(pr[np.arange(512),chosen[train]],1e-15)).mean())
    else:
     beta=float(policy.split('_')[1]);delta=np.log(np.maximum(pr[np.arange(512),chosen[train]],1e-15))-np.log(np.maximum(pr[np.arange(512),rej[train]],1e-15));z=beta*(delta-ref_delta);sig=1/(1+np.exp(np.clip(z,-40,40)));coef=-beta*sig/512;grad=np.zeros_like(pr);grad[np.arange(512),chosen[train]]=coef;grad[np.arange(512),rej[train]]=-coef;loss=float(np.logaddexp(0,-z).mean())
    W-=.02*grad.T@h[train];b-=.02*grad.sum(0)
    if step%20==0 or step==159:curve.append({'step':step,'loss':loss})
   allp=softmax(h@W.T+b);val=np.arange(512,640);pred=allp[test].argmax(1);win=allp[test,chosen[test]]>allp[test,rej[test]];kl=np.sum(allp[test]*np.log(np.maximum(allp[test],1e-15)/np.maximum(ref[test],1e-15)),1)
   metrics.append(dict(seed=seed,policy=policy,n=len(test),validation_chosen=float((allp[val].argmax(1)==chosen[val]).mean()),test_pair_win=float(win.mean()),test_chosen_top1=float((pred==chosen[test]).mean()),original_retention=float((pred==rej[test]).mean()),mean_reference_kl=float(kl.mean())))
   rows.extend(dict(seed=seed,policy=policy,index=int(i),prefix=x[i].tolist(),chosen=int(chosen[i]),rejected=int(rej[i]),prediction=int(allp[i].argmax()),pair_win=bool(allp[i,chosen[i]]>allp[i,rej[i]]),probabilities=allp[i].tolist(),reference_probabilities=ref[i].tolist()) for i in test)
   losses[f'{seed}:{policy}']=curve;exports[f'{seed}:{policy}']={'weight':W.tolist(),'bias':b.tolist()}
 # New small train actually executed. Store inert head exports, not replace old policy.
 return save(folder,'DPO-Lab · 三种子真实偏好优化与SFT对照','偏好目标和单token正确率如何随真实训练变化，而非只做权重插值？',rows,metrics,['NumPy手工梯度真实训练输出头，基座冻结；DPO概率比reference固定。','三个新划分同时冻结，无测试选beta或训练步数。验证仅报告，不用于挑最佳。','偏好为合成+2规则，赢率、chosen top1、KL和原规则保留分开；不是人类对齐。'],protocol,details={'loss_curves':losses,'head_exports':exports},files=[Path(__file__),p/'artifacts/model.json',PROJECTS/'tiny-attention/artifacts/model.json'])

def moe():
 folder='moe-lab';p=PROJECTS/folder;protocol={'kind':'order_sensitive_capacity_stress','n':256,'seeds':[194001,194002,194003],'permutations':6,'capacity_factors':[.5,1],'policies':['drop','second'],'input':'same skewed batch restored to original IDs after routing'};freeze(folder,protocol)
 m=load(p/'artifacts/model.json');dispatch=module(folder).dispatch;rows=[];metrics=[]
 for seed in protocol['seeds']:
  rng=np.random.default_rng(seed);x=rng.uniform(-1,1,(256,2));x[:,0]=rng.uniform(.5,1,256);truth=np.sin(3*x[:,1])+.5*x[:,0]
  for cap in protocol['capacity_factors']:
   for policy in protocol['policies']:
    admitted_history=[]
    for repeat in range(6):
     perm=rng.permutation(256);out,route,kept,count,prob=dispatch(x[perm],m,cap,policy);inv=np.argsort(perm);out,route,kept=out[inv],route[inv],kept[inv];admitted_history.append(kept)
     metrics.append(dict(seed=seed,capacity=cap,policy=policy,order=repeat,n=256,coverage=float(kept.mean()),all_rmse=float(np.sqrt(np.mean((out-truth)**2))),admitted_rmse=float(np.sqrt(np.mean((out[kept]-truth[kept])**2))) if kept.any() else None))
     rows.extend(dict(seed=seed,capacity=cap,policy=policy,order=repeat,id=i,admitted=bool(kept[i]),route=int(route[i]),error=float(out[i]-truth[i])) for i in range(256))
    matrix=np.array(admitted_history);metrics.append(dict(seed=seed,capacity=cap,policy=policy,order='aggregate',n=256,coverage=float(matrix.mean()),all_rmse=None,admitted_rmse=None,always_admitted=float(matrix.all(0).mean()),never_admitted=float((~matrix).all(0).mean())))
 return save(folder,'SparseMoE · 输入顺序与容量公平性','同一批输入仅改变排队顺序，哪些样本会持续被丢弃？',rows,metrics,['同批6排列是相关变体，非新增独立数据。','均值接收率不表明每样本公平，always/never-admitted公开。','本地CPU分发不是GPU AllToAll吞吐，不能报告生产加速。'],protocol,files=[Path(__file__),p/'depth.py',p/'artifacts/model.json'])

def acceptance_distribution(p,q):
 accept=np.minimum(p,q);residual=np.maximum(p-q,0);mass=float(residual.sum());return accept+(mass*residual/mass if mass>1e-14 else 0),float(accept.sum())

def stochastic_step(target,draft,prefix,rng):
 p=softmax(target.forward(prefix)[0,-1]);q=softmax(draft.forward(prefix)[0,-1]);proposal=int(rng.choice(len(q),p=q));accepted=rng.random()<min(1,float(p[proposal]/q[proposal]))
 if accepted:return proposal,True
 residual=np.maximum(p-q,0);residual/=residual.sum();return int(rng.choice(len(p),p=residual)),False

def spec():
 folder='spec-decode';p=PROJECTS/folder;protocol={'kind':'distribution_correct_single_proposal_sampling','contexts':16,'empirical_samples_per_context':1000,'seed':195001,'temperature':1,'multi_token_block':False,'analytical_identity':True};freeze(folder,protocol)
 m=load(p/'artifacts/model.json');target=Attention(m['target']);draft=Attention(m['draft']);rng=np.random.default_rng(195001);prefixes=rng.integers(0,8,(16,4));rows=[];metrics=[]
 for i,prefix in enumerate(prefixes):
  pp=softmax(target.forward(prefix)[0,-1]);qq=softmax(draft.forward(prefix)[0,-1]);analytic,accept=acceptance_distribution(pp,qq);counts=np.zeros(18,int);acc=0
  # Cached distributions perform actual rejection/correction sampling without rerunning identical logits.
  for sample in range(1000):
   proposal=int(rng.choice(18,p=qq));yes=rng.random()<min(1,float(pp[proposal]/qq[proposal]));acc+=yes
   if yes:token=proposal
   else:res=np.maximum(pp-qq,0);token=int(rng.choice(18,p=res/res.sum()))
   counts[token]+=1
  empirical=counts/1000;metrics.append(dict(context=i,n=1000,analytic_max_error=float(np.max(abs(analytic-pp))),theoretical_acceptance=accept,observed_acceptance=acc/1000,total_variation=float(.5*abs(empirical-pp).sum())))
  rows.append(dict(context=i,prefix=prefix.tolist(),target_probabilities=pp.tolist(),draft_probabilities=qq.tolist(),analytic_probabilities=analytic.tolist(),empirical_counts=counts.tolist()))
 # Sequential 4-token samples use state-dependent fresh distributions, recorded separately.
 trajectories=[]
 for i in range(64):
  seq=prefixes[i%16].tolist();accepted=[]
  for step in range(4):token,yes=stochastic_step(target,draft,seq,rng);seq.append(token);accepted.append(yes)
  trajectories.append({'prefix':prefixes[i%16].tolist(),'output':seq[4:],'accepted':accepted})
 return save(folder,'SpecDecode · 分布正确的拒绝采样与修正','greedy一致性之外，随机草稿接受/修正能否保持目标token分布？',rows,metrics,['公式min(p,q)+正残差逐token精确恢复p，分析误差与经验总变差分别报告。','单草稿token机制，不是多token并行验证，不宣称加速。','1000抽样只检验有限上下文，经验偏差来自采样；64四token轨迹不证明全语言分布。'],protocol,details={'sequential_samples':trajectories},files=[Path(__file__),p/'artifacts/model.json'])
