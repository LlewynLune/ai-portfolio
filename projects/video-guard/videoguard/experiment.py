"""Reproducible experiment driver. All sets grouped by unique base-media seed."""
from pathlib import Path
import argparse, json, hashlib, platform, time
import numpy as np
from .data import make_clip, content_hash, LAGS
from .features import extract, lag_features, baseline, signal_quality, windows
from .model import fit, forward, predict, export, temperature
from .calibration import metrics, choose_threshold, selective, conformal_q, conformal_sets, bootstrap_difference

ROOT=Path(__file__).resolve().parents[1]


def write_json(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def dataset(start,n,condition='id'):
    X=[];y=[];records=[]
    for seed in range(start,start+n):
        c=make_clip(seed,condition=condition)
        s=extract(c.frames,c.audio,c.fps,c.sample_rate)
        X.append(lag_features(s));y.append(c.delay+6)
        records.append({'seed':seed,'media_sha256':content_hash(c),'delay_frames':c.delay,
                        'xcorr':baseline(s),'onset_xcorr':baseline(s,True),'quality':signal_quality(s),
                        'signals':s if seed==start else None})
    return np.asarray(X),np.asarray(y),records


def evaluate(p,temp,q,threshold,X,y,records):
    t=time.perf_counter();probs=predict(X,p,temp);secs=time.perf_counter()-t
    sets=conformal_sets(probs,q)
    result=metrics(probs,y)
    result.update({'selective':selective(probs,y,threshold,[r['quality']['scorable'] for r in records]),
                   'prediction_set_coverage':float(sets[np.arange(len(y)),y].mean()),
                   'prediction_set_mean_size':float(sets.sum(1).mean()),
                   'inference_seconds_batch':secs,'inference_ms_per_clip':secs/len(y)*1000})
    bp=np.array([r['xcorr']+6 for r in records]);op=np.array([r['onset_xcorr']+6 for r in records])
    result['baselines']={'zero_offset':{'accuracy':float((y==6).mean()),'mae_frames':float(np.abs(y-6).mean())},
                         'raw_xcorr':{'accuracy':float((bp==y).mean()),'mae_frames':float(np.abs(bp-y).mean())},
                         'onset_xcorr':{'accuracy':float((op==y).mean()),'mae_frames':float(np.abs(op-y).mean())}}
    result['mlp_minus_raw_xcorr']=bootstrap_difference(probs.argmax(1)==y,bp==y)
    result['raw_uncalibrated']=metrics(predict(X,p),y)
    failures=[]
    for i in np.where(probs.argmax(1)!=y)[0][:15]:
        failures.append({'seed':records[i]['seed'],'media_sha256':records[i]['media_sha256'],
                         'true_delay_frames':int(y[i]-6),'predicted_delay_frames':int(probs[i].argmax()-6),
                         'confidence':float(probs[i].max()),'xcorr':int(bp[i]-6)})
    result['failures']=failures
    rows=[{'seed':r['seed'],'true_delay':int(y[i]-6),'pred_delay':int(probs[i].argmax()-6),
           'confidence':float(probs[i].max()),'xcorr':r['xcorr'],'onset_xcorr':r['onset_xcorr'],
           'set_size':int(sets[i].sum()),'scorable':r['quality']['scorable']} for i,r in enumerate(records)]
    return result,rows


def run(out,quick=False):
    out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    sizes=[480,120,160,180] if quick else [1600,400,500,600]
    print('Generating independent media groups',sizes,flush=True)
    train=dataset(110000,sizes[0]);val=dataset(120000,sizes[1]);cal=dataset(130000,sizes[2]);test=dataset(140000,sizes[3])
    manifests={k:[{a:b for a,b in r.items() if a not in {'signals'}} for r in pack[2]] for k,pack in zip(['train','validation','calibration','test'],[train,val,cal,test])}
    all_hashes=[r['media_sha256'] for rows in manifests.values() for r in rows]
    assert len(set(all_hashes))==len(all_hashes)
    # Main architecture fixed before test. Three optimizer seeds; seed 7 published, no test-based seed selection.
    runs=[];main=None
    for seed in [7,19,31]:
        print('Training shared lag ranker seed',seed,flush=True)
        p,log,best_epoch=fit(train[0],train[1],val[0],val[1],seed=seed,epochs=180 if quick else 260)
        # Calibration split into disjoint temperature fit / threshold + conformal fit groups.
        split=len(cal[1])//2
        temp=temperature(forward(cal[0][:split],p)[0],cal[1][:split])
        cp=predict(cal[0][split:],p,temp);cy=cal[1][split:]
        threshold=choose_threshold(cp,cy);q=conformal_q(cp,cy)
        result,rows=evaluate(p,temp,q,threshold,*test)
        runs.append({'optimizer_seed':seed,'selected_epoch':best_epoch,'temperature':temp,'test':result})
        write_json(out/f'training-seed-{seed}.json',log)
        if seed==7:
            main=(p,temp,q,threshold)
            write_json(out/'test-predictions.json',rows)
    p,temp,q,threshold=main
    model={'schema_version':1,'model_type':'shared-lag-MLP','lag_frames':LAGS.tolist(),
           'fps':20,'sample_rate':8000,'feature_dim':12,'hidden':16,'optimizer_seed':7,
           'parameters':export(p),'temperature':temp,'threshold':threshold,'conformal_q':q,
           'alpha':.1,'training_size':sizes[0],'calibration_split':sizes[2]//2}
    write_json(out/'model.json',model);write_json(out/'split-manifest.json',manifests)
    results={'version':'0.1.0','quick':quick,'sizes':sizes,'runs':runs,'conditions':{},
             'protocol':'disjoint base-media seeds; validation checkpoint; calibration split in half; fixed seed 7 primary',
             'environment':{'python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__}}
    examples=[]
    for j,condition in enumerate(['id','noise','periodic','silent','distractor','drift','missing','long']):
        print('Evaluating',condition,flush=True)
        pack=test if condition=='id' else dataset(150000+j*1000,120 if quick else 240,condition)
        res,rows=evaluate(p,temp,q,threshold,*pack);results['conditions'][condition]=res
        write_json(out/f'{condition}-predictions.json',rows)
        s=pack[2][0]['signals'];pr=predict(lag_features(s)[None],p,temp)[0]
        local=[]
        for pos,window in windows(s):
            pp=predict(lag_features(window)[None],p,temp)[0]
            local.append({'start_seconds':pos/20,'end_seconds':(pos+32)/20,
                          'delay_ms':int((pp.argmax()-6)*50),'confidence':float(pp.max()),
                          'scorable':signal_quality(window)['scorable']})
        examples.append({'condition':condition,'seed':pack[2][0]['seed'],'signals':s,
                         'true_delay_frames':int(pack[1][0]-6),'features':pack[0][0].tolist(),
                         'probabilities':pr.tolist(),'windows':local})
    # Ablation: same ranking architecture, only raw correlation; not chosen as primary after test.
    mask=np.zeros(12);mask[0]=1
    ap,alog,aepoch=fit(train[0]*mask,train[1],val[0]*mask,val[1],seed=7,epochs=180 if quick else 260)
    results['ablation_raw_correlation_only']=metrics(predict(test[0]*mask,ap),test[1])
    write_json(out/'examples.json',examples)
    results['wall_seconds']=time.perf_counter()-start
    results['model_sha256']=hashlib.sha256((out/'model.json').read_bytes()).hexdigest()
    write_json(out/'results.json',results)
    print(json.dumps({k:{a:v for a,v in r.items() if a in ['accuracy','mae_frames','ece_10_equal_width','selective']} for k,r in results['conditions'].items()},indent=2),flush=True)
    print('Completed in',results['wall_seconds'],'seconds',flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--quick',action='store_true');a.add_argument('--out',type=Path,default=ROOT/'artifacts');args=a.parse_args();run(args.out,args.quick)
