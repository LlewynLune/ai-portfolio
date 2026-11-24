# VisionCal｜小型神经网络校准与鲁棒性｜模型卡

## 模型与预期用途

公开8×8灰度样本 → 固定训练/验证/测试 → 64输入/48 ReLU隐藏/10类别MLP → 验证温度搜索 → 清洁/噪声/平移对照 → 高置信度错误分析 → JSON参数与浏览器推断。

默认导出类型：mlp；输入维数64。仅离线学习、参数推断、复现与失败分析。

## 数据、训练与测试

1797 public 8x8 images; fixed 60/20/20 stratified split. MLP trained only train; temperature minimizes validation NLL only; clean and corrupted test share held-out image IDs.

[实际指标](artifacts/REPORT.md)不是生产指标，也没有第三方审计。训练环境记录在[结果](artifacts/results.json)中，代码和数据/参数哈希不证明专业资质。

## 禁止外推

- Not MNIST, CNN, foundation model or real OCR; small sklearn MLP.
- Digits split has no writer IDs; writer leakage cannot be ruled out.
- Temperature can improve NLL without raising accuracy; ECE bins arbitrary.
- Corruptions are authored tests, not real deployment distribution.
- Confidence0.9 is a fixed demo threshold, not a safety guarantee.
- AI assisted; no prior personal research or production achievement implied.

## 人机分工与退出

页面只显示模型输出和假设；缺失输入/维数错误/非有限数拒绝。修改输入后不再显示预设样本标签作为真值。分布外、无真实标签、数据可用性不足时必须人工调查，不把模型倾向写成事实。

## 贡献与许可

AI辅助学习实现，用户提出范围；本人独立贡献尚待亲自修改与验证，不以此冒充已掌握的研究经历。数据/参考许可分别适用，仓库暂未统一授予开源许可证。
