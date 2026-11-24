# 跨学科实验｜阅读与复核指南

本批四项目加已有四项，共八个独立研究作品；基线、模块和Demo不重复计数。AI辅助实现，个人独立研究/硬件/生产履历未被验证。不是“满分”或招聘官方标准。

## 四条主线

|方向|作品|要验证的问题|数据边界|
|---|---|---|---|
|AI算法|VisionCal|校准是否能提高可信度，扰动时是否高置信出错|公开8×8图像；真实小MLP训练|
|电子科学与技术|CircuitID|学习辨识何时胜出，何时物理拟合更稳|理想RC数学仿真；无硬件|
|信息与通信工程|ChannelEst|导频到信道的学习映射能否改善NMSE/BER|理想频域QPSK，多径AWGN；无无线设备|
|AI数据中心/电气工程|PowerScope|计划信息、时间因果与冷却漂移如何影响负荷预测|透明合成时序；仅只读，无设备控制|

## 本批冻结结果：不利情况一并看

### VisionCal

1797 public 8x8 images; fixed 60/20/20 stratified split. MLP trained only train; temperature minimizes validation NLL only; clean and corrupted test share held-out image IDs.

表中多seed组对三个seed均值；原始报告逐seed保留，无统计显著性断言。VisionCal只有一个训练seed；PowerScope时间相关且只有一个主轨迹。

|group|model|accuracy|nll|ece10|coverage90|selective_error90|
|---|---|---:|---:|---:|---:|---:|
|clean|logistic|0.95556|0.19277|0.07449|0.64444|0.00000|
|clean|mlp_raw|0.97222|0.11267|0.01236|0.89167|0.00623|
|clean|mlp_temperature|0.97222|0.12101|0.01658|0.92778|0.00898|
|noise_sigma0.25|logistic|0.87500|0.41101|0.08690|0.42222|0.00658|
|noise_sigma0.25|mlp_raw|0.83611|0.48207|0.06421|0.72222|0.07308|
|noise_sigma0.25|mlp_temperature|0.83611|0.56556|0.09170|0.78889|0.07746|
|shift_right1px|logistic|0.39444|2.22489|0.28029|0.18611|0.44776|
|shift_right1px|mlp_raw|0.49722|3.04769|0.33904|0.51944|0.40107|
|shift_right1px|mlp_temperature|0.49722|3.93613|0.38164|0.62500|0.44000|

[可操作页面](../projects/vision-cal/demo.html) · [逐项实测](../projects/vision-cal/artifacts/REPORT.md) · [原理与协议](../projects/vision-cal/METHOD.md) · [模型卡](../projects/vision-cal/MODEL_CARD.md)

### CircuitID

Independent synthetic RC step waveforms: train1800, validation400, 4 test groups x3 seeds x160. Tau0.5–3ms train; slow OOD4–6ms. Ridge alpha and default model chosen only validation; physical solver does not train.

表中多seed组对三个seed均值；原始报告逐seed保留，无统计显著性断言。VisionCal只有一个训练seed；PowerScope时间相关且只有一个主轨迹。

|group|model|mae|rmse|p95_abs_error|
|---|---|---:|---:|---:|
|id|crossing63|0.16944|0.20401|0.36577|
|id|mlp|0.11322|0.15818|0.34365|
|id|physical_curve_fit|0.04989|0.06324|0.12611|
|id|ridge|0.03472|0.04677|0.09600|
|noisy_ood|crossing63|0.27426|0.34177|0.65148|
|noisy_ood|mlp|0.58982|0.76891|1.50261|
|noisy_ood|physical_curve_fit|0.10300|0.13449|0.27756|
|noisy_ood|ridge|0.14921|0.20323|0.41940|
|offset_ood|crossing63|0.27237|0.33113|0.60591|
|offset_ood|mlp|0.59033|0.66845|1.07212|
|offset_ood|physical_curve_fit|0.53057|0.57493|0.88028|
|offset_ood|ridge|0.38281|0.41835|0.66940|
|slow_ood|crossing63|0.21750|0.26955|0.52811|
|slow_ood|mlp|2.55164|2.65589|3.66197|
|slow_ood|physical_curve_fit|0.10095|0.12140|0.22207|
|slow_ood|ridge|1.10199|1.17787|1.76890|

[可操作页面](../projects/circuit-id/demo.html) · [逐项实测](../projects/circuit-id/artifacts/REPORT.md) · [原理与协议](../projects/circuit-id/METHOD.md) · [模型卡](../projects/circuit-id/MODEL_CARD.md)

### ChannelEst

Ideal frequency-domain OFDM-equivalent:32 subcarriers,8 unit pilots,24 QPSK data tones; AWGN complex variance=10^(-SNR/10), block-static channel. Train3600 frames at5/15/25dB, validation600 at15dB. Test4groups x3seeds x220 paired frames.

