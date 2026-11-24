# LoRA-Lab｜冻结运行结果

Shared pretrained TinyAttention from this portfolio. New rule:answer value+1 mod8.1000train/300validation/500test disjoint within adaptation; original-task retention500; length5 OOD300.450steps each; choose rank1 vs4 by validation accuracy only.

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

## 边界
- Not pretrained large language model; base task and synthetic prefixes shared in family.
- q/v/head adapted; frozen embedding/FFN limits adaptation, results not universal optimal layer recipe.
- Output merged forDemo; adapter tensors retained below; merge reduces extra branches but no GPU latency claim.
- Original-task retention may fall, LoRA does not eliminate forgetting.
- Same optimizer steps not equal FLOPs/memory; parameter count not measured energy saving.
- No real finetuning corpus, human task or original contribution implied.

[逐条结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)
