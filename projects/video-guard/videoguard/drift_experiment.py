from pathlib import Path
import json,time,hashlib,itertools
import numpy as np
from .experiment import ROOT,write_json
from .drift_data import make_drift
from .features import extract
from .data import content_hash
from .drift import lag_trajectory,detect,match_events,summarize

OUT=ROOT/'artifacts/drift-localization';GROUPS=['stable','step','negative','small_step','ramp','multiple','quiet_gap','noise','exposure','silent']


def records(model,start,n,condition):
    out=[]
    for seed in range(start,start+n):
        f=make_drift(seed,condition);c=f.clip;s=extract(c.frames,c.audio,c.fps,c.sample_rate)
        out.append({'seed':seed,'media_sha256':content_hash(c),'condition':condition,'changes':f.change_frames,
                    'delay_track':f.delay_track.tolist(),'trajectory':lag_trajectory(s,model),
                    'signals':s if seed==start else None})
    return out


def run():
    OUT.mkdir(exist_ok=True);t=time.perf_counter();mp=ROOT/'artifacts/model.json';model=json.loads(mp.read_text())
    # Validation protocol fixed before test; raw/onset confidence not same quantity as MLP.
    validation=[]
    for j,g in enumerate(['stable','step','negative','quiet_gap']):validation+=records(model,700000+j*1000,40,g)
    grid=[];chosen={}
    for method in ['raw','onset','mlp']:
        for conf,jump,patience in itertools.product(([.3,.5,.7] if method!='mlp' else [.6,.8,.9]),[1,2],[1,2,3]):
            cfg={'confidence':conf,'min_jump':jump,'patience':patience};score=summarize(validation,method,cfg)
            grid.append({'method':method,'config':cfg,'validation':score})
        candidates=[r for r in grid if r['method']==method and (r['validation']['stable_false_alarm_rate'] or 0)<=.1]
        if not candidates:candidates=[r for r in grid if r['method']==method]
        selected=max(candidates,key=lambda r:(r['validation']['f1'],-r['validation']['fp'],-r['config']['confidence'],-r['config']['patience']))
        chosen[method]=selected['config']
    results={'version':'0.3.0','model_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'configs':chosen,
             'validation_n':len(validation),'methods':['raw','onset','mlp'],'groups':{},
             'protocol':'validation F1 subject to stable false alarm <=10%; fixed tie break; untouched test seeds; causal trailing windows size32/stride4; event tolerance800ms',
             'scope':'self-owned rendered RGB/PCM; structural output-time boundary; no real video data'}
    write_json(OUT/'validation-grid.json',grid);write_json(OUT/'validation-records.json',validation)
    all_records={};examples=[]
    for j,g in enumerate(GROUPS):
        print('Localization test',g,flush=True);rows=records(model,800000+j*1000,120,g);all_records[g]=rows
        results['groups'][g]={m:summarize(rows,m,chosen[m]) for m in chosen}
        write_json(OUT/f'{g}-records.json',rows)
        e=rows[0];examples.append({**e,'predictions':{m:detect(e['trajectory'],m,**chosen[m]) for m in chosen}})
    # Repeat independently with same fixed detector config, no repeated selection.
    repeats=[]
    for rep in range(3):
        rows=[]
        for j,g in enumerate(['stable','step','negative','quiet_gap','noise']):rows+=records(model,900000+rep*10000+j*1000,40,g)
        repeats.append({'repeat':rep,'methods':{m:summarize(rows,m,chosen[m]) for m in chosen}})
        write_json(OUT/f'repeat-{rep}.json',rows)
    results['repeats']=repeats
    combined=sum(all_records.values(),[])
    results['overall']={m:summarize(combined,m,chosen[m]) for m in chosen}
    results['tolerance_sweep']={str(tol*50):{m:summarize(combined,m,chosen[m],tol) for m in chosen} for tol in [4,8,16,24]}
    # Clip-level paired uncertainty: 300 resamples; keep miss penalty, don't compare matched times only.
    paired=[]
    for rows in all_records.values():
        for r in rows:
            flags={m:match_events(r['changes'],detect(r['trajectory'],m,**chosen[m])) for m in chosen}
            paired.append({m:float(flags[m]['fn']==0 and flags[m]['fp']==0) for m in chosen})
    rng=np.random.default_rng(402);d=np.array([x['mlp']-x['onset'] for x in paired]);boot=d[rng.integers(0,len(d),(1000,len(d)))].mean(1)
    results['mlp_minus_onset_exact_clip_success']={'difference':float(d.mean()),'ci95':np.quantile(boot,[.025,.975]).tolist(),'definition':'all changes matched, no extra alarms; negatives require no alarms'}
    results['seconds']=time.perf_counter()-t
    write_json(OUT/'results.json',results);write_json(OUT/'examples.json',examples)
    print(json.dumps(results['overall'],indent=2),flush=True);print('Seconds',results['seconds'],flush=True)

if __name__=='__main__':run()
