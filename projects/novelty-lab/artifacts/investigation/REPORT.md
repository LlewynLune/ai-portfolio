# NoveltyLab · 相关特征与收缩协方差

忽略特征相关性的中心距离，和只在正常训练拟合的协方差基线有什么差异？

## 预声明实验协议

{
  "kind": "train_only_shrinkage_mahalanobis_baseline",
  "shrinkage": [
    0.1,
    0.5,
    1.0
  ],
  "threshold": "95th quantile of 12 normal validation rows, descriptive due tiny calibration",
  "data": "same public Wine test IDs; class0 normal, other classes constructed shift",
  "no_test_selection": true
}

## 全部条件结果

|shrinkage|n|condition_number|threshold|normal_false_positive|shift_detection|accuracy|
|---|---|---|---|---|---|---|
|0.1|131|20.581|6.2886|0|0.87395|0.8855|
|0.5|131|4.5005|5.9139|0|0.86555|0.87786|
|1|131|1|6.3071|0|0.89076|0.90076|

## 发现、失败与适用边界

- 协方差只拟合35条正常训练，13维估计不稳定，condition number必须报告。
- 12条正常验证不足以支持高置信误报保证；95%经验分位数非认证。
- Wine类别人为异常定义不能外推工业故障。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project novelty-lab。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
