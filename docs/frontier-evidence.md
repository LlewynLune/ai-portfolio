# 前沿算法机制实验｜五项阅读地图

这些是2017–2023公开经典机制在当代大模型工程中的学习复现，不是2026最新论文榜单，也不是论文大规模性能复现。本页涵盖五个问题主线与独立代码目录；TinyAttention及其LoRA/DPO适配共享小型基座，不能视为彼此独立数据集。仓库现共14项工程实验；本页只描述算法机制子集，模块和基线不重复计数。

|作品|实际深度|核心边界|
|---|---|---|
|TinyAttention|因果多头/层归一/残差/训练、无注意力消融、长度OOD|单微型块查找仍有失败，不是自然语言预训练|
|LoRA-Lab|真实A/B低秩、冻结、rank、全量对照、合并parity、遗忘|小型基座共享，不是大模型/量化微调|
|DPO-Lab|真实DPO损失、reference、beta、SFT、win/top1/KL|规则单token偏好非人类对齐|
|SparseMoE|真实稀疏expert分发、门控梯度、负载辅助、dense对照|非Transformer或分布式MoE|
|SpecDecode|两模型真实训练、greedy块验证、exact path、actualCPU计时|非概率采样算法/商业加速|

## TinyAttention｜从零训练因果注意力

3000 train,500 validation,600 held-out3pair prefixes disjoint;600 authored5pair OOD. Fixed1000 Adam steps and no-attention ablation. Only final query value is supervised, not full language modeling.

[Demo](../projects/tiny-attention/demo.html) · [原理](../projects/tiny-attention/METHOD.md) · [报告](../projects/tiny-attention/artifacts/REPORT.md)

|group|model|trainable_parameters|accuracy|nll|
|---|---|---|---|---|
|validation|causal_attention|10226|0.41400|1.11916|
|validation|no_attention_ablation|10226|0.14800|2.09255|
|heldout3pairs|causal_attention|10226|0.41500|1.11553|
|heldout3pairs|no_attention_ablation|10226|0.14000|2.08841|
|length5pairs_ood|causal_attention|10226|0.20333|2.34030|
|length5pairs_ood|no_attention_ablation|10226|0.12000|2.12432|

原论文：https://arxiv.org/abs/1706.03762

## LoRA-Lab｜参数高效微调与遗忘

Shared pretrained TinyAttention from this portfolio. New rule:answer value+1 mod8.1000train/300validation/500test disjoint within adaptation; original-task retention500; length5 OOD300.450steps each; choose rank1 vs4 by validation accuracy only.

[Demo](../projects/lora-lab/demo.html) · [原理](../projects/lora-lab/METHOD.md) · [报告](../projects/lora-lab/artifacts/REPORT.md)

|group|model|trainable_parameters|accuracy|nll|
|---|---|---|---|---|
|validation_shift1|frozen|0|0.08333|5.46375|
|validation_shift1|lora_r1|178|0.24667|1.99553|
|validation_shift1|lora_r4|712|0.37000|1.60617|
|validation_shift1|full_finetune|10226|0.41000|1.54038|
|test_shift1|frozen|0|0.07000|5.45016|
|test_shift1|lora_r1|178|0.28400|1.89905|
|test_shift1|lora_r4|712|0.43200|1.47049|
|test_shift1|full_finetune|10226|0.44200|1.46826|
|original_task_retention|frozen|0|0.45000|1.10203|
|original_task_retention|lora_r1|178|0.20800|2.28013|
|original_task_retention|lora_r4|712|0.10400|3.01848|
|original_task_retention|full_finetune|10226|0.05000|5.54176|
|length5_shift1_ood|frozen|0|0.09667|3.79224|
|length5_shift1_ood|lora_r1|178|0.21000|2.92671|
|length5_shift1_ood|lora_r4|712|0.18333|2.36634|
|length5_shift1_ood|full_finetune|10226|0.18333|4.04162|

原论文：https://arxiv.org/abs/2106.09685

## DPO-Lab｜偏好、概率排序与模型漂移

