# CiteRAG deduplication & evidence stress｜深化实测

25 authored queries × clean/duplicate/irrelevant corpora × raw/dedup RRF. Explicit supported/abstained state and content hashes. Correctness is top3 retrieval or refusal, not answer semantics.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|dedup_rrf|clean|25|{"accuracy": 0.96}|
|dedup_rrf|duplicate_flood|25|{"accuracy": 0.96}|
|dedup_rrf|irrelevant_flood|25|{"accuracy": 0.96}|
|raw_rrf|clean|25|{"accuracy": 0.96}|
|raw_rrf|duplicate_flood|25|{"accuracy": 0.96}|
|raw_rrf|irrelevant_flood|25|{"accuracy": 0.96}|

## 发现与失败边界

- Content fingerprint deduplication prevents exact duplicate results occupying all top-k slots.
- RRF scores are not calibrated confidence; metric combines retrieval/refusal and is explicitly defined.
- Distractors alter BM25 IDF; evidence IDs and hashes help auditing, not truth verification.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
