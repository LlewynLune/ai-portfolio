"""CPU-only independent audit of frozen Qwen samples and evaluation. No model download.
Replays the sampling from logged probabilities, not the MLX gradient computation.
"""
import hashlib,json,math
from pathlib import Path


def load(p):return json.loads(p.read_text())


def verify(root):
    root=Path(root);results=[];reference_data=None
    for name,source in [('qwen-policy',root/'qwen-policy/runner-original.py'),('qwen-centered',root.parent/'laminar_lab/llm_policy.py')]:
        folder=root/name;data=load(folder/'dataset.json');summary=load(folder/'summary.json')
        assert hashlib.sha256(source.read_bytes()).hexdigest()==summary['source_sha256']
        if reference_data is None:reference_data=data
        assert data==reference_data
        seen=set()
        for split,n in [('train',96),('test',64),('ood',64)]:
            assert len(data[split])==n and sum(r['y'] for r in data[split])==n//2
            for r in data[split]:
                a,b=tuple(r['a']),tuple(r['b']);key=tuple(sorted([a,b]));assert key not in seen and sum(a)!=sum(b) and int(sum(b)>sum(a))==r['y'];seen.add(key)
        def eval_stats(rows):
            out={}
            for split in ['test','ood']:
                assert len(rows[split])==len(data[split]);p_correct=[];correct=0;predict_b=0
                for i,r in enumerate(rows[split]):
                    p=r['p'];y=data[split][i]['y'];assert r['index']==i and r['y']==y and abs(sum(p)-1)<2e-6 and all(0<v<1.000001 for v in p)
                    predicted=int(p[1]>p[0]);assert r['correct']==int(predicted==y);correct+=r['correct'];predict_b+=predicted;p_correct.append(p[y])
                out[split]={'correct':correct,'n':len(p_correct),'predict_b':predict_b,'target_probability':sum(p_correct)/len(p_correct),'nll':-sum(math.log(x) for x in p_correct)/len(p_correct)}
            return out
        baseline=eval_stats(summary['baseline_rows']);paired={}
        entries=sorted(folder.glob('*-lag*.json'));assert len(entries)==6
        for p in entries:
            r=load(p);seed,lag=r['seed'],r['lag'];assert lag in [0,2] and seed in [7,19,41]
            chain=[r['initial_adapter_sha256']];count=0;multi=0;seen_ids=set();var=0;grad=0;max_clip=0.;max_ratio=1.
            assert len(r['updates'])==12 and r['adapter_parameters']==81920
            for t,u in enumerate(r['updates']):
                assert u['step']==t+1 and u['learner_version']==t and u['behavior_version']==max(0,t-lag)
                assert chain[u['behavior_version']]==u['behavior_sha256'];chain.append(u['result_sha256'])
                multi+=int(u['behavior_version']!=t);ids=u['train_ids'];assert len(ids)==8 and not seen_ids.intersection(ids);seen_ids.update(ids)
                for j,i in enumerate(ids):
                    q=u['behavior_probs'][j];a=u['actions'][j];z=u['uniforms'][j];rew=u['reward'][j];old=u['behavior_logp'][j];y=data['train'][i]['y']
                    assert abs(sum(q)-1)<2e-6 and len(a)==len(z)==len(rew)==len(old)==8
                    for action,uniform,reward,logp in zip(a,z,rew,old):
                        assert 0<=uniform<1 and action==int(uniform>=q[0]) and reward==int(action==y) and abs(logp-math.log(q[action]))<1e-7
                        count+=1
                    var+=int(len(set(rew))>1)
                assert len(u['optimizer_steps'])==2
                for o in u['optimizer_steps']:
                    assert 0<=o['clip_fraction']<=1 and o['ratio_min']>0 and o['ratio_max']>=o['ratio_min'] and math.isfinite(o['loss']) and math.isfinite(o['grad_norm'])
                    grad+=int(o['grad_norm']>1e-4);max_clip=max(max_clip,o['clip_fraction']);max_ratio=max(max_ratio,o['ratio_max'])
            assert seen_ids==set(range(96)) and chain[-1]==r['final_adapter_sha256']
            paired.setdefault(seed, {})[lag]=(r['initial_adapter_sha256'],[(u['train_ids'],u['uniforms']) for u in r['updates']]);evaluation=eval_stats(r['eval_rows'])
            saved=next(x for x in summary['runs'] if x['seed']==seed and x['lag']==lag)
            for split,ev in evaluation.items():
                assert r['final'][split]==saved['final'][split] and abs(ev['correct']/ev['n']-saved['final'][split]['accuracy'])<1e-9
            results.append(dict(protocol=name,seed=seed,lag=lag,action_draws=count,informative_groups=var,groups=96,stale_updates=multi,grad_above_1e_4=grad,max_clip_fraction=max_clip,largest_ratio=max_ratio,baseline=baseline,final=evaluation,adapter_changed=chain[0]!=chain[-1]))
        assert all(p[0]==p[2] for p in paired.values())
    return {'dataset_exact_or_swapped_overlap':0,'deterministic_sum_parser_accuracy':1.0,'runs':results,'scope':'Recompute sampling, reward, version chain and evaluation from published logs. No MLX weight replay; hashes link recorded versions, not an independent signature.'}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--artifacts',type=Path,default=Path('artifacts'));p.add_argument('--output',type=Path);a=p.parse_args();result=verify(a.artifacts)
    if a.output:
        with a.output.open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
    print(json.dumps(result,ensure_ascii=False))
