# PowerScope rolling error & interval failure｜深化实测

Read-only reanalysis of frozen chronological and drift forecasts; daily288-point blocks, residual coverage vs width; no recalibration on test or model retraining. Counterfactual contributions from frozen linear weights.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|frozen_ridge|chronological_test|2879|{"mae": 26.048001551177475, "rmse": 36.06193615412892}|
|frozen_ridge|cooling_drift_ood|2591|{"mae": 120.6126378122865, "rmse": 138.52913874651978}|

## 发现与失败边界

- Interval width / coverage trade-off is descriptive and not a certified protection margin.
- Chronological residual dependence prevents independent-example binomial guarantees.
- Drift cannot be fixed by silently widening an interval; bias, MAE and tail error stay visible.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
