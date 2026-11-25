# DPO-Lab · 三种子真实偏好优化与SFT对照：结果讨论

sft：三种子平均pair win 88.0%，chosen top1 45.7%，原规则保留 9.4%。

dpo_0.1：三种子平均pair win 15.8%，chosen top1 14.4%，原规则保留 43.6%。

dpo_0.5：三种子平均pair win 36.6%，chosen top1 24.0%，原规则保留 38.9%。

## 仍未完成的下一阶段

下一阶段增加非规则偏好并独立标注；冻结输出头无法代表全模型RLHF。

[原始结果](results.json) · [实验协议与方法](REPORT.md)
