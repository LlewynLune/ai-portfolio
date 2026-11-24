# NoveltyLab feature sensitivity & attribution｜深化实测

Frozen centroid/scaler, 131 historical test rows × 13 single-feature shifts × 5 standardized amplitudes. Each shift is authored; correlations and class plausibility are not enforced.

## 方法与结果

|模型|条件|样本|Accuracy / MAE / 其他|
|---|---|---:|---|
|centroid_distance|zshift_0|1703|{"accuracy": 0.9007633587786259}|
|centroid_distance|zshift_0.25|1703|{"accuracy": 0.8990017615971815}|
|centroid_distance|zshift_0.5|1703|{"accuracy": 0.9025249559600704}|
|centroid_distance|zshift_1|1703|{"accuracy": 0.9007633587786259}|
|centroid_distance|zshift_2|1703|{"accuracy": 0.911332941867293}|

## 发现与失败边界

- Corrected attribution uses squared distance to fitted centroid, not distance to origin.
- Repeated feature variants are correlated: intervals do not establish independent sample confidence.
- High detection metrics on Wine classes do not represent industrial anomaly effectiveness.

## 工程与复现

在本项目目录运行 python3 depth.py；新结果只写 artifacts/depth，原模型/报告不覆盖。

[完整新结果](results.json) · [交互分析](../../depth-demo.html) · [代码](../../depth.py)

AI-assisted new local stress experiments; no retraining, external API, private data or production claim
