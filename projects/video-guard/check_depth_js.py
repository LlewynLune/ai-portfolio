"""Native JS/Python candidate set and risk-count parity on new holdout examples."""
import json,subprocess
import numpy as np
from enhance_demo import SET_ENGINE
from videoguard.experiment import ROOT,write_json
from videoguard.prediction_sets import predict_sets,risk_curve


def run():
    d=ROOT/'artifacts/calibration-depth';r=json.loads((d/'results.json').read_text());pools=json.loads((d/'probability-pools.json').read_text());m=json.loads((ROOT/'artifacts/model.json').read_text());cases=[]
    for group in r['conditions']:
        pool=pools[group]
        for i in [0,7,31,91,233,599]:
            for method in r['methods']+['legacy_lac']:
                q=m['conformal_q'] if method=='legacy_lac' else r['fresh_thresholds'][method]
                cases.append({'p':pool['probabilities'][i],'q':q,'method':method,'u':pool['uniforms'][i]})
    code=SET_ENGINE+'const cases='+json.dumps(cases)+';console.log(JSON.stringify(cases.map(c=>setFor(c.p,c.q,c.method,c.u))));'
    js=json.loads(subprocess.run(['node','--input-type=commonjs'],input=code,text=True,capture_output=True,check=True).stdout)
    for c,a in zip(cases,js):
        p=np.array(c['p'])[None];method='lac' if c['method']=='legacy_lac' else c['method']
        s=predict_sets(p,c['q'],method,u=np.array([c['u']]) if method=='aps_randomized' else None)
        assert a==np.flatnonzero(s[0]).tolist(),c
    riskcases=[{'pool':pools[g],'threshold':t} for g in r['conditions'] for t in [0,.5,.9,1]]
    code=SET_ENGINE+'const cases='+json.dumps(riskcases)+';console.log(JSON.stringify(cases.map(c=>riskFor(c.pool,c.threshold))));'
    js=json.loads(subprocess.run(['node','--input-type=commonjs'],input=code,text=True,capture_output=True,check=True).stdout)
    for c,a in zip(riskcases,js):
        pool=c['pool'];b=risk_curve(np.array(pool['probabilities']),np.array(pool['labels']),thresholds=[c['threshold']])[0]
        assert a['n']==b['accepted'] and a['errors']==b['errors']
    write_json(d/'js-parity.json',{'set_cases':len(cases),'risk_cases':len(riskcases),'exact_candidate_and_count_parity':True})
    print('Depth JS/Python parity',len(cases),'sets and',len(riskcases),'risk counts')
if __name__=='__main__':run()
