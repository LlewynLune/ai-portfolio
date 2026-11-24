"""Small CPU research models; independent implementations, not paper-scale replication."""
from pathlib import Path
import json,hashlib,math,platform,time,copy
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
THREADS=2
torch.set_num_threads(THREADS)
V=18

class LowRankLinear(nn.Module):
 def __init__(self,base,rank):
  super().__init__();self.base=base
  for p in base.parameters():p.requires_grad=False
  self.A=nn.Parameter(torch.randn(rank,base.in_features)*.02);self.B=nn.Parameter(torch.zeros(base.out_features,rank));self.rank=rank
 def forward(self,x):return self.base(x)+F.linear(F.linear(x,self.A),self.B)/self.rank
 def merged(self):return self.base.weight+self.B@self.A/self.rank

class TinyAttention(nn.Module):
 def __init__(self,d=32,heads=2,attention=True):
  super().__init__();self.d=d;self.heads=heads;self.attention=attention
  self.embed=nn.Embedding(V,d);self.pos=nn.Embedding(16,d);self.ln1=nn.LayerNorm(d);self.ln2=nn.LayerNorm(d)
  self.q=nn.Linear(d,d);self.k=nn.Linear(d,d);self.v=nn.Linear(d,d);self.proj=nn.Linear(d,d)
  self.ff1=nn.Linear(d,64);self.ff2=nn.Linear(64,d);self.head=nn.Linear(d,V)
 def forward(self,tokens,return_attention=False):
  B,T=tokens.shape;x=self.embed(tokens)+self.pos(torch.arange(T));weights=None
  if self.attention:
   z=self.ln1(x);h=self.heads;a=self.d//h
   q=self.q(z).reshape(B,T,h,a).transpose(1,2);k=self.k(z).reshape(B,T,h,a).transpose(1,2);v=self.v(z).reshape(B,T,h,a).transpose(1,2)
   score=q@k.transpose(-1,-2)/math.sqrt(a);mask=torch.triu(torch.ones(T,T,dtype=torch.bool),diagonal=1);weights=score.masked_fill(mask,float('-inf')).softmax(-1)
   out=(weights@v).transpose(1,2).reshape(B,T,self.d);x=x+self.proj(out)
  x=x+self.ff2(F.relu(self.ff1(self.ln2(x))));logits=self.head(x)
  return (logits,weights) if return_attention else logits

def generate(n,seed,pairs=3,shift=0,exclude=None):
 rng=np.random.default_rng(seed);exclude=set(exclude or []);tokens=[];ys=[];ids=[]
 while len(tokens)<n:
  keys=rng.choice(8,pairs,replace=False);values=rng.integers(0,8,pairs);j=int(rng.integers(pairs));prefix=np.column_stack([keys,values+8]).reshape(-1).tolist()+[16,int(keys[j])];identity=json.dumps(prefix)
  if identity in exclude:continue
  exclude.add(identity);tokens.append(prefix);ys.append(int((values[j]+shift)%8+8));ids.append(identity)
 return torch.tensor(tokens),torch.tensor(ys),ids

def train_model(model,x,y,steps=900,lr=.003,seed=42):
 torch.manual_seed(seed);opt=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=lr);losses=[];model.train()
 for step in range(steps):
  idx=torch.randint(len(x),(64,));loss=F.cross_entropy(model(x[idx])[:,-1],y[idx]);opt.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1);opt.step()
  if step%50==0:losses.append({'step':step,'loss':float(loss.detach())})
 model.eval();return losses

def evaluate(model,x,y):
 model.eval()
 with torch.no_grad():
  logits=torch.cat([model(b)[:,-1] for b in x.split(128)]);p=logits.softmax(-1);pred=p.argmax(-1);nll=F.cross_entropy(logits,y)
 return {'accuracy':float((pred==y).float().mean()),'nll':float(nll)},p.tolist()
def export(model):
 # Only inert tensor data; no pickle/class/object deserialization.
 return {'config':{'d':model.d,'heads':model.heads,'attention':model.attention},'state':{k:v.detach().cpu().tolist() for k,v in model.state_dict().items()}}
def restore(data):
 m=TinyAttention(**data['config']);m.load_state_dict({k:torch.tensor(v) for k,v in data['state'].items()});return m.eval()
def merged_export(m):
 a=copy.deepcopy(m)
 for name in ['q','v','head']:
  layer=getattr(a,name)
  if isinstance(layer,LowRankLinear):
   linear=nn.Linear(layer.base.in_features,layer.base.out_features)
   with torch.no_grad():linear.weight.copy_(layer.merged());linear.bias.copy_(layer.base.bias)
   setattr(a,name,linear)
 return export(a)
def param_count(m):return sum(p.numel() for p in m.parameters() if p.requires_grad)
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(root,report,model):
 root=Path(root);out=root/'artifacts';out.mkdir(exist_ok=True);report.update({'environment':{'torch':torch.__version__,'numpy':np.__version__,'platform':platform.platform(),'threads':THREADS,'device':'cpu'},'code_sha256':digest(root/'train.py'),'support_sha256':digest(__file__)})
 for n,v in [('results.json',report),('model.json',model)]: (out/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False))
 (out/'checksums.json').write_text(json.dumps({n:digest(out/n) for n in ['results.json','model.json']},indent=2))
 rows=report['metrics'];keys=list(rows[0]);lines=['# '+report['title']+'｜冻结运行结果','',report['protocol'],'','|'+'|'.join(keys)+'|','|'+'|'.join(['---']*len(keys))+'|']
 for r in rows:lines.append('|'+'|'.join(f'{r[k]:.5f}' if isinstance(r[k],float) else str(r[k]) for k in keys)+'|')
 lines+=['','## 边界']+['- '+l for l in report['limits']]+['','[逐条结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)']
 (out/'REPORT.md').write_text('\n'.join(lines)+'\n');print(report['title'],json.dumps(rows,ensure_ascii=False))
