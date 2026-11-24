# DPO-Lab｜偏好、概率排序与模型漂移｜模型卡

## 使用边界

仅离线学习与实验复现。

Shared pretrained TinyAttention; synthetic1-token preference prefers(value+2)%8 and rejects original value.1000train/300validation/500test disjoint prefixes; head-only400steps. DPO beta0.1/0.5 selected by validation win-.05KL, chosen-onlySFT baseline same head.

## 限制与风险

- One-token closed-form preferences, not human feedback or natural-language alignment.
- DPO preference ordering can improve while chosen top1 remains bad; both reported.
- Original answer retention intentionally conflicts with preference; drift is not proof of safer behavior.
- No PPO/RLHF online rollout/reward model; PyTorch objective independently implemented.
- Frozen reference must remain unchanged; beta comparisons not matchedKL training budget.
- Shared tiny base disclosed; no foundation-model finetuning or paper-scale claims.

## 输入和人机分工

词表/数值输入需符合Demo声明，超过范围拒绝。输出是模型倾向，不保证语义正确；自定义输入无预设真值。全部张量在静态页面内联，无API/账号/密钥、无数据外发。

## 贡献与证据

AI辅助生成，个人独立贡献待记录；非本人已完成论文/工作或生产成果。原研究版权/引用单列，库许可证独立适用，仓库尚未统一授予开源许可证。
