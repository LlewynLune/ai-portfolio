# CircuitID gain/offset-aware physical inference｜深化实测

400 fresh32-point simulated step curves, tau0.5–6ms, unit/gain/offset/combined stress. Variable-projection fit estimates gain/offset at each tau; compare frozen Ridge and old unit physics.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|frozen_ridge|combined|100|{"mae": 1.2225463472909532, "rmse": 1.5757995227540893}|
|frozen_ridge|gain_shift|100|{"mae": 0.6026830372015322, "rmse": 0.8279756447864426}|
|frozen_ridge|offset_shift|100|{"mae": 1.2839903351592215, "rmse": 1.5499915643336697}|
|frozen_ridge|unit|100|{"mae": 0.4470883898001617, "rmse": 0.7200005210238976}|
|nuisance_physics|combined|100|{"mae": 0.17513650500806796, "rmse": 0.2609595900667484}|
|nuisance_physics|gain_shift|100|{"mae": 0.17513650500374534, "rmse": 0.26095959005253355}|
|nuisance_physics|offset_shift|100|{"mae": 0.13049571871729276, "rmse": 0.19313205841876321}|
|nuisance_physics|unit|100|{"mae": 0.13049571871727386, "rmse": 0.19313205841895212}|
|unit_physics|combined|100|{"mae": 0.25358340814849983, "rmse": 0.2833287748781389}|
|unit_physics|gain_shift|100|{"mae": 2.820983756109604, "rmse": 2.8538346406353647}|
|unit_physics|offset_shift|100|{"mae": 1.276250708720471, "rmse": 1.407999881227927}|
|unit_physics|unit|100|{"mae": 0.031877899033502424, "rmse": 0.046686482692706616}|

## 发现与失败边界

- Nuisance fitting addresses a missing assumption but can be ill-conditioned at long tau or weak signal.
- Only tau=RC identifiable; fitted gain and offset are numerical nuisance terms, not measured devices.
- No equipment control, hardware validation or electrical tolerance guarantee.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
