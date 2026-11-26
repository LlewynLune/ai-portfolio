"""Offline Qwen LoRA policy gradients on a synthetic contextual bandit (one-token output).
Single GPU, sequential forward passes. Version lag is injected, not async GPU execution.
"""
import argparse, hashlib, json, platform, time
from pathlib import Path
import numpy as np

MODEL='mlx-community/Qwen3-4B-Instruct-2507-4bit'
REV='50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b'
LABELS=('A','B')
TEMPERATURE=2.0


def dataset():
    # Unique input tuples, balanced within each split; length shift is deliberate.
    rng=np.random.default_rng(63019);seen=set();out={}
    for split,n,length,limit in [('train',96,3,9),('test',64,3,9),('ood',64,5,19)]:
        rows=[]
        for y in range(2):
            part=[]
            while len(part)<n//2:
                a=tuple(int(x) for x in rng.integers(1,limit+1,length));b=tuple(int(x) for x in rng.integers(1,limit+1,length))
                key=(a,b);reverse=(b,a)
                if key in seen or reverse in seen or sum(a)==sum(b) or int(sum(b)>sum(a))!=y:continue
                seen.add(key);part.append(dict(a=a,b=b,y=y))
            rows.extend(part)
        out[split]=[rows[i] for i in rng.permutation(n)]
    return out


def weights_hash(weights):
    h=hashlib.sha256()
    for k,v in sorted(weights):h.update(k.encode());h.update(np.asarray(v,dtype='<f4').tobytes())
    return h.hexdigest()


