# ChannelEst missing pilots & abstention｜深化实测

Frozen learned16→64 estimator vs observed-pilot4-tap least-squares;160 fresh channels at20dB and0/1/2/4/6 missing pilots. NMSE per frame; LS refuses fewer than4 measurements.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|observed_pilot_ls|missing_0|160|{"mae": 0.07915216562924143, "rmse": 0.0853720580173133, "mean_nmse": 0.007288388290111509}|
|observed_pilot_ls|missing_1|160|{"mae": 0.08598566377357778, "rmse": 0.09266317865375677, "mean_nmse": 0.008586464678218046}|
|observed_pilot_ls|missing_2|160|{"mae": 0.11543583158942727, "rmse": 0.12702156615201282, "mean_nmse": 0.016134478267710167}|
|observed_pilot_ls|missing_4|160|{"mae": 0.5816928049319782, "rmse": 0.6697859130623003, "mean_nmse": 0.44861316933669926}|
|zero_imputed_frozen|missing_0|160|{"mae": 0.09775507624993146, "rmse": 0.10305703354734426, "mean_nmse": 0.01062075216357844}|
|zero_imputed_frozen|missing_1|160|{"mae": 0.26003640350113955, "rmse": 0.27485581394720016, "mean_nmse": 0.0755457184605779}|
|zero_imputed_frozen|missing_2|160|{"mae": 0.40215402591379695, "rmse": 0.42886167013941795, "mean_nmse": 0.18392233211477094}|
|zero_imputed_frozen|missing_4|160|{"mae": 0.6112248181055182, "rmse": 0.6329877126600167, "mean_nmse": 0.4006734443785599}|
|zero_imputed_frozen|missing_6|160|{"mae": 0.8078595161161161, "rmse": 0.8176208319782191, "mean_nmse": 0.6685038248847552}|

## 发现与失败边界

- Zero-imputing unavailable pilots changes input distribution and may silently corrupt learning.
- Four-tap LS has privileged model-order assumption; not universal best or a5G/6G product.
- Metrics include NMSE; generic error column sqrt(NMSE) is not physical-unit MAE.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
