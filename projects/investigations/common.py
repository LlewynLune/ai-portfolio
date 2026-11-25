"""Immutable outputs for domain-specific investigations; no original evidence edits."""
import json,hashlib,platform,sys,importlib.util,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];PROJECTS=ROOT/'projects'
sys.path.insert(0,str(PROJECTS))
from depth_support import load,Attention,softmax,affine,generate_lookup

def module(folder):
 path=PROJECTS/folder/'depth.py';spec=importlib.util.spec_from_file_location('investigation_'+folder.replace('-','_'),path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def freeze(folder,protocol):
 out=PROJECTS/folder/'artifacts/investigation'
 if out.exists():raise RuntimeError('immutable investigation already exists: '+folder)
 out.mkdir(parents=True);(out/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n');return out

def save(folder,title,question,rows,metrics,findings,protocol,details=None,files=None):
 out=PROJECTS/folder/'artifacts/investigation'
 sources=[Path(__file__)]+[Path(p) for p in files or []]
 evidence={'schema_version':1,'project':folder,'title':title,'question':question,'records':rows,'metrics':metrics,'findings':findings,'protocol':protocol,'details':details or {},
 'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
 'environment':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},
 'scope':'AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.'}
 (out/'results.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
 lines=['# '+title,'',question,'','## 预声明实验协议','',json.dumps(protocol,ensure_ascii=False,indent=2),'','## 全部条件结果','']
 if metrics:
  keys=list(dict.fromkeys(k for r in metrics for k in r));lines+=['|'+'|'.join(keys)+'|','|'+'|'.join('---' for k in keys)+'|']
  for r in metrics:lines+=['|'+'|'.join((f'{r.get(k):.5g}' if isinstance(r.get(k),float) else str(r.get(k,'—'))).replace('|','/') for k in keys)+'|']
 lines+=['','## 发现、失败与适用边界','']+['- '+f for f in findings]+['','## 原始证据与复现','','[全部逐条记录](results.json) · [预声明协议](protocol.json)','',f'从仓库根目录运行 python3 scripts/run_investigations.py --project {folder}。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。','',evidence['scope']]
 (out/'REPORT.md').write_text('\n'.join(lines)+'\n');hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()};(out/'checksums.json').write_text(json.dumps(hashes,indent=2)+'\n');print('completed',folder,len(rows),'records',flush=True)
 return evidence

def finite_quantile(scores,alpha):
 # Split conformal finite sample rank, infinity when n cannot support requested level.
 a=np.sort(np.asarray(scores));rank=int(np.ceil((len(a)+1)*(1-alpha)))
 return (float(a[rank-1]) if 1<=rank<=len(a) else None),rank

def class_metrics(p,y):
 p=np.asarray(p);y=np.asarray(y);one=np.eye(p.shape[1])[y];pred=p.argmax(1)
 return {'n':len(y),'accuracy':float(np.mean(pred==y)),'nll':float(-np.log(np.maximum(p[np.arange(len(y)),y],1e-15)).mean()),'brier':float(np.mean(np.sum((p-one)**2,axis=1)))}

def hidden(tokens,m):
 """Independent final hidden state for head-only training; forward parity checked."""
 a=Attention(m);ids=np.asarray(tokens);B,T=ids.shape
 x=a.s['embed.weight'][ids]+a.s['pos.weight'][np.arange(T)]
 if a.enabled:
  z=a.norm(x,'ln1');h=a.heads;dh=a.d//h;q,k,v=[a.linear(z,n).reshape(B,T,h,dh).transpose(0,2,1,3) for n in ('q','k','v')]
  scores=q@k.transpose(0,1,3,2)/np.sqrt(dh);scores=np.where(np.triu(np.ones((T,T),bool),1),-np.inf,scores)
  x=x+a.linear((softmax(scores)@v).transpose(0,2,1,3).reshape(B,T,a.d),'proj')
 x=x+a.linear(np.maximum(a.linear(a.norm(x,'ln2'),'ff1'),0),'ff2');return x[:,-1]
