"""Frozen-model calibration depth study. No retraining / no test-selected model.
Keeps v0.6 artifacts unchanged; every fresh media seed and probability is stored.
"""
from pathlib import Path
import json,time,hashlib,platform
import numpy as np
from .experiment import ROOT,dataset,write_json
from .model import predict
from .prediction_sets import fit_threshold,predict_sets,set_metrics,risk_curve,binomial_upper

METHODS=['lac','log_lac','aps_randomized','aps_crossing','lac_top1']
OUT=ROOT/'artifacts'/'calibration-depth'


def infer(model,start,n,condition='id'):
    X,y,records=dataset(start,n,condition)
    p=predict(X,model['parameters'],model['temperature'])
    return p,y,[{'seed':r['seed'],'sha256':r['media_sha256'],'scorable':r['quality']['scorable']} for r in records]


def run():
    OUT.mkdir(exist_ok=True);t=time.perf_counter();mp=ROOT/'artifacts/model.json';m=json.loads(mp.read_text())
    orig_cal= infer(m,130250,250);fresh_cal=infer(m,300000,1000)
    pools={};results={'version':'0.2.0','model_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),
        'frozen_temperature':m['temperature'],'methods':METHODS,'alpha':.1,'conditions':{},'repeats':[],
        'protocol':'all model/temperature frozen; primary calibration=fresh 1000 ID; no test-based selection; all five methods reported',
        'sources':['https://mapie.readthedocs.io/en/stable/theoretical_description_classification.html','https://arxiv.org/html/2009.14193v5'],
        'environment':{'python':platform.python_version(),'numpy':np.__version__}}
    rng=np.random.default_rng(8021);uc=rng.uniform(size=len(fresh_cal[1]));uo=rng.uniform(size=len(orig_cal[1]))
    thresholds={k:fit_threshold(fresh_cal[0],fresh_cal[1],k,u=uc if k=='aps_randomized' else None) for k in METHODS}
    results['fresh_thresholds']=thresholds
    oldq=fit_threshold(orig_cal[0],orig_cal[1],'lac')
    results['original_calibration']={'n':250,'threshold_recomputed':oldq,'threshold_frozen':m['conformal_q'],
        'threshold_abs_difference':abs(oldq-m['conformal_q']),
        'set_metrics':set_metrics(predict_sets(orig_cal[0],oldq),orig_cal[1],orig_cal[0]),
        'nonconformity_quantiles':np.quantile(1-orig_cal[0][np.arange(250),orig_cal[1]],[0,.5,.9,.95,1]).tolist()}
    for j,condition in enumerate(['id','noise','periodic','silent','distractor','drift','missing','long']):
        print('New heldout',condition,flush=True)
        pack=infer(m,310000+j*2000,600,condition);p,y,records=pack;u=rng.uniform(size=len(y))
        comparisons={}
        for k in METHODS:
            sets=predict_sets(p,thresholds[k],k,u=u if k=='aps_randomized' else None)
            comparisons[k]=set_metrics(sets,y,p)
        comparisons['legacy_lac']=set_metrics(predict_sets(p,m['conformal_q']),y,p)
        singleton=predict_sets(p,thresholds['aps_crossing'],'aps_crossing').sum(1)==1
        eligible=np.array([r['scorable'] for r in records]) & singleton
        results['conditions'][condition]={'sets':comparisons,
            'all_confidence_risk':risk_curve(p,y),
            'aps_singleton_scorable_risk':risk_curve(p,y,eligible),
            'accuracy':float(np.mean(p.argmax(1)==y)),
            'label_validity':'first-half delay only, not full-video stable truth' if condition=='drift' else ('latent chosen source, observationally ambiguous' if condition in ['periodic','silent'] else 'synthetic delay')}
        pools[condition]={'probabilities':p.tolist(),'labels':y.tolist(),'uniforms':u.tolist(),'records':records}
    # Each replicate uses independent new media, rather than resampling a fixed test.
    for repeat in range(24):
        print('Independent calibration/test repeat',repeat,flush=True)
        start=400000+repeat*2000;c=infer(m,start,250);e=infer(m,start+500,400)
        uc=rng.uniform(size=250);ut=rng.uniform(size=400);row={'repeat':repeat,'calibration_start':start,'test_start':start+500,'methods':{}}
        for k in METHODS:
            q=fit_threshold(c[0],c[1],k,u=uc if k=='aps_randomized' else None)
            sets=predict_sets(e[0],q,k,u=ut if k=='aps_randomized' else None)
            row['methods'][k]={'q':q,**set_metrics(sets,e[1],e[0])}
        results['repeats'].append(row)
        write_json(OUT/f'repeat-{repeat:02d}.json',{'calibration':{'probabilities':c[0].tolist(),'labels':c[1].tolist(),'uniforms':uc.tolist(),'records':c[2]},
            'test':{'probabilities':e[0].tolist(),'labels':e[1].tolist(),'uniforms':ut.tolist(),'records':e[2]},'results':row})
    results['repeat_summary']={}
    for k in METHODS:
        cov=np.array([r['methods'][k]['coverage'] for r in results['repeats']]);size=np.array([r['methods'][k]['mean_size'] for r in results['repeats']])
        results['repeat_summary'][k]={'mean_coverage':float(cov.mean()),'sd_coverage':float(cov.std(ddof=1)),
            'coverage_quantiles_05_50_95':np.quantile(cov,[.05,.5,.95]).tolist(),'replicates_below_90':int((cov<.9).sum()),
            'mean_set_size':float(size.mean()),'mean_empty_rate':float(np.mean([r['methods'][k]['empty_rate'] for r in results['repeats']]))}
    # Exact 0 observed errors doesn't imply 0 risk; dependence assumptions explicit.
    results['zero_error_illustration']=[{'accepted':n,'errors':0,'upper95':binomial_upper(0,n)} for n in [3,20,50,100,211,600]]
    pools['fresh_calibration']={'probabilities':fresh_cal[0].tolist(),'labels':fresh_cal[1].tolist(),'uniforms':uc.tolist() if len(uc)==1000 else [],'records':fresh_cal[2]}
    # Persist exact uniforms used for primary threshold, independent from repeat uniforms.
    primary_rng=np.random.default_rng(8021)
    pools['fresh_calibration']['uniforms']=primary_rng.uniform(size=1000).tolist()
    write_json(OUT/'probability-pools.json',pools)
    results['seconds']=time.perf_counter()-t
    write_json(OUT/'results.json',results)
    print(json.dumps(results['repeat_summary'],indent=2),flush=True)
    print('Wall seconds',results['seconds'],flush=True)

if __name__=='__main__':run()
