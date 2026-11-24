# PowerScope｜本次实际运行

Authored synthetic36days at5min; train first20days, validation next6days, test last10days; lag288 requires firstday warmup. One-step forecasts use known-now sensors and noisy planned-next-IT input, never measured future facility power. Fixed cooling-drift10day OOD independent seed.

|group|model|mae|rmse|p95_abs_error|interval90_coverage|flag_tp|flag_fp|flag_fn|
|---|---|---|---|---|---|---|---|---|
|chronological_test|persistence|23.58225|62.62380|41.51952|None|117|102|9|
|chronological_test|seasonal_lag288|262.84820|355.51996|762.11179|None|1|288|125|
|chronological_test|ridge_no_plan|24.55043|61.70302|54.45204|None|116|76|10|
|chronological_test|ridge_full|26.04800|36.06194|65.51139|0.91976|121|65|5|
|cooling_drift_ood|persistence|33.33552|82.40778|185.17849|None|254|200|13|
|cooling_drift_ood|seasonal_lag288|292.40129|382.43315|756.94733|None|65|312|202|
|cooling_drift_ood|ridge_no_plan|96.64242|123.23154|209.29678|None|192|14|75|
|cooling_drift_ood|ridge_full|120.61264|138.52914|246.92509|0.17329|178|0|89|

## 明确局限
- All traces/scheduler forecasts/cooling/loss factors are authored simulation, no real ByteDance or external facility telemetry.
- 5min interval average power; cannot evaluate subsecond electrical transients.
- Toy1200kW threshold not equipment rating, redundancy margin or breaker limit.
- Interval from chronological validation residuals; autocorrelation violates exchangeability, no guaranteed90% coverage.
- Same-window ratio not audited annual PUE; no measured energy saving.
- Forecast only: no control commands, switchgear/cooling setpoints, UPS/protection coordination or safety approvals.
- AI assisted research prototype; offline only and human review required.

[逐样本/逐帧结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)
