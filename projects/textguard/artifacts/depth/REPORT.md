# TextGuard lexical stress & abstention｜深化实测

20 authored English probes × 6 transformations; intended labels explicitly authored, not natural-distribution evaluation. Frozen threshold. Historical test risk curve is descriptive, not threshold selection.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|frozen_tfidf|case_punctuation|20|{"accuracy": 1.0, "nll": 0.13059540973250733}|
|frozen_tfidf|clean|20|{"accuracy": 1.0, "nll": 0.13059540973250733}|
|frozen_tfidf|negation|20|{"accuracy": 1.0, "nll": 0.1929891119257278}|
|frozen_tfidf|single_typo|20|{"accuracy": 1.0, "nll": 0.2027440135916442}|
|frozen_tfidf|unknown_prefix|20|{"accuracy": 1.0, "nll": 0.13059540973250733}|
|frozen_tfidf|whitespace|20|{"accuracy": 1.0, "nll": 0.13059540973250733}|

## 发现与失败边界

- Case/punctuation and whitespace must preserve normalized model inference.
- Negation and typos expose lexical limitations; unknown language must route to manual review.
- Abstention curve uses the same historical test, so no post-hoc safety guarantee.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