def run(args):
    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    from mlx.utils import tree_flatten,tree_unflatten
    from mlx_lm import load
    from mlx_lm.tuner.utils import linear_to_lora_layers
    path=Path(args.model)
    if path.name!=REV or not (path/'model.safetensors').is_file():raise ValueError('Pinned offline weights required')
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    data=dataset();(out/'dataset.json').write_text(json.dumps(data,indent=2))
    model,tok=load(str(path),tokenizer_config={'trust_remote_code':False,'local_files_only':True});model.freeze();mx.random.seed(2718)
    linear_to_lora_layers(model,2,dict(rank=4,scale=8.,dropout=0.,keys=['self_attn.q_proj','self_attn.v_proj']))
    model.eval();mx.eval(model.parameters())
    label_ids=[tok.encode(x,add_special_tokens=False) for x in LABELS]
    if any(len(x)!=1 for x in label_ids):raise ValueError(label_ids)
    label_ids=[x[0] for x in label_ids];label_tensor=mx.array(label_ids)
    def snapshot():
        weights=tree_flatten(model.trainable_parameters())
        if set(k.split('.')[-1] for k,_ in weights)!={'lora_a','lora_b'}:raise ValueError('unexpected trainable parameters')
        weights=[(k,mx.array(v.astype(mx.float32))) for k,v in weights];mx.eval(*[v for _,v in weights]);return weights
    def restore(weights):model.update(tree_unflatten(weights))
    initial=snapshot()
    def encode(row):
        text=(f"Column A: {', '.join(map(str,row['a']))}\nColumn B: {', '.join(map(str,row['b']))}\n"
              'Add each column. Which column has the larger sum? Answer only A or B.')
        return tok.apply_chat_template([dict(role='user',content=text)],tokenize=True,add_generation_prompt=True)
    encoded={k:[encode(r) for r in v] for k,v in data.items()}
    def inputs(seq):
        n=max(map(len,seq));pad=tok.eos_token_id
        return mx.array([s+[pad]*(n-len(s)) for s in seq]),mx.array([len(s)-1 for s in seq])
    def logits(x,end):
        z=model(x);return z[mx.arange(x.shape[0]),end][:,label_tensor].astype(mx.float32)/TEMPERATURE
    def prob(x,end):
        p=mx.softmax(logits(x,end),axis=-1);mx.eval(p);return np.asarray(p).astype(float)
    def evaluate():
        result={}
        for split in ['test','ood']:
            rows=[]
            for i in range(0,len(data[split]),8):
                for j,p in enumerate(prob(*inputs(encoded[split][i:i+8]))):
                    y=data[split][i+j]['y'];rows.append(dict(index=i+j,y=y,p=p.tolist(),correct=int(p.argmax()==y)))
            result[split]=rows
        return result
    def stat(rows):
        return {s:{'accuracy':float(np.mean([r['correct'] for r in rs])), 'target_probability':float(np.mean([r['p'][r['y']] for r in rs])),'n':len(rs)} for s,rs in rows.items()}
    baseline=evaluate();print('Frozen BASE',stat(baseline),flush=True)
    def objective(x,ends,actions,advantages,old,ref):
        logp=nn.log_softmax(logits(x,ends),axis=-1);p=mx.exp(logp)
        chosen=mx.take_along_axis(logp,actions,axis=1);ratio=mx.exp(chosen-old)
        surrogate=mx.minimum(ratio*advantages,mx.clip(ratio,.8,1.2)*advantages)
        kl=mx.mean(mx.sum(p*(logp-ref),axis=-1));return -mx.mean(surrogate)+.04*kl
    grad_fn=nn.value_and_grad(model,objective)
    results=[]
    for seed in args.seeds:
        order=np.random.default_rng(seed).permutation(len(data['train'])).tolist()
        for lag in args.lags:
            restore(initial);opt=optim.Adam(learning_rate=2e-4,bias_correction=True);versions=[snapshot()];updates=[];rng=np.random.default_rng(seed+7000)
            for step in range(args.updates):
                ids=order[step*8:(step+1)*8];x,ends=inputs([encoded['train'][i] for i in ids]);start=time.perf_counter()
                behavior=max(0,step-lag);restore(versions[behavior]);p=prob(x,ends);u=rng.random((len(ids),8));actions=(u>=p[:,0,None]).astype(int)
                y=np.array([data['train'][i]['y'] for i in ids]);reward=(actions==y[:,None]).astype(float);adv=(reward-reward.mean(1,keepdims=True))/(reward.std(1,keepdims=True)+1e-6)
                old=np.log(np.take_along_axis(p,actions,1));restore(initial);ref=nn.log_softmax(logits(x,ends),axis=-1);mx.eval(ref);restore(versions[-1]);tr=[]
                for inner in range(2):
                    before=prob(x,ends);ratios=np.take_along_axis(before,actions,1)/np.exp(old)
                    val,g=grad_fn(x,ends,mx.array(actions),mx.array(adv,dtype=mx.float32),mx.array(old,dtype=mx.float32),ref);mx.eval(val,g)
                    norm=float(mx.sqrt(sum(mx.sum(t.astype(mx.float32)**2) for _,t in tree_flatten(g))).item())
                    if not np.isfinite(norm) or not np.isfinite(val.item()):raise FloatingPointError('nonfinite gradient')
                    opt.update(model,g);mx.eval(model.parameters(),opt.state)
                    tr.append(dict(loss=float(val.item()),grad_norm=norm,ratio_min=float(ratios.min()),ratio_max=float(ratios.max()),clip_fraction=float(np.mean(((adv>0)&(ratios>1.2))|((adv<0)&(ratios<.8))))))
                versions.append(snapshot());updates.append(dict(step=step+1,train_ids=ids,behavior_version=behavior,learner_version=step,behavior_sha256=weights_hash(versions[behavior]),result_sha256=weights_hash(versions[-1]),uniforms=u.tolist(),behavior_probs=p.tolist(),actions=actions.tolist(),reward=reward.tolist(),behavior_logp=old.tolist(),optimizer_steps=tr,elapsed_s=time.perf_counter()-start));print(seed,lag,step+1,'reward',round(reward.mean(),3),'norm',round(norm,3),flush=True)
            eval_rows=evaluate();row=dict(seed=seed,lag=lag,updates=updates,baseline=stat(baseline),final=stat(eval_rows),eval_rows=eval_rows,final_adapter_sha256=weights_hash(versions[-1]),adapter_parameters=sum(v.size for _,v in initial),initial_adapter_sha256=weights_hash(initial))
            with (out/f'{seed}-lag{lag}.json').open('x') as f:json.dump(row,f,allow_nan=False)
            # Adapters in a user-chosen external directory only; compact JSON evidence goes in repo.
            if args.weights:
                wp=Path(args.weights);wp.mkdir(parents=True,exist_ok=True);target=wp/f'{seed}-lag{lag}.safetensors'
                if target.exists():raise FileExistsError(target)
                mx.save_safetensors(str(target),dict(versions[-1]))
            print('FINAL',seed,lag,row['final'],flush=True);results.append({k:v for k,v in row.items() if k not in ['updates','eval_rows']})
    output=dict(model=MODEL,revision=REV,num_updates=args.updates,baseline=stat(baseline),baseline_rows=baseline,runs=results,label_ids=label_ids,seed_init=2718,base_weights_file_sha256=hashlib.file_digest((path/'model.safetensors').open('rb'),'sha256').hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),device=str(mx.default_device()),python=platform.python_version(),platform=platform.system(),notes='Single GPU; constrained A/B bandit. Per-version lag emulated by explicitly restoring historical weights. No free-form generation or continuous asynchronous rollout with Qwen.')
    (out/'summary.json').write_text(json.dumps(output,indent=2));print('END',flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--output',required=True);p.add_argument('--weights');p.add_argument('--seeds',type=int,nargs='+',default=[7,19,41]);p.add_argument('--lags',type=int,nargs='+',default=[0,2]);p.add_argument('--updates',type=int,default=12);a=p.parse_args()
    if not 1<=a.updates<=12 or any(l<0 for l in a.lags):p.error('updates 1..12 and nonnegative lag required')
    run(a)

if __name__=='__main__':main()
