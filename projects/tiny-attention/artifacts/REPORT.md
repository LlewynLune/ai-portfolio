# TinyAttention｜冻结运行结果

3000 train,500 validation,600 held-out3pair prefixes disjoint;600 authored5pair OOD. Fixed1000 Adam steps and no-attention ablation. Only final query value is supervised, not full language modeling.

|group|model|trainable_parameters|accuracy|nll|
|---|---|---|---|---|
|validation|causal_attention|10226|0.41400|1.11916|
|validation|no_attention_ablation|10226|0.14800|2.09255|
|heldout3pairs|causal_attention|10226|0.41500|1.11553|
|heldout3pairs|no_attention_ablation|10226|0.14000|2.08841|
|length5pairs_ood|causal_attention|10226|0.20333|2.34030|
|length5pairs_ood|no_attention_ablation|10226|0.12000|2.12432|

## 边界
- One tiny causal block,2heads,d32; no natural-language pretraining or foundation model.
- Synthetic associative lookup; train and test generator shared,5pair length OOD has untrained positional slots.
- Validation reported only; fixed hyperparameters, no test selection.
- No-attention model has fewer active computation paths, not matched-FLOP comparison.
- PyTorch autograd provides differentiation; algorithm implementation AI assisted.
- Attention weights are not a causal explanation or proof of reasoning.

[逐条结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)
