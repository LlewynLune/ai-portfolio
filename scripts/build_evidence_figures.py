"""Rebuild 14 portfolio evidence figures from frozen Markdown reports.
No retraining / no invented metrics. Means aggregate only selected repeated seeds.
Each chart stores exact input rows, source hash and display definitions in manifest.
"""
from pathlib import Path
import json,html,hashlib,statistics
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/portfolio'
E=lambda s:html.escape(str(s))
CONFIG=[
('video-guard','VideoGuard: causal drift','projects/video-guard/artifacts/drift-localization/REPORT.md',1,'方法','F1',None,['raw','onset','mlp'],['Raw','Onset','MLP'],'Event F1 · tolerance 800 ms','Higher is better',['Time cost remains: matched MLP median alarm delay 1350 ms.','Synthetic RGB/PCM only; quiet gaps and ramps still fail.']),
('vision-cal','VisionCal: robustness','projects/vision-cal/artifacts/REPORT.md',0,'model','accuracy','group',['logistic','mlp_raw','mlp_temperature'],['Linear','MLP','Temp'],['clean','shift_right1px'],['Clean','1 px shift'],'Accuracy · held-out image IDs','Higher is better',['Calibration does not remove distribution-shift errors.','Public 8 x 8 images; not a deployed OCR model.']),
('novelty-lab','NoveltyLab: detection','projects/novelty-lab/artifacts/REPORT.md',0,'模型','Recall',None,['centroid_distance','isolation_forest','one_class_svm'],['Distance','IForest','OCSVM'],'Recall · fixed validation threshold','Higher is better',['Normal train / validation: 35 / 12; test unknowns: 119.','Class novelty is not an industrial fault label.']),
('textguard','TextGuard: held-out F1','projects/textguard/artifacts/REPORT.md',0,'模型','F1',None,['majority','multinomial_nb','tfidf_logistic'],['Majority','NB','Logistic'],'F1 · 1020 held-out texts','Higher is better',['Vocabulary fit on train; threshold selected on validation.','Old English SMS dataset; no modern fraud deployment claim.']),
('reliability-lab','FlowBench: crash recovery','projects/reliability-lab/results/advanced/REPORT.md',0,'策略','重复副作用','崩溃边界',['retry','resilient'],['Retry','Resilient'],['after_commit'],['After commit'],'Duplicate side effects · controlled crash','Lower is better',['Both recover 4 tasks; idempotence removes duplicated effects.','Only experiment subprocesses; not power-loss resilience.']),
('cite-rag','CiteRAG: hard queries','projects/cite-rag/artifacts/REPORT.md',0,'方法','Recall@3','集合',['bm25','char','hybrid'],['BM25','Char','RRF'],['challenge'],['Challenge'],'Recall@3 · 4 authored hard queries','Higher is better',['Valid citation IDs do not prove semantic support.','15 authored documents / 25 questions; LLM not invoked.']),
('tiny-attention','TinyAttention: ablation','projects/tiny-attention/artifacts/REPORT.md',0,'model','accuracy','group',['causal_attention','no_attention_ablation'],['Attention','No-attn'],['heldout3pairs','length5pairs_ood'],['3 pairs','5 pairs OOD'],'Accuracy · synthetic key-value lookup','Higher is better',['Longer inputs degrade performance; failures are retained.','10226 trainable parameters; not language pretraining.']),
('lora-lab','LoRA: adaptation / forgetting','projects/lora-lab/artifacts/REPORT.md',0,'model','accuracy','group',['frozen','lora_r4','full_finetune'],['Frozen','Rank 4','Full FT'],['test_shift1','original_task_retention'],['New task','Old task'],'Accuracy · shared TinyAttention base','Higher is better',['Low-rank learning still forgets the original task.','Rank 4: 712 trainable parameters; Full FT: 10226.']),
('dpo-lab','DPO: wins vs correct answers','projects/dpo-lab/artifacts/REPORT.md',0,'model','pair_win_rate','group',['reference','dpo_beta0.1','sft_chosen'],['Reference','DPO 0.1','SFT'],['heldout_pairs'],['Held-out'],'Pair win rate · rule-based preference','Higher is better',['DPO 0.1: win 0.990 vs chosen top1 0.422; KL 6.231.','Single-token synthetic preference; not human alignment.']),
('moe-lab','SparseMoE: dense comparison','projects/moe-lab/artifacts/REPORT.md',0,'model','rmse','group',['top1_lb0.03','dense_active16','dense_total64'],['Top1 + LB','Dense 16','Dense 64'],['heldout_uniform'],['Held-out'],'RMSE · synthetic nonlinear regression','Lower is better',['Sparse routing does not automatically beat dense baselines.','272 total / 77 active-estimate parameters; no speed claim.']),
('spec-decode','SpecDecode: actual CPU cost','projects/spec-decode/artifacts/REPORT.md',0,'k','speculative_ms',None,['2','4'],['k = 2','k = 4'],'Speculative time (ms) · 3 paired repeats','Lower is better',['Baseline ~21 ms; speculative path is slower in this setup.','All 8 prompts match greedy target output; no GPU claims.']),
('circuit-id','CircuitID: out-of-range tau','projects/circuit-id/artifacts/REPORT.md',0,'model','mae','group',['physical_curve_fit','ridge','mlp'],['Physics','Ridge','MLP'],['id','slow_ood'],['In range','Slow OOD'],'MAE (ms) · mean of 3 test seeds','Lower is better',['Learning helps in range; physics extrapolates more reliably.','Ideal RC simulation; only tau = RC is identifiable.']),
('channel-est','ChannelEst: estimation error','projects/channel-est/artifacts/REPORT.md',0,'model','nmse','group',['linear_interpolation','learned_ridge','known_prior_lmmse4'],['Linear','Learned','LMMSE'],['snr15','long_delay_ood'],['SNR 15','Delay OOD'],'NMSE · mean of 3 test seeds','Lower is better',['LMMSE uses known noise and prior: privileged comparator.','Ideal frequency-domain simulation; no SDR / RF hardware.']),
('power-scope','PowerScope: cooling drift','projects/power-scope/artifacts/REPORT.md',0,'model','rmse','group',['persistence','ridge_full','ridge_no_plan'],['Persist','Plan','No plan'],['chronological_test','cooling_drift_ood'],['Time test','Drift OOD'],'RMSE (kW) · chronological holdout','Lower is better',['Plan features help jumps, but cooling drift reverses gains.','Synthetic time series; read-only, not equipment control.'])]

