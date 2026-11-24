# SpecDecode-Lab｜greedy块验证与真实开销｜模型卡

## 使用边界

仅离线学习与实验复现。

Independent tiny causal next-token models trained on48 synthetic modular-recurrence initial states;8validation/8test states. Target700steps d32, draft250steps d16. Evaluation measures greedy equivalence and actual CPU timing,8outputs after4token prompt,k2/k4,3 paired repeats,warmup; noKV cache.

## 限制与风险

- Implements deterministic greedy block verification only, not rejection-sampling distribution preservation.
- Synthetic recurrence state paths overlap later; test is inference-correctness probe, not generalization score.
- NoKV cache/GPU/parallel kernels; Python tiny CPU models can be slower despite fewer target calls.
- Includes draft time and verification time; speed ratio is actual this environment only, not service throughput.
- Target path is reference, not correctness against arithmetic labels.
- No inference service, foundation-model accelerator or original algorithm claims.

## 输入和人机分工

词表/数值输入需符合Demo声明，超过范围拒绝。输出是模型倾向，不保证语义正确；自定义输入无预设真值。全部张量在静态页面内联，无API/账号/密钥、无数据外发。

## 贡献与证据

AI辅助生成，个人独立贡献待记录；非本人已完成论文/工作或生产成果。原研究版权/引用单列，库许可证独立适用，仓库尚未统一授予开源许可证。
