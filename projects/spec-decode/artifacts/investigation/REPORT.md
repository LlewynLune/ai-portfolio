# SpecDecode · 分布正确的拒绝采样与修正

greedy一致性之外，随机草稿接受/修正能否保持目标token分布？

## 预声明实验协议

{
  "kind": "distribution_correct_single_proposal_sampling",
  "contexts": 16,
  "empirical_samples_per_context": 1000,
  "seed": 195001,
  "temperature": 1,
  "multi_token_block": false,
  "analytical_identity": true
}

## 全部条件结果

|context|n|analytic_max_error|theoretical_acceptance|observed_acceptance|total_variation|
|---|---|---|---|---|---|
|0|1000|1.3553e-20|0.43622|0.439|0.0008972|
|1|1000|2.7756e-17|0.79154|0.78|0.0029995|
|2|1000|1.1102e-16|0.27473|0.285|0.0047321|
|3|1000|0|0.52852|0.529|0.00048615|
|4|1000|0|0.028665|0.025|0.01479|
|5|1000|0|0.22342|0.207|0.00097923|
|6|1000|0|0.95432|0.957|0.0016436|
|7|1000|3.3881e-21|0.40774|0.444|0.027402|
|8|1000|0|0.90496|0.913|0.00015918|
|9|1000|0|0.036954|0.041|0.0047425|
|10|1000|0|0.075089|0.085|0.012416|
|11|1000|0|0.0085892|0.01|0.0012584|
|12|1000|0|0.0080298|0.011|0.0033808|
|13|1000|8.6736e-19|0.99337|0.993|0.0017898|
|14|1000|0|0.64184|0.619|0.00013297|
|15|1000|0|0.94823|0.954|0.0012166|

## 发现、失败与适用边界

- 公式min(p,q)+正残差逐token精确恢复p，分析误差与经验总变差分别报告。
- 单草稿token机制，不是多token并行验证，不宣称加速。
- 1000抽样只检验有限上下文，经验偏差来自采样；64四token轨迹不证明全语言分布。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project spec-decode。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
