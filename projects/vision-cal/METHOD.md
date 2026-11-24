# VisionCal｜小型神经网络校准与鲁棒性｜原理、对照与失败

## 从算法到实验

输入是64维0–1像素，固定除以16，不估计测试统计量。单隐藏层 MLP 使用 sklearn 实际训练，不把库的反向传播包装成自己编写的框架。线性 Logistic 为同数据分集基线；不同模型超参数预先固定，没有统一超参数竞赛。

神经网络为 $a=\operatorname{ReLU}(xW_1+b_1)$，$z=aW_2+b_2$。温度缩放 $p_k=\exp(z_k/T)/\sum_j\exp(z_j/T)$。正温度不改变argmax，因此准确率不应该被“校准提升”修改；若准确率变化说明实现错误。

### 分集与校准

1797个样本固定stratified60/20/20；仅训练集拟合分类权重，验证集搜索0.5–3的51个温度，最小化NLL。训练停止使用训练损失，没有读取外部测试。参数/训练轮数/loss_curve留在结果；达到max_iter不等于收敛，不能隐瞒优化警告。

### 评测问题

1. 清洁留出：Accuracy、NLL、10-bin ECE。
2. 固定高置信阈值0.9：Coverage与Selective Error分别报告，不能以拒答多来冒充精度高。
3. 与同一批留出ID配对的高斯噪声、右移1像素：标签不变，但分布变化。右移零填充而不是环形移位。
4. 对三个模型raw/temperature/linear全部报告，不删除温度选择失败。

ECE按10个等宽置信区间加权计算，不同分箱可得到不同值。验证最优温度并不保证测试NLL或ECE变好；尤其分布迁移时可能更自信、更错误。项目因此着重“可检验的可信度”，而非只展示干净集高分。

### 贡献边界

Digits不是MNIST，也没有writer分组，随机划分不能证明跨书写者泛化；不是CNN或大型视觉模型。点击编辑像素只是定制输入，没有人工正确标签。概率非安全级判断，不部署到身份识别、支付或关键决策。

## 本批原始证据

1797 public 8x8 images; fixed 60/20/20 stratified split. MLP trained only train; temperature minimizes validation NLL only; clean and corrupted test share held-out image IDs.

[完整表](artifacts/REPORT.md)保留所有组与seed；[JSON](artifacts/results.json)保留逐项预测、样本与运行环境。SHA校验只能发现变更，不是第三方签名。重新修改train.py或共享生成器后必须重跑，不得把旧结果重新打hash当新证据。

来源：https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
