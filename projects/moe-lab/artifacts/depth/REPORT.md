# SparseMoE capacity, overflow & second-choice routing｜深化实测

Frozen4-expert model; two fresh256-sample batches; capacities0.5/1/1.5 and unlimited; ordered dispatch, drop→zero vs second-ranked fallback. All-item and admitted-only RMSE both recorded.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|drop_capacity0.5|skew|256|{"mae": 0.5597550305166513, "rmse": 0.7304672996535998, "admission_coverage": 0.25}|
|drop_capacity0.5|uniform|256|{"mae": 0.40905000018406074, "rmse": 0.5689051558476036, "admission_coverage": 0.5}|
|drop_capacity1|skew|256|{"mae": 0.3865216823496571, "rmse": 0.5757253069613266, "admission_coverage": 0.5}|
|drop_capacity1|uniform|256|{"mae": 0.21492766387163578, "rmse": 0.3415564692791516, "admission_coverage": 0.83984375}|
|drop_capacity1.5|skew|256|{"mae": 0.30996874036354627, "rmse": 0.4879163028000904, "admission_coverage": 0.63671875}|
|drop_capacity1.5|uniform|256|{"mae": 0.1426954000144488, "rmse": 0.20830544137193488, "admission_coverage": 1.0}|
|drop_capacityNone|skew|256|{"mae": 0.12383669094481789, "rmse": 0.17956285917663262, "admission_coverage": 1.0}|
|drop_capacityNone|uniform|256|{"mae": 0.1426954000144488, "rmse": 0.20830544137193488, "admission_coverage": 1.0}|
|second_capacity0.5|skew|256|{"mae": 0.5493700024192523, "rmse": 0.7260988645416312, "admission_coverage": 0.375}|
|second_capacity0.5|uniform|256|{"mae": 0.4174867217408317, "rmse": 0.5696254498132223, "admission_coverage": 0.5}|
|second_capacity1|skew|256|{"mae": 0.37149471889492136, "rmse": 0.5626134315578777, "admission_coverage": 0.75}|
|second_capacity1|uniform|256|{"mae": 0.1908575746812214, "rmse": 0.28887528501317566, "admission_coverage": 0.90625}|
|second_capacity1.5|skew|256|{"mae": 0.19670031361230772, "rmse": 0.3136028241679256, "admission_coverage": 0.94921875}|
|second_capacity1.5|uniform|256|{"mae": 0.1426954000144488, "rmse": 0.20830544137193488, "admission_coverage": 1.0}|
|second_capacityNone|skew|256|{"mae": 0.12383669094481789, "rmse": 0.17956285917663262, "admission_coverage": 1.0}|
|second_capacityNone|uniform|256|{"mae": 0.1426954000144488, "rmse": 0.20830544137193488, "admission_coverage": 1.0}|

## 发现与失败边界

- Dropped items remain in all-item RMSE; coverage cannot be hidden by reporting admitted-only quality.
- Second-choice routing changes probabilities and expert semantics; not guaranteed improvement.
- Batch-order routing is deterministic but order-sensitive; not distributed AllToAll throughput.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
