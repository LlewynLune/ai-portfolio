# LoRA-Lab｜参数高效微调与遗忘｜模型卡

## 使用边界

仅离线学习与实验复现。

Shared pretrained TinyAttention from this portfolio. New rule:answer value+1 mod8.1000train/300validation/500test disjoint within adaptation; original-task retention500; length5 OOD300.450steps each; choose rank1 vs4 by validation accuracy only.

## 限制与风险

- Not pretrained large language model; base task and synthetic prefixes shared in family.
- q/v/head adapted; frozen embedding/FFN limits adaptation, results not universal optimal layer recipe.
- Output merged forDemo; adapter tensors retained below; merge reduces extra branches but no GPU latency claim.
- Original-task retention may fall, LoRA does not eliminate forgetting.
- Same optimizer steps not equal FLOPs/memory; parameter count not measured energy saving.
- No real finetuning corpus, human task or original contribution implied.

## 输入和人机分工

词表/数值输入需符合Demo声明，超过范围拒绝。输出是模型倾向，不保证语义正确；自定义输入无预设真值。全部张量在静态页面内联，无API/账号/密钥、无数据外发。

## 贡献与证据

AI辅助生成，个人独立贡献待记录；非本人已完成论文/工作或生产成果。原研究版权/引用单列，库许可证独立适用，仓库尚未统一授予开源许可证。
