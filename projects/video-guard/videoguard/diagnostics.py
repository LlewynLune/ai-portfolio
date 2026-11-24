"""Held-out diagnostic gates and negative controls; NOT used to tune the model.
A conservative operational floor of .9 is fixed for this diagnostic protocol.
Unknown source/meaning and any real upload always require human review.
"""
import json
import numpy as np
from .data import make_clip,shift
from .features import extract,lag_features,signal_quality,windows
from .model import predict
from .experiment import ROOT,write_json


def decision(signals,model):
    p=model['parameters'];t=model['temperature'];prob=predict(lag_features(signals)[None],p,t)[0]
    lag=int(prob.argmax()-6);candidates=np.where(prob>=1-model['conformal_q']-1e-12)[0]-6
    locals=[]
    for i,s in windows(signals):
        pr=predict(lag_features(s)[None],p,t)[0]
        locals.append({'start':i,'lag':int(pr.argmax()-6),'confidence':float(pr.max()),'energy':signal_quality(s)['evidence_energy']})
    local_lags=[x['lag'] for x in locals if x['confidence']>=.9 and x['energy']>.008]
    disagreement=len(local_lags)>=2 and max(local_lags)-min(local_lags)>=2
    gate=signal_quality(signals)['scorable'] and prob.max()>=.9 and len(candidates)==1 and not disagreement
    return {'accept':bool(gate),'lag':lag,'confidence':float(prob.max()),'set':candidates.tolist(),
            'disagreement':disagreement,'windows':locals}


def run():
    m=json.loads((ROOT/'artifacts/model.json').read_text());result={'operational_floor':.9,'not_used_for_model_selection':True,'conditions':{}}
    for condition in ['id','noise','periodic','silent','distractor','drift','missing','long']:
        rows=[]
        for seed in range(210000,210240):
            c=make_clip(seed,condition=condition);s=extract(c.frames,c.audio,20,8000);r=decision(s,m)
            r.update({'seed':seed,'true_first_half_delay':c.delay,'correct':r['lag']==c.delay});rows.append(r)
        accepted=[r for r in rows if r['accept']]
        result['conditions'][condition]={'n':len(rows),'accepted':len(accepted),'coverage':len(accepted)/len(rows),
                                         'accepted_error':float(np.mean([not r['correct'] for r in accepted])) if accepted else None,
                                         'window_disagreement_rate':float(np.mean([r['disagreement'] for r in rows]))}
        write_json(ROOT/f'artifacts/diagnostic-{condition}.json',rows)
    result['negative_controls']={}
    for name in ['reversed_audio','unrelated_audio','range_out','low_visual_evidence']:
        rows=[]
        for seed in range(220000,220240):
            c=make_clip(seed)
            if name=='reversed_audio':c.audio=c.audio[::-1].copy()
            elif name=='unrelated_audio':c.audio=make_clip(seed+1000).audio
            elif name=='range_out':c=make_clip(seed,delay=10)
            elif name=='low_visual_evidence':c.frames=.12+.05*(c.frames-.12)
            r=decision(extract(c.frames,c.audio,20,8000),m);rows.append(r)
        result['negative_controls'][name]={'n':len(rows),'incorrect_unique_estimate_rate':float(np.mean([r['accept'] for r in rows])),
                                          'note':('This is acceptance under deliberately attenuated visual evidence, NOT necessarily incorrect delay. Metric name retained for compatibility; do not interpret as error rate.' if name=='low_visual_evidence' else 'No valid stable in-range alignment in this negative control; accepted unique estimates are unsupported.')}
        write_json(ROOT/f'artifacts/negative-{name}.json',rows)
    write_json(ROOT/'artifacts/diagnostics.json',result)
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':run()
