"""Shared numerical evidence helpers for four independent learning experiments."""
from pathlib import Path
import hashlib,json,platform,sys
import numpy as np
import sklearn

def save(root,report,model):
 out=Path(root)/'artifacts';out.mkdir(exist_ok=True)
 report['environment']={'python':sys.version,'numpy':np.__version__,'sklearn':sklearn.__version__,'platform':platform.platform()}
 report['code_sha256']=hashlib.sha256((Path(root)/'train.py').read_bytes()).hexdigest()
 report['support_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 for name,value in [('results.json',report),('model.json',model)]:
  (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False))
 (out/'checksums.json').write_text(json.dumps({n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ('results.json','model.json')},indent=2))
 rows=report['metrics'];keys=list(rows[0]);lines=['# '+report['title']+'｜本次实际运行','',report['protocol'],'','|'+ '|'.join(keys)+'|','|'+ '|'.join(['---']*len(keys))+'|']
 for r in rows:lines.append('|'+ '|'.join(f'{r[k]:.5f}' if isinstance(r[k],float) else str(r[k]) for k in keys)+'|')
 lines+=['','## 明确局限']+['- '+v for v in report['limits']]+['','[逐样本/逐帧结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)']
 (out/'REPORT.md').write_text('\n'.join(lines)+'\n');print(report['title'],json.dumps(rows,ensure_ascii=False))

def linear_export(est,mean,scale,kind='linear'):
 return {'kind':kind,'mean':np.asarray(mean).tolist(),'scale':np.asarray(scale).tolist(),'weights':np.atleast_2d(est.coef_).tolist(),'bias':np.atleast_1d(est.intercept_).tolist()}
def mlp_export(est,mean,scale):
 return {'kind':'mlp','mean':np.asarray(mean).tolist(),'scale':np.asarray(scale).tolist(),'weights':[w.tolist() for w in est.coefs_],'bias':[b.tolist() for b in est.intercepts_],'activation':est.activation}
def forward(x,m):
 a=(np.asarray(x,dtype=float)-np.asarray(m['mean']))/np.asarray(m['scale'])
 if m['kind']=='mlp':
  for i,(w,b) in enumerate(zip(m['weights'],m['bias'])):
   a=a@np.asarray(w)+b
   if i<len(m['weights'])-1:a=np.maximum(a,0) if m['activation']=='relu' else np.tanh(a)
  return a
 return a@np.asarray(m['weights']).T+m['bias']
def softmax(logits,temperature=1):
 z=np.asarray(logits)/temperature;z=z-z.max(axis=-1,keepdims=True);e=np.exp(z);return e/e.sum(axis=-1,keepdims=True)
def regression(y,p):
 e=np.asarray(p)-np.asarray(y);return {'mae':float(np.abs(e).mean()),'rmse':float(np.sqrt(np.mean(e**2))),'p95_abs_error':float(np.quantile(np.abs(e),.95))}