Shared pretrained TinyAttention; synthetic1-token preference prefers(value+2)%8 and rejects original value.1000train/300validation/500test disjoint prefixes; head-only400steps. DPO beta0.1/0.5 selected by validation win-.05KL, chosen-onlySFT baseline same head.

[Demo](../projects/dpo-lab/demo.html) · [原理](../projects/dpo-lab/METHOD.md) · [报告](../projects/dpo-lab/artifacts/REPORT.md)

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

原论文：https://arxiv.org/abs/2305.18290

## SparseMoE-Lab｜真实稀疏执行与路由平衡

2400train/500validation/700test authored2D nonlinear regression; skewOOD700 independent seed.4experts width16 top1 vs dense16(active-like) and dense64(total-like).700steps; choose balance0 vs.03 only validation RMSE.

[Demo](../projects/moe-lab/demo.html) · [原理](../projects/moe-lab/METHOD.md) · [报告](../projects/moe-lab/artifacts/REPORT.md)

|group|model|rmse|total_parameters|active_parameter_estimate|max_expert_fraction|routing_entropy|
|---|---|---|---|---|---|---|
|validation|top1_lb0|0.23029|272|77|0.42800|1.21757|
|validation|top1_lb0.03|0.21653|272|77|0.37000|1.32606|
|validation|dense_active16|0.19217|65|65|None|None|
|validation|dense_total64|0.19616|257|257|None|None|
|heldout_uniform|top1_lb0|0.25743|272|77|0.44571|1.21107|
|heldout_uniform|top1_lb0.03|0.25433|272|77|0.34143|1.31576|
|heldout_uniform|dense_active16|0.22029|65|65|None|None|
|heldout_uniform|dense_total64|0.23041|257|257|None|None|
|skew_positive_ood|top1_lb0|0.18409|272|77|0.90571|0.31234|
|skew_positive_ood|top1_lb0.03|0.18790|272|77|0.77857|0.52871|
|skew_positive_ood|dense_active16|0.15484|65|65|None|None|
|skew_positive_ood|dense_total64|0.17141|257|257|None|None|

原论文：https://arxiv.org/abs/2101.03961

## SpecDecode-Lab｜greedy块验证与真实开销

Independent tiny causal next-token models trained on48 synthetic modular-recurrence initial states;8validation/8test states. Target700steps d32, draft250steps d16. Evaluation measures greedy equivalence and actual CPU timing,8outputs after4token prompt,k2/k4,3 paired repeats,warmup; noKV cache.

[Demo](../projects/spec-decode/demo.html) · [原理](../projects/spec-decode/METHOD.md) · [报告](../projects/spec-decode/artifacts/REPORT.md)

|k|repeat|prompts|exact_prompts|baseline_ms|speculative_ms|speed_ratio_baseline_over_spec|target_calls|draft_calls|acceptance_checked|
|---|---|---|---|---|---|---|---|---|---|
|2|0|8|8|21.48512|31.55981|0.68077|33|65|0.65385|
|2|1|8|8|21.23275|31.36544|0.67695|33|65|0.65385|
|2|2|8|8|21.26095|31.28152|0.67966|33|65|0.65385|
|4|0|8|8|21.43287|40.92135|0.52376|30|100|0.69492|
|4|1|8|8|20.97462|40.54971|0.51726|30|100|0.69492|
|4|2|8|8|21.40031|40.94577|0.52265|30|100|0.69492|

原论文：https://arxiv.org/abs/2211.17192

## 不利结果必须留下

- 微型单块attention没有可靠解决完整绑定任务，长度OOD显著差。
- LoRA学新规则同时丢失旧规则，低rank不等于没有遗忘。
- DPO pair win提升不等于chosen top1正确，KL/旧任务冲突需分别看。
- MoE在小型任务上不必超过dense，平衡不等于语义分工或速度。
- 推测解码减少target calls但可能CPU更慢，真实3次计时全保留。

后续本人深度贡献：重跑一项、手算一个forward/梯度、改变明确训练条件并预先冻结验证协议，解释一条失败后才填写“本人实现”。不盲目靠数量代替能力。前沿不是标题，重点是实现和可核验边界。GitHub新版源码与Pages已发布并核验，真实远程LLM未调用。
