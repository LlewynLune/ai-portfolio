"""A real small conditional autoregressive MLP, supervised warm-start + RL update.
No transformer/LLM weight claims. Shared 4-symbol task, sampled sequential actions.
"""
import numpy as np,hashlib,json
ACTIONS=4;FEATURES=13

def softmax(z):
 e=np.exp(z-z.max(axis=-1,keepdims=True));return e/e.sum(axis=-1,keepdims=True)
def features(prompt,pos,previous):
 v=np.zeros(FEATURES);v[int(prompt[pos])]=1;v[4+int(previous)]=1;v[8]=pos/8;v[9]=len(prompt)/8
 v[10:]=[np.mean(prompt)/3,np.std(prompt)/3,1.];return v

def init(seed):
 rng=np.random.default_rng(seed)
 return {'w1':rng.normal(0,.15,(FEATURES,24)),'b1':np.zeros(24),'w2':rng.normal(0,.15,(24,ACTIONS)),'b2':np.zeros(ACTIONS)}
def forward(x,m):
 h=np.tanh(x@m['w1']+m['b1']);return softmax(h@m['w2']+m['b2']),h

def gradients(x,logit_grad,m):
 _,h=forward(x,m);dh=(logit_grad@m['w2'].T)*(1-h*h)
 return {'w2':h.T@logit_grad,'b2':logit_grad.sum(0),'w1':x.T@dh,'b1':dh.sum(0)}
def apply(m,g,lr):
 norm=float(np.sqrt(sum(np.sum(v*v) for v in g.values())));scale=min(1.,5/max(norm,1e-12))
 return {k:np.array(m[k]-lr*g[k]*scale,copy=True) for k in m},norm

def model_hash(m):
 h=hashlib.sha256()
 for k in sorted(m):h.update(k.encode());h.update(np.ascontiguousarray(m[k]).tobytes())
 return h.hexdigest()
def serialize(m):return {k:v.tolist() for k,v in m.items()}
def deserialize(m):return {k:np.asarray(v,dtype=float) for k,v in m.items()}

def pretrain(seed,steps=120):
 rng=np.random.default_rng(seed+1000);m=init(seed);x=[];labels=[]
 for i in range(1024):
  p=rng.integers(0,4,int(rng.choice([1,2,4,8]))).tolist();pos=int(rng.integers(len(p)));x.append(features(p,pos,int(rng.integers(4))));labels.append(p[pos])
 x=np.array(x);labels=np.array(labels);loss=[]
 for step in range(steps):
  pr,_=forward(x,m);dz=pr.copy();dz[np.arange(len(x)),labels]-=1;dz/=len(x);m,_=apply(m,gradients(x,dz,m),.2)
  if step%20==0 or step==steps-1:loss.append({'step':step,'nll':float(-np.log(pr[np.arange(len(x)),labels]).mean())})
 return m,loss

def rollout(prompt,m,version,seed):
 rng=np.random.default_rng(seed);xs=[];actions=[];logps=[];previous=0
 for pos in range(len(prompt)):
  x=features(prompt,pos,previous);pr,_=forward(x[None],m);a=int(rng.choice(4,p=pr[0]));xs.append(x.tolist());actions.append(a);logps.append(float(np.log(pr[0,a])));previous=a
 target=[(int(v)+1)%4 for v in prompt];reward=float(np.mean(np.array(actions)==target))
 return {'features':xs,'actions':actions,'behavior_logp':logps,'reward':reward,'target':target,'policy_version':version,'length':len(prompt),'behavior_model_sha256':model_hash(m)}

def group(seed,gid,m,version):
 rng=np.random.default_rng(seed*10000+gid);length=int(rng.choice([1,2,4,8],p=[.4,.3,.2,.1]));prompt=rng.integers(0,4,length).tolist()
 samples=[rollout(prompt,m,version,seed*1000000+gid*10+j) for j in range(4)]
 return {'id':f'{seed}:{gid}','gid':gid,'prompt':prompt,'policy_version':version,'behavior_model_sha256':model_hash(m),'samples':samples,'length':length}

def objective_gradient(m,ref,groups,correct=True,clip=.2,kl_coef=.02):
 """Token-ratio clipped GRPO-like surrogate; NOT unbiased trajectory IS or V-trace.
 Group reward advantages frozen; per-sequence mean weights length equally.
 """
 total={k:np.zeros_like(v) for k,v in m.items()};loss=0.;ratios=[];clipped=0;tokens=0;zero_groups=0;mean_kl=0.;responses=sum(len(g['samples']) for g in groups)
 for g in groups:
  rewards=np.array([s['reward'] for s in g['samples']]);std=float(rewards.std());adv=(rewards-rewards.mean())/(std+1e-6);zero_groups+=std<1e-12
  for advantage,s in zip(adv,g['samples']):
   x=np.array(s['features']);act=np.array(s['actions']);pr,_=forward(x,m);rp,_=forward(x,ref);logp=np.log(np.maximum(pr[np.arange(len(x)),act],1e-12));ratio=np.exp(np.clip(logp-np.array(s['behavior_logp']),-30,30)) if correct else np.ones(len(x))
   active=np.ones(len(x),bool) if not correct else np.where(advantage>=0,ratio<=1+clip,ratio>=1-clip)
   chosen=np.minimum(ratio*advantage,np.clip(ratio,1-clip,1+clip)*advantage) if correct else ratio*advantage
   loss-=float(chosen.mean() if correct else (advantage*logp).mean())/responses;coeff=-advantage*ratio*active/(len(x)*responses);dz=-coeff[:,None]*pr;dz[np.arange(len(x)),act]+=coeff
   # Exact categorical KL(p_current || p_reference), regularizer at sampled visited states.
   logs=np.log(np.maximum(pr,1e-12)/np.maximum(rp,1e-12));kl=np.sum(pr*logs,1);dz+=kl_coef*pr*(logs-kl[:,None])/(len(x)*responses);loss+=kl_coef*float(kl.mean())/responses;mean_kl+=float(kl.mean())/responses
   grad=gradients(x,dz,m)
   for k in total:total[k]+=grad[k]
   ratios.extend(ratio.tolist());clipped+=int((~active).sum());tokens+=len(x)
 return loss,total,{'ratio_mean':float(np.mean(ratios)),'ratio_max':float(max(ratios)),'clip_fraction':clipped/max(tokens,1),'reference_kl':mean_kl,'zero_variance_groups':zero_groups,'tokens':tokens}

def evaluate(m,seed=8801):
 rng=np.random.default_rng(seed);correct=total=exact=0;probs=[]
 for i in range(160):
  length=int(rng.choice([1,2,4,8]));prompt=rng.integers(0,4,length).tolist();previous=0;out=[]
  for pos in range(length):pr,_=forward(features(prompt,pos,previous)[None],m);a=int(pr.argmax());out.append(a);probs.append(float(pr[0,(prompt[pos]+1)%4]));previous=a
  y=[(v+1)%4 for v in prompt];correct+=sum(a==b for a,b in zip(out,y));total+=length;exact+=out==y
 return {'heldout_token_accuracy':correct/total,'heldout_sequence_accuracy':exact/160,'heldout_target_probability':float(np.mean(probs)),'sequences':160,'tokens':total}
