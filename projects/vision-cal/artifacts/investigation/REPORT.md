# VisionCal · 留出校准的预测集合与失效

不在测试上挑置信门槛，预测集合在干净和迁移图像上还能覆盖真值吗？

## 预声明实验协议

{
  "kind": "validation_split_conformal_prediction_sets",
  "alpha": [
    0.05,
    0.1,
    0.2
  ],
  "score": "1-p_true with finite-sample ceil((n+1)*(1-alpha)) rank",
  "frozen_validation": 359,
  "corruptions": [
    "clean",
    "gaussian_0.2",
    "translation_1"
  ],
  "seed": 190901,
  "labels_not_used_for_test_sets": true
}

## 全部条件结果

|condition|alpha|n|quantile_rank|threshold|coverage|mean_set_size|singleton_rate|empty_rate|
|---|---|---|---|---|---|---|---|---|
|clean|0.05|360|342|0.34003|0.96111|0.97778|0.97778|0.022222|
|gaussian_0.2|0.05|360|342|0.34003|0.875|0.93056|0.93056|0.069444|
|translation_1|0.05|360|342|0.34003|0.46667|0.86944|0.86944|0.13056|
|clean|0.1|360|324|0.076361|0.90833|0.91389|0.91389|0.086111|
|gaussian_0.2|0.1|360|324|0.076361|0.80833|0.82778|0.82778|0.17222|
|translation_1|0.1|360|324|0.076361|0.34444|0.6|0.6|0.4|
|clean|0.2|360|288|0.0054077|0.79167|0.79722|0.79722|0.20278|
|gaussian_0.2|0.2|360|288|0.0054077|0.62778|0.63056|0.63056|0.36944|
|translation_1|0.2|360|288|0.0054077|0.22222|0.34444|0.34444|0.65556|

## 发现、失败与适用边界

- 分位数仅从原验证集冻结，测试不选alpha或温度。
- 交换性是覆盖理论条件；噪声/平移迁移破坏它，不能用名义水平保证OOD。
- 集合大小、空集与单例一起报告，不用扩大集合隐藏低效。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project vision-cal。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
