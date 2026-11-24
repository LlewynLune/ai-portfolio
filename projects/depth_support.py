"""Shared numerical inference and evidence utilities; no training or private credentials.
Frozen exports are inert JSON. New results live in artifacts/depth, never old artifacts.
"""
from pathlib import Path
import json,hashlib,platform,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def load(path):return json.loads(Path(path).read_text())
def softmax(z):
    z=np.asarray(z,dtype=float);e=np.exp(z-z.max(axis=-1,keepdims=True));return e/e.sum(axis=-1,keepdims=True)
def affine(x,model):
    x=np.asarray(x,float)
    if x.shape[-1]!=len(model['mean']) or not np.isfinite(x).all():raise ValueError('finite input dimension required')
    z=(x-model['mean'])/model['scale']
    if model['kind']=='mlp':
        for i,(w,b) in enumerate(zip(model['weights'],model['bias'])):
            z=z@np.asarray(w)+b
            if i<len(model['weights'])-1:z=np.maximum(z,0) if model['activation']=='relu' else np.tanh(z)
        return z
    return z@np.asarray(model['weights']).T+model['bias']
class Attention:
    """Float64 inference for existing one-block causal model; exact KV-cache semantics."""
    def __init__(self,model):
        self.model=model;self.s={k:np.asarray(v,float) for k,v in model['state'].items()};self.d=model['config']['d'];self.heads=model['config']['heads'];self.enabled=model['config']['attention']
    def linear(self,x,n):return x@self.s[n+'.weight'].T+self.s[n+'.bias']
    def norm(self,x,n):return (x-x.mean(-1,keepdims=True))/np.sqrt(x.var(-1,keepdims=True)+1e-5)*self.s[n+'.weight']+self.s[n+'.bias']
    def forward(self,tokens,weights=False):
        ids=np.asarray(tokens)
        if ids.ndim==1:ids=ids[None,:]
        if ids.ndim!=2 or ids.dtype.kind not in 'iu' or not 1<=ids.shape[1]<=16 or ids.min()<0 or ids.max()>=18:raise ValueError('integer tokens 0..17, length 1..16')
        B,T=ids.shape;x=self.s['embed.weight'][ids]+self.s['pos.weight'][np.arange(T)];a=None
        if self.enabled:
            z=self.norm(x,'ln1');hs=self.heads;dh=self.d//hs
            q,k,v=[self.linear(z,n).reshape(B,T,hs,dh).transpose(0,2,1,3) for n in ['q','k','v']]
            score=q@k.transpose(0,1,3,2)/np.sqrt(dh);score=np.where(np.triu(np.ones((T,T),bool),1),-np.inf,score);a=softmax(score)
            out=(a@v).transpose(0,2,1,3).reshape(B,T,self.d);x=x+self.linear(out,'proj')
        x=x+self.linear(np.maximum(self.linear(self.norm(x,'ln2'),'ff1'),0),'ff2');logits=self.linear(x,'head')
        return (logits,a) if weights else logits
    def step(self,token,cache=None):
        cache=cache or {'k':[],'v':[]};p=len(cache['k'])
        if not isinstance(token,(int,np.integer)) or not 0<=token<18 or p>=16:raise ValueError('cache/token out of range')
        x=self.s['embed.weight'][token]+self.s['pos.weight'][p];z=self.norm(x,'ln1')
        q,k,v=[self.linear(z,n).reshape(self.heads,-1) for n in ['q','k','v']]
        new={'k':cache['k']+[k], 'v':cache['v']+[v]}
        if self.enabled:
            ks=np.stack(new['k'],axis=1);vs=np.stack(new['v'],axis=1);a=softmax(np.einsum('hd,htd->ht',q,ks)/np.sqrt(self.d/self.heads));out=np.einsum('ht,htd->hd',a,vs).reshape(-1);x=x+self.linear(out,'proj')
        x=x+self.linear(np.maximum(self.linear(self.norm(x,'ln2'),'ff1'),0),'ff2');return self.linear(x,'head'),new

