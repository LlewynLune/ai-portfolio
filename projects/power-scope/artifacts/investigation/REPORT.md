# PowerScope · 严格先预测后更新的区间运营

只用过去误差在线更新区间，冷却漂移下能否恢复覆盖，而代价多大？

## 预声明实验协议

{
  "kind": "prequential_residual_recalibration",
  "history": 288,
  "alpha": 0.1,
  "evaluation": "old chronological/cooling OOD forecasts",
  "update_order": "predict interval using past residuals, then observe current residual",
  "no_retraining": true
}

## 全部条件结果

|condition|method|n|coverage|mean_width_kw|mae_kw|p95_absolute_error_kw|
|---|---|---|---|---|---|---|
|chronological_test|fixed|2879|0.91976|113.74|26.048|65.511|
|chronological_test|past_residual_quantile|2879|0.89684|104.06|26.048|65.511|
|cooling_drift_ood|fixed|2591|0.17329|113.74|120.61|246.93|
|cooling_drift_ood|past_residual_quantile|2591|0.87688|415.39|120.61|246.93|

## 发现、失败与适用边界

- 每个时点区间先由过去残差确定，当前真值仅在预测后更新。
- 更新仅区间宽度，预测点及MAE不变；不能当作解决了负荷漂移。
- 时序依赖/非平稳下无IID conformal覆盖保证，warm-start样本数公开。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project power-scope。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
