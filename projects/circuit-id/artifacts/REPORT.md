# CircuitID｜本次实际运行

Independent synthetic RC step waveforms: train1800, validation400, 4 test groups x3 seeds x160. Tau0.5–3ms train; slow OOD4–6ms. Ridge alpha and default model chosen only validation; physical solver does not train.

|group|seed|model|mae|rmse|p95_abs_error|coverage90|
|---|---|---|---|---|---|---|
|id|31|crossing63|0.17830|0.21228|0.37555|None|
|id|31|physical_curve_fit|0.05126|0.06429|0.12703|None|
|id|31|ridge|0.04109|0.05871|0.12105|0.89375|
|id|31|mlp|0.12869|0.17831|0.38362|None|
|id|32|crossing63|0.16049|0.19617|0.35814|None|
|id|32|physical_curve_fit|0.04885|0.06137|0.12116|None|
|id|32|ridge|0.03281|0.04072|0.08036|0.95000|
|id|32|mlp|0.10103|0.14242|0.32258|None|
|id|33|crossing63|0.16953|0.20357|0.36361|None|
|id|33|physical_curve_fit|0.04956|0.06408|0.13015|None|
|id|33|ridge|0.03025|0.04088|0.08659|0.94375|
|id|33|mlp|0.10994|0.15382|0.32476|None|
|noisy_ood|31|crossing63|0.29172|0.36293|0.69155|None|
|noisy_ood|31|physical_curve_fit|0.10824|0.14095|0.29699|None|
|noisy_ood|31|ridge|0.16413|0.22614|0.47168|0.36250|
|noisy_ood|31|mlp|0.66558|0.86131|1.75364|None|
|noisy_ood|32|crossing63|0.28683|0.35097|0.68552|None|
|noisy_ood|32|physical_curve_fit|0.10532|0.13504|0.26406|None|
|noisy_ood|32|ridge|0.15225|0.20842|0.45911|0.36875|
|noisy_ood|32|mlp|0.53827|0.68790|1.37517|None|
|noisy_ood|33|crossing63|0.24422|0.31141|0.57739|None|
|noisy_ood|33|physical_curve_fit|0.09544|0.12748|0.27163|None|
|noisy_ood|33|ridge|0.13126|0.17513|0.32741|0.41250|
|noisy_ood|33|mlp|0.56561|0.75752|1.37902|None|
|offset_ood|31|crossing63|0.29432|0.34932|0.64182|None|
|offset_ood|31|physical_curve_fit|0.54093|0.58401|0.86629|None|
|offset_ood|31|ridge|0.39317|0.43118|0.68914|0.00625|
|offset_ood|31|mlp|0.61129|0.69102|1.09566|None|
|offset_ood|32|crossing63|0.25822|0.32259|0.60335|None|
|offset_ood|32|physical_curve_fit|0.52853|0.57528|0.88015|None|
|offset_ood|32|ridge|0.37931|0.41492|0.66986|0.00625|
|offset_ood|32|mlp|0.58536|0.67097|1.13380|None|
|offset_ood|33|crossing63|0.26458|0.32146|0.57257|None|
|offset_ood|33|physical_curve_fit|0.52225|0.56549|0.89439|None|
|offset_ood|33|ridge|0.37595|0.40895|0.64921|0.00000|
|offset_ood|33|mlp|0.57435|0.64338|0.98689|None|
|slow_ood|31|crossing63|0.21945|0.27225|0.53319|None|
|slow_ood|31|physical_curve_fit|0.10195|0.12141|0.21579|None|
|slow_ood|31|ridge|1.12906|1.20861|1.81777|0.00000|
|slow_ood|31|mlp|2.59824|2.70531|3.75153|None|
|slow_ood|32|crossing63|0.20779|0.26122|0.47970|None|
|slow_ood|32|physical_curve_fit|0.09905|0.11852|0.21709|None|
|slow_ood|32|ridge|1.08729|1.16405|1.76174|0.00000|
|slow_ood|32|mlp|2.53158|2.63835|3.67951|None|
|slow_ood|33|crossing63|0.22527|0.27517|0.57146|None|
|slow_ood|33|physical_curve_fit|0.10184|0.12426|0.23332|None|
|slow_ood|33|ridge|1.08962|1.16096|1.72718|0.00000|
|slow_ood|33|mlp|2.52510|2.62401|3.55486|None|

## 明确局限
- All ideal analytic RC simulations; no measured board/oscilloscope/hardware validation.
- Only tau=RC identifiable from normalized step; cannot identify R and C separately.
- Known unit input assumption; gain drift/offset break model and physical baseline.
- Sampling fixed10ms/32points; no parasitics, inductance, temperature or device aging modeled.
- Validation residual interval coverage has no guarantee for OOD; not certified tolerance.
- No physical device control or high-voltage actions. AI assisted learning prototype.

[逐样本/逐帧结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)
