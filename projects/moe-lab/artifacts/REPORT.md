# SparseMoE-Lab｜冻结运行结果

2400train/500validation/700test authored2D nonlinear regression; skewOOD700 independent seed.4experts width16 top1 vs dense16(active-like) and dense64(total-like).700steps; choose balance0 vs.03 only validation RMSE.

|group|model|rmse|total_parameters|active_parameter_estimate|max_expert_fraction|routing_entropy|
|---|---|---|---|---|---|---|
|validation|top1_lb0|0.23029|272|77|0.42800|1.21757|
|validation|top1_lb0.03|0.21653|272|77|0.37000|1.32606|
|validation|dense_active16|0.19217|65|65|None|None|
|validation|dense_total64|0.19616|257|257|None|None|
|heldout_uniform|top1_lb0|0.25743|272|77|0.44571|1.21107|
|heldout_uniform|top1_lb0.03|0.25433|272|77|0.34143|1.31576|
|heldout_uniform|dense_active16|0.22029|65|65|None|None|
|heldout_uniform|dense_total64|0.23041|257|257|None|None|
|skew_positive_ood|top1_lb0|0.18409|272|77|0.90571|0.31234|
|skew_positive_ood|top1_lb0.03|0.18790|272|77|0.77857|0.52871|
|skew_positive_ood|dense_active16|0.15484|65|65|None|None|
|skew_positive_ood|dense_total64|0.17141|257|257|None|None|

## 边界
- Not a Transformer MoE, distributed experts, AllToAll or trillion-parameter training.
- Top1 gating multiplies expert output by selected probability for router gradients.
- Routing load balancing loss from minibatch proportions; selection nondifferentiable, could collapse.
- Each expert actually processes only selected examples, but Python CPU dispatch may be slower; parameter estimate not latency benchmark.
- No capacity dropping; dataset skew can alter load and hurt coverage.
- Dense comparisons active-like and total-like are not exact compute matches; noSOTA.

[逐条结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)
