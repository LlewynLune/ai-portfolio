# TinyAttention causal prefix & length stress｜深化实测

Frozen single-block model; 120 newly authored prefixes at each length2–7, plus reorder and unknown-query stress. No test tuning or retraining. Causal prefix logits compared at every token.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|frozen_attention|length_2|120|{"accuracy": 0.3, "nll": 2.146924031893262}|
|frozen_attention|length_3|120|{"accuracy": 0.43333333333333335, "nll": 1.0861110537962726}|
|frozen_attention|length_4|120|{"accuracy": 0.25, "nll": 1.8395839423869276}|
|frozen_attention|length_5|120|{"accuracy": 0.24166666666666667, "nll": 2.147644846737911}|
|frozen_attention|length_6|120|{"accuracy": 0.24166666666666667, "nll": 2.579470014140331}|
|frozen_attention|length_7|120|{"accuracy": 0.24166666666666667, "nll": 2.464503412511156}|
|frozen_attention|pair_reorder|120|{"accuracy": 0.425, "nll": 1.0627585209545596}|
|frozen_attention|query_unknown|120|{"accuracy": 0.43333333333333335, "nll": 1.4134617462887897}|

## 发现与失败边界

- Causal invariance is a correctness property, not proof of key-value task generalization.
- Attention weights can be inspected but are not causal explanations.
- Unknown key stress is deliberately out-of-vocabulary task semantics; reported accuracy is not deployment performance.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
