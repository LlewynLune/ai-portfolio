# DPO-Lab · 三种子真实偏好优化与SFT对照

偏好目标和单token正确率如何随真实训练变化，而非只做权重插值？

## 预声明实验协议

{
  "kind": "new_numpy_head_only_DPO_training",
  "seeds": [
    193001,
    193002,
    193003
  ],
  "train": 512,
  "validation": 128,
  "test": 192,
  "steps": 160,
  "learning_rate": 0.02,
  "beta": [
    0.1,
    0.5
  ],
  "policies": [
    "sft",
    "dpo_0.1",
    "dpo_0.5"
  ],
  "chosen_rule": "original+2",
  "labels": "synthetic one-token preference; not human alignment",
  "excluded_prior_ids": true
}

## 全部条件结果

|seed|policy|n|validation_chosen|test_pair_win|test_chosen_top1|original_retention|mean_reference_kl|
|---|---|---|---|---|---|---|---|
|193001|sft|192|0.42969|0.86979|0.46354|0.09375|3.6803|
|193001|dpo_0.1|192|0.11719|0.15104|0.14062|0.45833|0.091417|
|193001|dpo_0.5|192|0.24219|0.38542|0.25521|0.41667|0.81659|
|193002|sft|192|0.46875|0.86979|0.44792|0.098958|3.8158|
|193002|dpo_0.1|192|0.1875|0.17708|0.15104|0.44792|0.060715|
|193002|dpo_0.5|192|0.28125|0.38542|0.24479|0.39583|0.71028|
|193003|sft|192|0.39844|0.90104|0.45833|0.088542|3.6539|
|193003|dpo_0.1|192|0.10156|0.14583|0.14062|0.40104|0.078191|
|193003|dpo_0.5|192|0.14062|0.32812|0.21875|0.35417|0.69226|

## 发现、失败与适用边界

- NumPy手工梯度真实训练输出头，基座冻结；DPO概率比reference固定。
- 三个新划分同时冻结，无测试选beta或训练步数。验证仅报告，不用于挑最佳。
- 偏好为合成+2规则，赢率、chosen top1、KL和原规则保留分开；不是人类对齐。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project dpo-lab。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
