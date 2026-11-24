# VideoGuard latency-bounded drift events｜深化实测

Frozen160-frame trajectories,5 challenging groups×120 clips; fixed validated detector configs. Require both800ms boundary tolerance and500/1000/1500/2000ms emitted-alarm delay. One-to-one chronological DP matching.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|mlp|exposure_budget1000ms|120|{"accuracy": 0.11666666666666667}|
|mlp|exposure_budget1500ms|120|{"accuracy": 0.6166666666666667}|
|mlp|exposure_budget2000ms|120|{"accuracy": 0.9416666666666667}|
|mlp|exposure_budget500ms|120|{"accuracy": 0.0}|
|mlp|multiple_budget1000ms|120|{"accuracy": 0.0}|
|mlp|multiple_budget1500ms|120|{"accuracy": 0.6166666666666667}|
|mlp|multiple_budget2000ms|120|{"accuracy": 0.95}|
|mlp|multiple_budget500ms|120|{"accuracy": 0.0}|
|mlp|quiet_gap_budget1000ms|120|{"accuracy": 0.0}|
|mlp|quiet_gap_budget1500ms|120|{"accuracy": 0.0}|
|mlp|quiet_gap_budget2000ms|120|{"accuracy": 0.35}|
|mlp|quiet_gap_budget500ms|120|{"accuracy": 0.0}|
|mlp|ramp_budget1000ms|120|{"accuracy": 0.0}|
|mlp|ramp_budget1500ms|120|{"accuracy": 0.08333333333333333}|
|mlp|ramp_budget2000ms|120|{"accuracy": 0.11666666666666667}|
|mlp|ramp_budget500ms|120|{"accuracy": 0.0}|
|mlp|step_budget1000ms|120|{"accuracy": 0.125}|
|mlp|step_budget1500ms|120|{"accuracy": 0.7916666666666666}|
|mlp|step_budget2000ms|120|{"accuracy": 0.9833333333333333}|
|mlp|step_budget500ms|120|{"accuracy": 0.0}|
|onset|exposure_budget1000ms|120|{"accuracy": 0.041666666666666664}|
|onset|exposure_budget1500ms|120|{"accuracy": 0.31666666666666665}|
|onset|exposure_budget2000ms|120|{"accuracy": 0.95}|
|onset|exposure_budget500ms|120|{"accuracy": 0.0}|
|onset|multiple_budget1000ms|120|{"accuracy": 0.0}|
|onset|multiple_budget1500ms|120|{"accuracy": 0.075}|
|onset|multiple_budget2000ms|120|{"accuracy": 0.9666666666666667}|
|onset|multiple_budget500ms|120|{"accuracy": 0.0}|
|onset|quiet_gap_budget1000ms|120|{"accuracy": 0.0}|
|onset|quiet_gap_budget1500ms|120|{"accuracy": 0.0}|
|onset|quiet_gap_budget2000ms|120|{"accuracy": 0.39166666666666666}|
|onset|quiet_gap_budget500ms|120|{"accuracy": 0.0}|
|onset|ramp_budget1000ms|120|{"accuracy": 0.0}|
|onset|ramp_budget1500ms|120|{"accuracy": 0.0}|
|onset|ramp_budget2000ms|120|{"accuracy": 0.008333333333333333}|
|onset|ramp_budget500ms|120|{"accuracy": 0.0}|
|onset|step_budget1000ms|120|{"accuracy": 0.025}|
|onset|step_budget1500ms|120|{"accuracy": 0.4166666666666667}|
|onset|step_budget2000ms|120|{"accuracy": 0.95}|
|onset|step_budget500ms|120|{"accuracy": 0.0}|
|raw|exposure_budget1000ms|120|{"accuracy": 0.06666666666666667}|
|raw|exposure_budget1500ms|120|{"accuracy": 0.2833333333333333}|
|raw|exposure_budget2000ms|120|{"accuracy": 0.6416666666666667}|
|raw|exposure_budget500ms|120|{"accuracy": 0.008333333333333333}|
|raw|multiple_budget1000ms|120|{"accuracy": 0.0}|
|raw|multiple_budget1500ms|120|{"accuracy": 0.36666666666666664}|
|raw|multiple_budget2000ms|120|{"accuracy": 0.9416666666666667}|
|raw|multiple_budget500ms|120|{"accuracy": 0.0}|
|raw|quiet_gap_budget1000ms|120|{"accuracy": 0.0}|
|raw|quiet_gap_budget1500ms|120|{"accuracy": 0.0}|
|raw|quiet_gap_budget2000ms|120|{"accuracy": 0.39166666666666666}|
|raw|quiet_gap_budget500ms|120|{"accuracy": 0.0}|
|raw|ramp_budget1000ms|120|{"accuracy": 0.025}|
|raw|ramp_budget1500ms|120|{"accuracy": 0.11666666666666667}|
|raw|ramp_budget2000ms|120|{"accuracy": 0.14166666666666666}|
|raw|ramp_budget500ms|120|{"accuracy": 0.0}|
|raw|step_budget1000ms|120|{"accuracy": 0.10833333333333334}|
|raw|step_budget1500ms|120|{"accuracy": 0.7333333333333333}|
|raw|step_budget2000ms|120|{"accuracy": 0.9833333333333333}|
|raw|step_budget500ms|120|{"accuracy": 0.0}|

## 发现与失败边界

- A good retrospective boundary can still miss a real-time deadline; explicit late alarms lose credit.
- No future-window lookahead or new thresholds tuned on test.
- Reanalysis of existing clips, not independent new media or real-video evidence.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
