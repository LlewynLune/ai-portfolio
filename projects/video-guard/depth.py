"""VideoGuard alarm-latency constrained event matching; no post-hoc retuning."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from depth_support import *
from videoguard.drift import detect
HERE=Path(__file__).resolve().parent
def latency_match(truth,alarms,tolerance=16,delay_budget=20):
    truth=sorted(truth);alarms=sorted(alarms,key=lambda a:a['estimated_frame']);n,m=len(truth),len(alarms);dp=np.zeros((n+1,m+1),int)
    for i in range(1,n+1):
        for j in range(1,m+1):
            a=alarms[j-1];ok=abs(a['estimated_frame']-truth[i-1])<=tolerance and 0<=a['alarm_frame']-truth[i-1]<=delay_budget;dp[i,j]=max(dp[i-1,j],dp[i,j-1],dp[i-1,j-1]+int(ok))
    tp=int(dp[n,m]);return dict(tp=tp,fp=m-tp,fn=n-tp)
def main():
    base=HERE/'artifacts/drift-localization';old=load(base/'results.json');config=old['configs'];rows=[];summaries=[];sources=[base/'results.json']
    for condition in ['step','ramp','quiet_gap','multiple','exposure']:
        source=base/(condition+'-records.json');sources.append(source);records=load(source)
        for method in ['raw','onset','mlp']:
            for budget in [10,20,30,40]:
                counts=[]
                for r in records:
                    alarms=detect(r['trajectory'],method,**config[method]);stats=latency_match(r['changes'],alarms,16,budget);counts.append(stats);rows.append(dict(model=method,condition=f'{condition}_budget{budget*50}ms',index=r['seed'],correct=stats['fn']==0 and stats['fp']==0,loss=0.,confidence=0.,**stats,delay_budget_ms=budget*50))
                tp=sum(c['tp'] for c in counts);fp=sum(c['fp'] for c in counts);fn=sum(c['fn'] for c in counts);summaries.append(dict(condition=condition,method=method,delay_budget_ms=budget*50,tp=tp,fp=fp,fn=fn,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0))
    save(HERE,'VideoGuard latency-bounded drift events','Frozen160-frame trajectories,5 challenging groups×120 clips; fixed validated detector configs. Require both800ms boundary tolerance and500/1000/1500/2000ms emitted-alarm delay. One-to-one chronological DP matching.',rows,['A good retrospective boundary can still miss a real-time deadline; explicit late alarms lose credit.','No future-window lookahead or new thresholds tuned on test.','Reanalysis of existing clips, not independent new media or real-video evidence.'],extra=dict(latency_surface=summaries,configs=config),sources=sources)
if __name__=='__main__':main()