def tables(text):
    blocks=[];cur=[]
    for line in text.splitlines()+['']:
        if line.startswith('|'):cur.append([v.strip() for v in line.strip('|').split('|')])
        elif cur:
            if len(cur)>2:blocks.append([dict(zip(cur[0],r)) for r in cur[2:]])
            cur=[]
    return blocks

def figure(folder,title,metric,direction,models,series,values,notes):
    W,H=800,480;s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"><title>{E(title)}</title><desc>{E(metric)}. {E(direction)}. Source: frozen local experiment report.</desc><rect width="800" height="480" fill="white"/><style>text{{font-family:Arial,Helvetica,sans-serif}}.heading{{fill:#13386c;font-weight:bold}}.note{{fill:#59697b}}</style>']
    def text(x,y,t,size=17,cls='note',anchor='start'):s.append(f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" text-anchor="{anchor}">{E(t)}</text>')
    text(28,35,title,26,'heading');text(28,63,metric,17);text(772,63,direction,14,'note','end')
    colors=['#214e85','#de9560'];mx=max(max(row) for row in values);maxval=1 if mx<=1 else mx*1.22; maxval=max(maxval,.01)
    x0,y0,pw,ph=65,105,690,230
    for i in range(5):
        v=maxval*i/4;y=y0+ph-ph*i/4;s.append(f'<line x1="{x0}" x2="{x0+pw}" y1="{y}" y2="{y}" stroke="#e7ecf2"/>');text(x0-9,y+5,f'{v:.2f}' if maxval<=5 else f'{v:.0f}',14,anchor='end')
    block=pw/len(models);bw=min(62,(block-45)/len(series))
    for i,m in enumerate(models):
        center=x0+block*(i+.5)
        for j,ser in enumerate(series):
            v=values[j][i];h=ph*v/maxval;x=center+(j-(len(series)-1)/2)*bw-bw*.42
            s.append(f'<rect x="{x:.2f}" y="{y0+ph-h:.2f}" width="{bw*.84:.2f}" height="{max(h,1.5):.2f}" rx="2" fill="{colors[j]}"/>');text(x+bw*.42,y0+ph-h-8,f'{v:.3f}' if v<10 else f'{v:.1f}',16,'heading','middle')
        text(center,y0+ph+25,m,18,'note','middle')
    for j,ser in enumerate(series):
        x=28+j*230;s.append(f'<rect x="{x}" y="382" width="15" height="15" fill="{colors[j]}"/>');text(x+23,395,ser,16)
    text(28,429,notes[0],16);text(28,455,notes[1],15)
    s.append('</svg>');(OUT/(folder+'-evidence.svg')).write_text(''.join(s))

def build():
    manifest=[]
    for cfg in CONFIG:
        folder,title,path,idx,mkey,metric,gkey,modelids,labels,*tail=cfg
        if gkey: groupids,series,metriclabel,direction,notes=tail
        else: groupids,series,metriclabel,direction,notes=[None],['Frozen test'],*tail
        source=ROOT/path;raw=source.read_text();rows=tables(raw)[idx];values=[];selected=[]
        for group in groupids:
            v=[]
            for m in modelids:
                hits=[r for r in rows if r[mkey]==m and (gkey is None or r[gkey]==group)]
                assert hits,(folder,group,m)
                vals=[float(r[metric]) for r in hits];v.append(statistics.mean(vals));selected.extend(hits)
            values.append(v)
        figure(folder,title,metriclabel,direction,labels,series,values,notes)
        manifest.append(dict(project=folder,source=path,sha256=hashlib.sha256(source.read_bytes()).hexdigest(),metric=metric,group_column=gkey,model_column=mkey,models=modelids,model_labels=labels,groups=groupids,series_labels=series,values=values,aggregation='mean of available selected repetitions; no cherry-pick',rows=selected,notes=notes))
    (OUT/'evidence-figures.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('Rebuilt',len(manifest),'vector evidence figures from frozen reports')
if __name__=='__main__':build()
