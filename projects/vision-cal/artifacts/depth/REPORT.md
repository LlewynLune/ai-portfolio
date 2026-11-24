# VisionCal corruption surface & selective risk｜深化实测

Frozen 64→48→10 MLP; same 360 historical held-out IDs, new fixed-seed corruptions, 8 conditions. Temperature frozen on prior validation. Test sweeps descriptive, not safety threshold selection.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|raw|center_occluded|360|{"accuracy": 0.7916666666666666, "nll": 0.7255422121420793}|
|raw|clean|360|{"accuracy": 0.9722222222222222, "nll": 0.11267477398651751}|
|raw|noise_0.05|360|{"accuracy": 0.9666666666666667, "nll": 0.12492755622430633}|
|raw|noise_0.15|360|{"accuracy": 0.9305555555555556, "nll": 0.1973764447766553}|
|raw|noise_0.3|360|{"accuracy": 0.7944444444444444, "nll": 0.6610178936627314}|
|raw|noise_0.5|360|{"accuracy": 0.5333333333333333, "nll": 2.2613031748335697}|
|raw|shift_1|360|{"accuracy": 0.49722222222222223, "nll": 3.04768949819032}|
|raw|shift_2|360|{"accuracy": 0.15, "nll": 9.102010774811795}|
|temperature|center_occluded|360|{"accuracy": 0.7916666666666666, "nll": 0.8929319960279906}|
|temperature|clean|360|{"accuracy": 0.9722222222222222, "nll": 0.1210147879984008}|
|temperature|noise_0.05|360|{"accuracy": 0.9666666666666667, "nll": 0.13188758091392588}|
|temperature|noise_0.15|360|{"accuracy": 0.9305555555555556, "nll": 0.21366102034385284}|
|temperature|noise_0.3|360|{"accuracy": 0.7944444444444444, "nll": 0.791568488641081}|
|temperature|noise_0.5|360|{"accuracy": 0.5333333333333333, "nll": 2.8881429632607842}|
|temperature|shift_1|360|{"accuracy": 0.49722222222222223, "nll": 3.9361314098645357}|
|temperature|shift_2|360|{"accuracy": 0.15, "nll": 11.963259937118142}|

## 发现与失败边界

- Temperature changes probabilities, not argmax accuracy.
- Increasing noise/occlusion/translation tests brittleness without claiming real OCR robustness.
- Coverage/error must be read together; writer isolation remains unavailable.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
