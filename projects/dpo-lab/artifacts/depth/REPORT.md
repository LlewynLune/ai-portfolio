# DPO preference / accuracy / KL frontier｜深化实测

Frozen head-only DPO policy and reference; interpolate output head over six strengths, fresh180 synthetic prefixes; chosen rule +2 and rejected original. No new optimizer training or test selection.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|alpha_0|chosen_top1|180|{"accuracy": 0.044444444444444446, "nll": 5.314764661962997}|
|alpha_0.25|chosen_top1|180|{"accuracy": 0.12222222222222222, "nll": 3.0925430579376245}|
|alpha_0.5|chosen_top1|180|{"accuracy": 0.3, "nll": 1.7519121245074125}|
|alpha_0.75|chosen_top1|180|{"accuracy": 0.4166666666666667, "nll": 1.3812044949603985}|
|alpha_1|chosen_top1|180|{"accuracy": 0.46111111111111114, "nll": 1.5109615214025165}|
|alpha_1.25|chosen_top1|180|{"accuracy": 0.4444444444444444, "nll": 1.8298279898514465}|

## 发现与失败边界

- Pair wins and chosen top1 can move differently; both are explicitly computed.
- Parameter interpolation is an inference diagnostic, not equivalent to retraining with a different beta.
- KL and original-task loss remain visible; no human-alignment claim.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
