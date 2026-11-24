"""New TextGuard lexical invariance and selective-risk analysis, frozen model."""
from pathlib import Path
import sys,re,collections
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from depth_support import *
HERE=Path(__file__).resolve().parent

def normalize(t):
    if not isinstance(t,str) or len(t)>2000:raise ValueError('text string <=2000')
    t=re.sub(r'https?://\S+|www\.\S+',' urltoken ',t.lower());t=re.sub(r'\S+@\S+',' emailtoken ',t);t=re.sub(r'\d+',' numbertoken ',t);return ' '.join(re.findall('[a-z]+',t))
def infer(text,m):
    ws=normalize(text).split();counts=collections.Counter(ws+[' '.join(ws[i:i+2]) for i in range(len(ws)-1)]);v={m['vocabulary'][k]:c*m['idf'][m['vocabulary'][k]] for k,c in counts.items() if k in m['vocabulary']};norm=np.linalg.norm(list(v.values()));z=m['intercept']+sum(x/norm*m['coef'][i] for i,x in v.items()) if norm else m['intercept'];p=float(1/(1+np.exp(-z)));return p,len(v)

def main():
    m=load(HERE/'artifacts/model.json');vocab=list(m['vocabulary']);items=[(f'Please attend the {word} meeting tomorrow',0) for word in ['project','school','library','team','lecture','research','family','office','design','training']]+[(f'Congratulations claim your free {word} prize now call this number',1) for word in ['cash','holiday','gift','mobile','bonus','ticket','money','reward','voucher','credit']]
    rows=[];transforms={'clean':lambda t:t,'case_punctuation':lambda t:t.upper()+'!!!','whitespace':lambda t:'  \n '.join(t.split()),'single_typo':lambda t:t.replace('free','fre').replace('meeting','meetin'),'negation':lambda t:'Do not respond to this message: '+t,'unknown_prefix':lambda t:'你好 qzxv kzzp '+t}
    for condition,fn in transforms.items():
        for i,(t,y) in enumerate(items):
            p,n=infer(fn(t),m);pred=int(p>=m['threshold']);rows.append(dict(model='frozen_tfidf',condition=condition,index=i,truth=y,prediction=pred,confidence=float(max(p,1-p)),loss=float(-np.log(max(p if y else 1-p,1e-15))),correct=pred==y,known_terms=n,probability=p,text=fn(t)))
    prior=load(HERE/'artifacts/results.json');test=[x for x in prior['predictions'] if x['model']=='tfidf_logistic'];curve=[]
    for margin in [0,.05,.1,.15,.2,.3,.4]:
        kept=[r for r in test if abs(r['probability']-m['threshold'])>=margin];err=sum(r['label']!=r['prediction'] for r in kept);curve.append(dict(margin=margin,n=len(kept),coverage=len(kept)/len(test),error=err/len(kept) if kept else None,error_interval=wilson(err,len(kept))))
    assert all(abs(infer(t,m)[0]-infer(t.upper()+'!!!',m)[0])<1e-12 for t,y in items)
    save(HERE,'TextGuard lexical stress & abstention','20 authored English probes × 6 transformations; intended labels explicitly authored, not natural-distribution evaluation. Frozen threshold. Historical test risk curve is descriptive, not threshold selection.',rows,['Case/punctuation and whitespace must preserve normalized model inference.','Negation and typos expose lexical limitations; unknown language must route to manual review.','Abstention curve uses the same historical test, so no post-hoc safety guarantee.'],extra=dict(selective_curve=curve,threshold=m['threshold'],unknown_language_probe=infer('你好明天开会',m)),sources=[HERE/'artifacts/model.json',HERE/'artifacts/results.json'])
if __name__=='__main__':main()