表中多seed组对三个seed均值；原始报告逐seed保留，无统计显著性断言。VisionCal只有一个训练seed；PowerScope时间相关且只有一个主轨迹。

|group|model|nmse|ber|
|---|---|---:|---:|
|long_delay_ood|known_prior_lmmse4|0.19792|0.09359|
|long_delay_ood|learned_ridge|0.19911|0.09400|
|long_delay_ood|linear_interpolation|0.23002|0.11787|
|long_delay_ood|perfect_CSI_oracle|0.00000|0.01679|
|snr15|known_prior_lmmse4|0.02122|0.02244|
|snr15|learned_ridge|0.02305|0.02285|
|snr15|linear_interpolation|0.06358|0.03908|
|snr15|perfect_CSI_oracle|0.00000|0.01540|
|snr25|known_prior_lmmse4|0.00218|0.00230|
|snr25|learned_ridge|0.00616|0.00278|
|snr25|linear_interpolation|0.03727|0.01783|
|snr25|perfect_CSI_oracle|0.00000|0.00133|
|snr5|known_prior_lmmse4|0.17383|0.14454|
|snr5|learned_ridge|0.19320|0.14514|
|snr5|linear_interpolation|0.32847|0.16875|
|snr5|perfect_CSI_oracle|0.00000|0.10777|

[可操作页面](../projects/channel-est/demo.html) · [逐项实测](../projects/channel-est/artifacts/REPORT.md) · [原理与协议](../projects/channel-est/METHOD.md) · [模型卡](../projects/channel-est/MODEL_CARD.md)

### PowerScope

Authored synthetic36days at5min; train first20days, validation next6days, test last10days; lag288 requires firstday warmup. One-step forecasts use known-now sensors and noisy planned-next-IT input, never measured future facility power. Fixed cooling-drift10day OOD independent seed.

表中多seed组对三个seed均值；原始报告逐seed保留，无统计显著性断言。VisionCal只有一个训练seed；PowerScope时间相关且只有一个主轨迹。

|group|model|mae|rmse|p95_abs_error|
|---|---|---:|---:|---:|
|chronological_test|persistence|23.58225|62.62380|41.51952|
|chronological_test|ridge_full|26.04800|36.06194|65.51139|
|chronological_test|ridge_no_plan|24.55043|61.70302|54.45204|
|chronological_test|seasonal_lag288|262.84820|355.51996|762.11179|
|cooling_drift_ood|persistence|33.33552|82.40778|185.17849|
|cooling_drift_ood|ridge_full|120.61264|138.52914|246.92509|
|cooling_drift_ood|ridge_no_plan|96.64242|123.23154|209.29678|
|cooling_drift_ood|seasonal_lag288|292.40129|382.43315|756.94733|

[可操作页面](../projects/power-scope/demo.html) · [逐项实测](../projects/power-scope/artifacts/REPORT.md) · [原理与协议](../projects/power-scope/METHOD.md) · [模型卡](../projects/power-scope/MODEL_CARD.md)

## 必须保留的发现

- VisionCal：验证温度选择并未使测试NLL更好；平移时置信仍高。达到训练迭代上限的优化警告不能解释成收敛证明。
- CircuitID：同分布学习Ridge有用，偏置/慢tau外推显著失败；强噪声或范围外物理拟合更稳。MLP复杂不等于胜出。
- ChannelEst：学习映射比简单插值好，但不等于超过获得真实噪声与先验的LMMSE；长delay OOD仍明显退化。
- PowerScope：计划输入减少大突变RMSE，却可能提高MAE；冷却漂移使经验区间覆盖率与峰值漏报恶化。

## 复现与证据

训练用 requirements-ml.txt，原始结果记录Python/numpy/sklearn环境。train.py和共享数值函数均有哈希；模型和结果有校验，哈希只发现改动不是第三方签名。所有逐点/帧预测可重算，导出参数在JavaScript与Python之间逐例核验。

模型参数推断Demo与训练仿真不是同一件事：浏览器只运行冻结模型，不重新训练，也不访问真实电路/无线/机房。修改输入后来源标签不继续冒充真值。

来源：VisionCal公开数据 https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html；RC公式 https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits；通信概念 https://wirelesspi.com/channel-estimation-in-ofdm-systems/；数据中心能效概念 https://www.energy.gov/cmei/femp/energy-efficiency-data-centers。项目数值不来自这些资料，全部由本项目代码产生。

## 后续深度不是盲目堆项目

各README已有本人能执行的独立修改问题。先重跑、讲清一个失败、做一处有证据的修改再填写个人贡献；不把本批AI辅助代码包装成过去论文/实习/工作成果。真实LLM仍未调用，未授权外发内部数据。GitHub新版源码与Pages已发布并核验。
