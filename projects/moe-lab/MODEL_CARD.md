# SparseMoE-Lab｜真实稀疏执行与路由平衡｜模型卡

## 使用边界

仅离线学习与实验复现。

2400train/500validation/700test authored2D nonlinear regression; skewOOD700 independent seed.4experts width16 top1 vs dense16(active-like) and dense64(total-like).700steps; choose balance0 vs.03 only validation RMSE.

## 限制与风险

- Not a Transformer MoE, distributed experts, AllToAll or trillion-parameter training.
- Top1 gating multiplies expert output by selected probability for router gradients.
- Routing load balancing loss from minibatch proportions; selection nondifferentiable, could collapse.
- Each expert actually processes only selected examples, but Python CPU dispatch may be slower; parameter estimate not latency benchmark.
- No capacity dropping; dataset skew can alter load and hurt coverage.
- Dense comparisons active-like and total-like are not exact compute matches; noSOTA.

## 输入和人机分工

词表/数值输入需符合Demo声明，超过范围拒绝。输出是模型倾向，不保证语义正确；自定义输入无预设真值。全部张量在静态页面内联，无API/账号/密钥、无数据外发。

## 贡献与证据

AI辅助生成，个人独立贡献待记录；非本人已完成论文/工作或生产成果。原研究版权/引用单列，库许可证独立适用，仓库尚未统一授予开源许可证。
