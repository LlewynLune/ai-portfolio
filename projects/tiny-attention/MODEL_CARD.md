# TinyAttention｜从零训练因果注意力｜模型卡

## 使用边界

仅离线学习与实验复现。

3000 train,500 validation,600 held-out3pair prefixes disjoint;600 authored5pair OOD. Fixed1000 Adam steps and no-attention ablation. Only final query value is supervised, not full language modeling.

## 限制与风险

- One tiny causal block,2heads,d32; no natural-language pretraining or foundation model.
- Synthetic associative lookup; train and test generator shared,5pair length OOD has untrained positional slots.
- Validation reported only; fixed hyperparameters, no test selection.
- No-attention model has fewer active computation paths, not matched-FLOP comparison.
- PyTorch autograd provides differentiation; algorithm implementation AI assisted.
- Attention weights are not a causal explanation or proof of reasoning.

## 输入和人机分工

词表/数值输入需符合Demo声明，超过范围拒绝。输出是模型倾向，不保证语义正确；自定义输入无预设真值。全部张量在静态页面内联，无API/账号/密钥、无数据外发。

## 贡献与证据

AI辅助生成，个人独立贡献待记录；非本人已完成论文/工作或生产成果。原研究版权/引用单列，库许可证独立适用，仓库尚未统一授予开源许可证。
