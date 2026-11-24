# DPO-Lab｜冻结运行结果

Shared pretrained TinyAttention; synthetic1-token preference prefers(value+2)%8 and rejects original value.1000train/300validation/500test disjoint prefixes; head-only400steps. DPO beta0.1/0.5 selected by validation win-.05KL, chosen-onlySFT baseline same head.

|group|model|pair_win_rate|chosen_top1_accuracy|original_top1_retention|kl_to_reference|
|---|---|---|---|---|---|
|validation|reference|0.15000|0.09000|0.44000|0.00000|
|validation|dpo_beta0.1|0.97667|0.37000|0.01333|6.15872|
|validation|dpo_beta0.5|0.93333|0.39333|0.05667|4.75908|
|validation|sft_chosen|0.89667|0.44000|0.07667|3.95724|
|heldout_pairs|reference|0.09200|0.04600|0.47200|0.00000|
|heldout_pairs|dpo_beta0.1|0.99000|0.42200|0.00800|6.23081|
|heldout_pairs|dpo_beta0.5|0.95600|0.43000|0.04200|4.91226|
|heldout_pairs|sft_chosen|0.87800|0.44200|0.08400|4.10003|

## 边界
- One-token closed-form preferences, not human feedback or natural-language alignment.
- DPO preference ordering can improve while chosen top1 remains bad; both reported.
- Original answer retention intentionally conflicts with preference; drift is not proof of safer behavior.
- No PPO/RLHF online rollout/reward model; PyTorch objective independently implemented.
- Frozen reference must remain unchanged; beta comparisons not matchedKL training budget.
- Shared tiny base disclosed; no foundation-model finetuning or paper-scale claims.

[逐条结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)
