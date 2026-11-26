"""Verify saved adapter payloads by reloading into the pinned base (local GPU only).
Read-only on weights. Checks final prediction parity, not exact gradient replay.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from .llm_policy import REV, LABELS, TEMPERATURE, weights_hash


def main():
    import mlx.core as mx
    from mlx_lm import load
    from mlx_lm.tuner.utils import linear_to_lora_layers
    from mlx.utils import tree_flatten, tree_unflatten
    p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--runs',type=Path,required=True);p.add_argument('--adapters',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.model.name!=REV or a.output.exists():raise ValueError('Require pinned base and a new output path')
    s=json.loads((a.runs/'summary.json').read_text());data=json.loads((a.runs/'dataset.json').read_text())
    with (a.model/'model.safetensors').open('rb') as f:
        assert hashlib.file_digest(f,'sha256').hexdigest()==s['base_weights_file_sha256']
    model,tok=load(str(a.model),tokenizer_config={'trust_remote_code':False,'local_files_only':True});model.freeze();model.eval()
    linear_to_lora_layers(model,2,dict(rank=4,scale=8.,dropout=0.,keys=['self_attn.q_proj','self_attn.v_proj']))
    expected={k:v.shape for k,v in tree_flatten(model.trainable_parameters())};labels=mx.array(s['label_ids']);assert s['label_ids']==[tok.encode(x,add_special_tokens=False)[0] for x in LABELS]
    offset=mx.array(s.get('center_offset',[0.,0.]),dtype=mx.float32);out=[]
    for path in sorted(a.runs.glob('*-lag*.json')):
        run=json.loads(path.read_text());weights=mx.load(str(a.adapters/(path.stem+'.safetensors')));assert {k:v.shape for k,v in weights.items()}==expected
        assert weights_hash(weights.items())==run['final_adapter_sha256'];model.update(tree_unflatten(list(weights.items())))
        errors=[];decisions=0;ties=0
        for split in ['test','ood']:
            for i in range(0,len(data[split]),8):
                seqs=[]
                for r in data[split][i:i+8]:
                    text=f"Column A: {', '.join(map(str,r['a']))}\nColumn B: {', '.join(map(str,r['b']))}\nAdd each column. Which column has the larger sum? Answer only A or B."
                    seqs.append(tok.apply_chat_template([dict(role='user',content=text)],tokenize=True,add_generation_prompt=True))
                n=max(map(len,seqs));x=mx.array([seq+[tok.eos_token_id]*(n-len(seq)) for seq in seqs]);end=mx.array([len(seq)-1 for seq in seqs]);h=model.model(x)[mx.arange(len(seqs)),end]
                z=model.model.embed_tokens.as_linear(h) if model.args.tie_word_embeddings else model.lm_head(h);prob=mx.softmax((z[:,labels].astype(mx.float32)-offset)/TEMPERATURE,axis=-1);mx.eval(prob)
                actual=np.asarray(prob);logged=np.asarray([r['p'] for r in run['eval_rows'][split][i:i+8]]);errors.extend(np.abs(actual-logged).max(axis=1).tolist());decisions+=int((actual.argmax(1)==logged.argmax(1)).sum());ties+=int((actual[:,0]==actual[:,1]).sum())
        record=dict(run=path.stem,adapter_sha256=run['final_adapter_sha256'],probes=len(errors),max_abs_probability_error=max(errors),decisions_matching=decisions,ties=ties)
        assert record['max_abs_probability_error']<1e-5 and decisions==len(errors),record
        out.append(record);print(record,flush=True)
    assert len(out)==6
    with a.output.open('x') as f:json.dump(dict(base_sha256=s['base_weights_file_sha256'],results=out,scope='GPU reloaded final adapter and reevaluated heldout and shifted probes; not gradient replay'),f,indent=2)

if __name__=='__main__':main()
