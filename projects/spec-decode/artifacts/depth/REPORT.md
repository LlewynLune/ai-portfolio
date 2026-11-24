# SpecDecode incremental KV cache & exact paths｜深化实测

Two frozen tiny models,24 fresh4-token prefixes;8 greedy outputs;three repeats; full recompute vs real single-layer cached K/V. k1/2/4 speculative target-path verification retained.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|full_recompute|decode8|72|{"accuracy": 1.0, "mean_elapsed_ms": 0.4129965349824892}|
|kv_cached|decode8|72|{"accuracy": 1.0, "mean_elapsed_ms": 0.41197339952405954}|

## 发现与失败边界

- K/V cache is exact per-layer inference, not caching final answers.
- CPU timing only this environment; repeated timings are correlated and tiny models are overhead-sensitive.
- Speculation remains deterministic greedy, not distribution-preserving random sampling.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
