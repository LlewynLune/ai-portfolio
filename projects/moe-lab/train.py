"""Sparse top1 expert routing on authored nonlinear scalar regression."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from frontier_support import *
ROOT=Path(__file__).resolve().parent

class SparseMoE(nn.Module):
 def __init__(self):
  super().__init__();self.router=nn.Linear(2,4);self.experts=nn.ModuleList([nn.Sequential(nn.Linear(2,16),nn.Tanh(),nn.Linear(16,1)) for _ in range(4)])
 def forward(self,x):
  probs=self.router(x).softmax(-1);ids=probs.argmax(-1);out=torch.zeros(len(x),1);counts=[]
  # Only selected examples execute each expert; no dense-all-expert fake sparsity.
  for i,e in enumerate(self.experts):
   ix=(ids==i).nonzero().flatten();counts.append(len(ix))
   if len(ix):out=out.index_copy(0,ix,e(x[ix])*probs[ix,i:i+1])
  fraction=F.one_hot(ids,4).float().mean(0);balance=4*(fraction*probs.mean(0)).sum()
  return out,ids,probs,balance,counts

def dataset(n,seed,shift=False):
 rng=np.random.default_rng(seed);x=rng.uniform(-1,1,(n,2));
 if shift:x[:,0]=rng.uniform(.6,1,n)
 y=np.where(x[:,0]>=0,np.sin(3*x[:,1])+.5*x[:,0],np.cos(3*x[:,1])-.5*x[:,0]);return torch.tensor(x,dtype=torch.float32),torch.tensor(y[:,None],dtype=torch.float32)
def fit(m,x,y,lb=0,steps=700):
 torch.manual_seed(42);opt=torch.optim.Adam(m.parameters(),lr=.005);history=[]
 for step in range(steps):
  ix=torch.randint(len(x),(128,));result=m(x[ix]);pred=result[0] if isinstance(result,tuple) else result;loss=F.mse_loss(pred,y[ix])+(lb*result[3] if isinstance(result,tuple) else 0);opt.zero_grad();loss.backward();opt.step()
  if step%50==0:history.append({'step':step,'loss':float(loss.detach())})
 return history
def export_moe(m):
 linear=lambda l:{'weight':l.weight.detach().tolist(),'bias':l.bias.detach().tolist()}
 return {'kind':'sparse_moe','router':linear(m.router),'experts':[{'first':linear(e[0]),'last':linear(e[2])} for e in m.experts]}
def main():
 x,y=dataset(2400,10);va,vy=dataset(500,20);te,ty=dataset(700,30);ood,oy=dataset(700,40,True);variants={};history={}
 for lb in [0,.03]:
  torch.manual_seed(42);m=SparseMoE();name='top1_lb'+str(lb);history[name]=fit(m,x,y,lb);variants[name]=m
 torch.manual_seed(42);dense=nn.Sequential(nn.Linear(2,16),nn.Tanh(),nn.Linear(16,1));history['dense_active16']=fit(dense,x,y);variants['dense_active16']=dense
 torch.manual_seed(42);large=nn.Sequential(nn.Linear(2,64),nn.Tanh(),nn.Linear(64,1));history['dense_total64']=fit(large,x,y);variants['dense_total64']=large
 chosen=min(['top1_lb0','top1_lb0.03'],key=lambda n:float(F.mse_loss(variants[n](va)[0],vy)));rows=[];predictions=[];examples=[]
 for group,xx,yy in [('validation',va,vy),('heldout_uniform',te,ty),('skew_positive_ood',ood,oy)]:
  for n,m in variants.items():
   with torch.no_grad():result=m(xx);p=result[0] if isinstance(result,tuple) else result
   if isinstance(result,tuple):counts=result[4];ratio=max(counts)/len(xx);entropy=float(-(torch.tensor(counts,dtype=torch.float32)/len(xx)).clamp_min(1e-10).log().mul(torch.tensor(counts)/len(xx)).sum())
   else:counts=[];ratio=None;entropy=None
   rows.append({'group':group,'model':n,'rmse':float(F.mse_loss(p,yy).sqrt()),'total_parameters':param_count(m),'active_parameter_estimate':12+65 if isinstance(m,SparseMoE) else param_count(m),'max_expert_fraction':ratio,'routing_entropy':entropy})
   predictions.extend({'group':group,'model':n,'index':i,'truth':float(v),'prediction':float(z),'route':int(result[1][i]) if isinstance(result,tuple) else None} for i,(v,z) in enumerate(zip(yy[:,0],p[:,0])))
  with torch.no_grad():p,route,prob,_,_=variants[chosen](xx)
  for i in [0,1,2]:examples.append({'group':group,'input':xx[i].tolist(),'truth':float(yy[i]),'output':[float(p[i])],'route':int(route[i]),'routing_probabilities':prob[i].tolist()})
 save(ROOT,{'title':'SparseMoE-Lab','protocol':'2400train/500validation/700test authored2D nonlinear regression; skewOOD700 independent seed.4experts width16 top1 vs dense16(active-like) and dense64(total-like).700steps; choose balance0 vs.03 only validation RMSE.',
 'selected':chosen,'metrics':rows,'predictions':predictions,'examples':examples,'loss_curves':history,
 'limits':['Not a Transformer MoE, distributed experts, AllToAll or trillion-parameter training.','Top1 gating multiplies expert output by selected probability for router gradients.','Routing load balancing loss from minibatch proportions; selection nondifferentiable, could collapse.','Each expert actually processes only selected examples, but Python CPU dispatch may be slower; parameter estimate not latency benchmark.','No capacity dropping; dataset skew can alter load and hurt coverage.','Dense comparisons active-like and total-like are not exact compute matches; noSOTA.']},export_moe(variants[chosen]))
if __name__=='__main__':main()
