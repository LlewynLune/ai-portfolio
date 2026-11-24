# LoRA adapter strength & retention frontier｜深化实测

Fixed rank4 q/v/head adapter delta, six strength settings. Same newly authored160 prefixes evaluated under old/new rules separately. Strength sweep not selected on test.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|alpha_0|new_rule|160|{"accuracy": 0.0875, "nll": 5.371912123335271}|
|alpha_0|old_rule|160|{"accuracy": 0.41875, "nll": 1.0007990365110164}|
|alpha_0.25|new_rule|160|{"accuracy": 0.14375, "nll": 3.6531457832547716}|
|alpha_0.25|old_rule|160|{"accuracy": 0.40625, "nll": 1.1871074108534052}|
|alpha_0.5|new_rule|160|{"accuracy": 0.23125, "nll": 2.491382383798127}|
|alpha_0.5|old_rule|160|{"accuracy": 0.29375, "nll": 1.7910240519376905}|
|alpha_0.75|new_rule|160|{"accuracy": 0.36875, "nll": 1.8503535873885197}|
|alpha_0.75|old_rule|160|{"accuracy": 0.1875, "nll": 2.4185367154499247}|
|alpha_1|new_rule|160|{"accuracy": 0.41875, "nll": 1.4943291532020389}|
|alpha_1|old_rule|160|{"accuracy": 0.125, "nll": 2.939493434526439}|
|alpha_1.5|new_rule|160|{"accuracy": 0.16875, "nll": 2.8082941626136266}|
|alpha_1.5|old_rule|160|{"accuracy": 0.0375, "nll": 5.177147150812838}|

## 发现与失败边界

- Adapter strength is a trade-off surface, not a free improvement.
- Reconstructed low-rank delta and merged export agree within float32 export tolerance.
- Original task and new-rule task share prefixes; not independent benchmarks.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
