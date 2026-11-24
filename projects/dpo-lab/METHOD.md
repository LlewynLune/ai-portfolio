# DPO-Lab｜偏好、概率排序与模型漂移｜方法与可证伪范围

## 目标函数

共享TinyAttention基座，偏好为value+2模8，rejected为原value，是人为规则而非人类反馈。每个response只有1token，序列logprob恰好简化为一个token logprob；这不是完整多token对话对齐。

$\mathcal L=-\log\sigma(\beta[(\log\pi_\theta(y_w|x)-\log\pi_\theta(y_l|x))-(\log\pi_\mathrm{ref}(y_w|x)-\log\pi_\mathrm{ref}(y_l|x))])$。

固定reference在no_grad下计算，不参与优化。只训练policy head，beta0.1/0.5各400steps；SFT_chosen对照同样head和步数。beta仅通过validation(pair_win-.05KL)选，组合系数预设，不查看测试选“最好”。

## 应报告四件不同的事

1. Pair win：chosen概率是否高于rejected，不等于chosen高于全部18候选。
2. Chosen top1：是否真的生成chosen。
3. 原top1保留：旧任务与新偏好冲突，所以下降可能是目标冲突，不是安全性结论。
4. KL到reference：policy||reference，用完整18类概率计算；不是训练目标显式KL惩罚，也不保证固定KL预算。

1000训练、300验证、500测试within-task不相交，保存每项chosen/rejected与概率。DPO排序提升可能伴随严重漂移，而SFT的top1可能更好；全部保留。

## 关键测试

相同policy/reference起点DPO loss应为log2；梯度应提升chosen/rejected相对差；翻转偏好改变梯度方向。权重不训练到reference，测试不能仅看loss下降。

## 不包含

不是PPO、在线RLHF、reward模型训练或真人标注。不代表模型伦理/安全/有用性，不使用敏感对话和个人数据。项目为偏好目标实现与可证伪对照，不是原创对齐算法或论文复现性能。

## 参考

https://arxiv.org/abs/2305.18290

## 运行证据

[全部表](artifacts/REPORT.md)、[JSON](artifacts/results.json)留存分集/预测/损失/环境。模型结果与train.py、frontier_support.py哈希绑定，哈希只检测改动不是第三方真实性签名。修改共享基座后需重训所有依赖，不把旧评测重新打hash作为新实验。
