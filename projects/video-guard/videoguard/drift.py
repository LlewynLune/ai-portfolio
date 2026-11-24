"""Causal trailing-window detector; no whole-clip normalization or future lookahead.
Estimated boundary (window-center) != alarm emitted at end of observation window.
"""
import numpy as np
from .features import lag_features,baseline,corr,overlap,positive_diff,signal_quality
from .model import predict
from .data import LAGS


def lag_trajectory(signals,model,size=32,stride=4):
    if size<24 or stride<=0:raise ValueError('invalid window')
    n=len(signals['visual']);rows=[]
    for end in range(size,n+1,stride):
        start=end-size;s={k:list(v[start:end]) for k,v in signals.items()}
        # Recompute onsets inside each trailing window; first point has no past diff.
        s['visual_onset']=positive_diff(np.array(s['visual'])).tolist();s['audio_onset']=positive_diff(np.array(s['audio'])).tolist()
        p=predict(lag_features(s)[None],model['parameters'],model['temperature'])[0]
        raw=[];onset=[]
        for k in LAGS:
            raw.append(corr(*overlap(np.array(s['visual']),np.array(s['audio']),int(k))))
            onset.append(corr(*overlap(np.array(s['visual_onset']),np.array(s['audio_onset']),int(k))))
        idx=int(np.argmax(raw));oi=int(np.argmax(onset));mi=int(p.argmax())
        rows.append({'start':start,'end':end,'center':start+size/2,'energy':signal_quality(s)['evidence_energy'],
                     'raw_lag':idx-6,'raw_confidence':float(np.clip(raw[idx],0,1)),
                     'onset_lag':oi-6,'onset_confidence':float(np.clip(onset[oi],0,1)),
                     'mlp_lag':mi-6,'mlp_confidence':float(p[mi])})
    return rows


def detect(trajectory,method='mlp',confidence=.9,min_jump=2,patience=2):
    if method not in ['mlp','raw','onset'] or not 0<=confidence<=1 or min_jump<1 or patience<1:raise ValueError('bad detector config')
    state=None;candidate=None;count=0;first=None;alarms=[];recent=[]
    for r in trajectory:
        valid=r['energy']>.008 and r[method+'_confidence']>=confidence
        if not valid:candidate=None;count=0;first=None;continue
        lag=r[method+'_lag']
        if state is None:
            recent.append(lag)
            if len(recent)>=patience:state=int(np.median(recent[-patience:]));recent=[]
            continue
        if abs(lag-state)<min_jump:candidate=None;count=0;first=None;continue
        if candidate is None or abs(lag-candidate)>=min_jump:
            candidate=lag;count=1;first=r
        else:count+=1
        if count>=patience:
            alarms.append({'estimated_frame':float(first['center']),'alarm_frame':int(r['end']),
                           'from_lag':int(state),'to_lag':int(candidate),'confidence':float(r[method+'_confidence'])})
            state=candidate;candidate=None;count=0;first=None
    return alarms


def match_events(truth,alarms,tolerance=16):
    """Maximum chronological one-to-one matching via DP. No early alarm gets credit.
    Optimize matches first, then localization error. Extra predictions remain false positives.
    """
    truth=sorted(truth);alarms=sorted(alarms,key=lambda x:x['estimated_frame']);n=len(truth);m=len(alarms)
    dp=[[None]*(m+1) for _ in range(n+1)];dp[0][0]=(0,0.,[])
    def better(a,b):
        if b is None:return a
        return a if (a[0],-a[1])>(b[0],-b[1]) else b
    for i in range(n+1):
        for j in range(m+1):
            cur=dp[i][j]
            if cur is None:continue
            if i<n:dp[i+1][j]=better(cur,dp[i+1][j])
            if j<m:dp[i][j+1]=better(cur,dp[i][j+1])
            if i<n and j<m:
                err=abs(alarms[j]['estimated_frame']-truth[i])
                if err<=tolerance and alarms[j]['alarm_frame']>=truth[i]:
                    nxt=(cur[0]+1,cur[1]+err,cur[2]+[(i,j)]);dp[i+1][j+1]=better(nxt,dp[i+1][j+1])
    pairs=dp[n][m][2]
    return {'tp':len(pairs),'fp':m-len(pairs),'fn':n-len(pairs),
            'matches':[{'truth_frame':truth[i],**alarms[j],'error_frames':abs(alarms[j]['estimated_frame']-truth[i]),
                        'detection_delay_frames':alarms[j]['alarm_frame']-truth[i]} for i,j in pairs]}


def summarize(records,method,config,tolerance=16):
    tp=fp=fn=0;matched=[];stable=0;stable_alarm=0;any_truth=0;detected=0
    for r in records:
        alarms=detect(r['trajectory'],method,**config);s=match_events(r['changes'],alarms,tolerance)
        tp+=s['tp'];fp+=s['fp'];fn+=s['fn'];matched.extend(s['matches'])
        if not r['changes']:stable+=1;stable_alarm+=bool(alarms)
        else:any_truth+=1;detected+=bool(s['tp'])
    precision=tp/(tp+fp) if tp+fp else 0.;recall=tp/(tp+fn) if tp+fn else 0.;f1=2*precision*recall/(precision+recall) if precision+recall else 0.
    return {'n':len(records),'tp':tp,'fp':fp,'fn':fn,'precision':precision,'recall':recall,'f1':f1,
            'stable_clips':stable,'stable_false_alarm_rate':stable_alarm/stable if stable else None,
            'positive_clip_match_rate':detected/any_truth if any_truth else None,
            'matched_localization_mae_ms':float(np.mean([x['error_frames'] for x in matched])*50) if matched else None,
            'matched_alarm_delay_median_ms':float(np.median([x['detection_delay_frames'] for x in matched])*50) if matched else None,
            'matched_alarm_delay_p90_ms':float(np.quantile([x['detection_delay_frames'] for x in matched],.9)*50) if matched else None,
            'timing_denominator':'matched events only; misses reported separately','tolerance_ms':tolerance*50}
