# FlowBench burst load, duplicate effects & resume｜深化实测

81 actual local async runs:3 fault profiles×3 concurrency levels×3 manifest seeds×3 strategies.16 tasks per run; same fault manifest across policies. SQLite pause/resume/reopen integration separate.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|baseline|ack_loss_c1|48|{"accuracy": 0.4375, "mean_elapsed_ms": 150.2035625}|
|baseline|ack_loss_c4|48|{"accuracy": 0.4375, "mean_elapsed_ms": 40.062374999999996}|
|baseline|ack_loss_c8|48|{"accuracy": 0.4375, "mean_elapsed_ms": 23.49910416666667}|
|baseline|mixed_c1|48|{"accuracy": 0.2916666666666667, "mean_elapsed_ms": 167.66954166666665}|
|baseline|mixed_c4|48|{"accuracy": 0.2916666666666667, "mean_elapsed_ms": 44.316812500000005}|
|baseline|mixed_c8|48|{"accuracy": 0.2916666666666667, "mean_elapsed_ms": 24.430666666666667}|
|baseline|slow_c1|48|{"accuracy": 0.4166666666666667, "mean_elapsed_ms": 276.92270833333333}|
|baseline|slow_c4|48|{"accuracy": 0.4166666666666667, "mean_elapsed_ms": 77.85345833333334}|
|baseline|slow_c8|48|{"accuracy": 0.4166666666666667, "mean_elapsed_ms": 45.352125}|
|resilient|ack_loss_c1|48|{"accuracy": 1.0, "mean_elapsed_ms": 181.64339583333336}|
|resilient|ack_loss_c4|48|{"accuracy": 1.0, "mean_elapsed_ms": 48.436625}|
|resilient|ack_loss_c8|48|{"accuracy": 1.0, "mean_elapsed_ms": 28.309041666666662}|
|resilient|mixed_c1|48|{"accuracy": 0.875, "mean_elapsed_ms": 244.26762499999998}|
|resilient|mixed_c4|48|{"accuracy": 0.875, "mean_elapsed_ms": 64.87495833333334}|
|resilient|mixed_c8|48|{"accuracy": 0.875, "mean_elapsed_ms": 35.662375}|
|resilient|slow_c1|48|{"accuracy": 0.8125, "mean_elapsed_ms": 390.6174583333334}|
|resilient|slow_c4|48|{"accuracy": 1.0, "mean_elapsed_ms": 112.8953125}|
|resilient|slow_c8|48|{"accuracy": 1.0, "mean_elapsed_ms": 64.1605}|
|retry|ack_loss_c1|48|{"accuracy": 1.0, "mean_elapsed_ms": 181.08220833333334}|
|retry|ack_loss_c4|48|{"accuracy": 1.0, "mean_elapsed_ms": 48.19070833333333}|
|retry|ack_loss_c8|48|{"accuracy": 1.0, "mean_elapsed_ms": 28.237958333333335}|
|retry|mixed_c1|48|{"accuracy": 0.875, "mean_elapsed_ms": 244.88910416666667}|
|retry|mixed_c4|48|{"accuracy": 0.875, "mean_elapsed_ms": 65.036}|
|retry|mixed_c8|48|{"accuracy": 0.875, "mean_elapsed_ms": 35.336354166666666}|
|retry|slow_c1|48|{"accuracy": 0.8125, "mean_elapsed_ms": 388.52212499999996}|
|retry|slow_c4|48|{"accuracy": 1.0, "mean_elapsed_ms": 112.74941666666666}|
|retry|slow_c8|48|{"accuracy": 1.0, "mean_elapsed_ms": 63.964625000000005}|

## 发现与失败边界

- Retries can duplicate acknowledgement-lost commit effects; resilient ledger bound is local SQLite only.
- Queue delay and failed tasks are included; do not report only successful latency.
- Seeds are repeated synthetic manifests, not production outage statistics.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
