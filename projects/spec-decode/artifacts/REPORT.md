# SpecDecode-Lab｜冻结运行结果

Independent tiny causal next-token models trained on48 synthetic modular-recurrence initial states;8validation/8test states. Target700steps d32, draft250steps d16. Evaluation measures greedy equivalence and actual CPU timing,8outputs after4token prompt,k2/k4,3 paired repeats,warmup; noKV cache.

|k|repeat|prompts|exact_prompts|baseline_ms|speculative_ms|speed_ratio_baseline_over_spec|target_calls|draft_calls|acceptance_checked|
|---|---|---|---|---|---|---|---|---|---|
|2|0|8|8|21.48512|31.55981|0.68077|33|65|0.65385|
|2|1|8|8|21.23275|31.36544|0.67695|33|65|0.65385|
|2|2|8|8|21.26095|31.28152|0.67966|33|65|0.65385|
|4|0|8|8|21.43287|40.92135|0.52376|30|100|0.69492|
|4|1|8|8|20.97462|40.54971|0.51726|30|100|0.69492|
|4|2|8|8|21.40031|40.94577|0.52265|30|100|0.69492|

## 边界
- Implements deterministic greedy block verification only, not rejection-sampling distribution preservation.
- Synthetic recurrence state paths overlap later; test is inference-correctness probe, not generalization score.
- NoKV cache/GPU/parallel kernels; Python tiny CPU models can be slower despite fewer target calls.
- Includes draft time and verification time; speed ratio is actual this environment only, not service throughput.
- Target path is reference, not correctness against arithmetic labels.
- No inference service, foundation-model accelerator or original algorithm claims.

[逐条结果](results.json) · [模型参数](model.json) · [哈希](checksums.json)