def generate_lookup(n,seed,pairs=3,shift=0,exclude=None):
    r=np.random.default_rng(seed);xs=[];ys=[];seen={tuple(json.loads(s)) if isinstance(s,str) else tuple(s) for s in (exclude or [])}
    while len(xs)<n:
        keys=r.choice(8,pairs,replace=False);values=r.integers(0,8,pairs);j=int(r.integers(pairs));x=np.column_stack([keys,values+8]).reshape(-1).tolist()+[16,int(keys[j])]
        if tuple(x) in seen:continue
        seen.add(tuple(x));xs.append(x);ys.append(int((values[j]+shift)%8+8))
    return np.array(xs,dtype=int),np.array(ys)
def cls_rows(project,model,group,y,p,keys=None):
    p=np.asarray(p);conf=p.max(-1);pred=p.argmax(-1)
    return [dict(model=model,condition=group,index=str(keys[i] if keys is not None else i),truth=int(y[i]),prediction=int(pred[i]),confidence=float(conf[i]),loss=float(-np.log(max(p[i,int(y[i])],1e-15))),correct=bool(pred[i]==y[i])) for i in range(len(y))]
def metrics(rows):
    if not rows:return {'n':0}
    o={'n':len(rows)}
    if 'correct' in rows[0]:
        k=sum(r['correct'] for r in rows);o.update(accuracy=k/len(rows))
        if any(r.get('loss',0)>0 for r in rows):o['nll']=float(np.mean([r.get('loss',0) for r in rows]))
    if 'error' in rows[0]:o.update(mae=float(np.mean([abs(r['error']) for r in rows])),rmse=float(np.sqrt(np.mean([r['error']**2 for r in rows]))))
    for key in ['nmse','elapsed_ms']:
        if key in rows[0]:o['mean_'+key]=float(np.mean([r[key] for r in rows]))
    if 'admitted' in rows[0]:o['admission_coverage']=float(np.mean([r['admitted'] for r in rows]))
    return o
def wilson(k,n,z=1.95996398454):
    if not n:return [None,None]
    p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;r=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return [float(max(0,c-r)),float(min(1,c+r))]
def aggregate(rows):
    return [dict(model=m,condition=c,**metrics([r for r in rows if r['model']==m and r['condition']==c])) for m,c in sorted(set((r['model'],r['condition']) for r in rows))]
def save(folder,title,protocol,rows,findings,extra=None,sources=None):
    folder=Path(folder);out=folder/'artifacts/depth';out.mkdir(parents=True,exist_ok=True)
    sourcefiles=[folder/'depth.py',Path(__file__)]+[Path(p) for p in sources or []];hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sourcefiles}
    report=dict(schema=1,title=title,protocol=protocol,metrics=aggregate(rows),records=rows,findings=findings,details=extra or {},source_hashes=hashes,environment=dict(python=sys.version,numpy=np.__version__,platform=platform.platform()),scope='AI-assisted new local stress experiments; no retraining, external API, private data or production claim')
    (out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    lines=['# '+title+'｜深化实测','',protocol,'','## 方法与结果','', '|模型|条件|样本|Accuracy / MAE / 其他|','|---|---|---:|---|']
    for r in report['metrics']:lines.append('|'+r['model']+'|'+r['condition']+'|'+str(r['n'])+'|'+json.dumps({k:v for k,v in r.items() if k not in ['model','condition','n']},ensure_ascii=False)+'|')
    lines+=['','## 发现与失败边界','']+['- '+x for x in findings]+['','## 工程与复现','', '在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。', '', '[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)','',report['scope']]
    (out/'REPORT.md').write_text('\n'.join(lines)+'\n');print(folder.name,len(rows),'records',len(report['metrics']),'conditions')
    return report
