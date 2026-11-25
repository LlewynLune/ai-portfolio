# ChannelEst · 导频几何与错误模型阶数

观测数量够了是否就可可靠估计？导频几何和错误四径假设带来什么风险？

## 预声明实验协议

{
  "kind": "pilot_geometry_vs_model_order",
  "actual_taps": [
    2,
    4,
    8
  ],
  "assumed_taps": 4,
  "snr_db": 20,
  "n_per_group": 120,
  "pilot_indices": {
    "spread": [
      0,
      8,
      16,
      24
    ],
    "clustered": [
      0,
      4,
      8,
      12
    ],
    "full": [
      0,
      4,
      8,
      12,
      16,
      20,
      24,
      28
    ]
  },
  "seed": 197001,
  "baselines": [
    "4tap_ls",
    "ridge_regularized_ls"
  ]
}

## 全部条件结果

|actual_taps|geometry|method|n|observations|rank|condition_number|mean_nmse|p95_nmse|
|---|---|---|---|---|---|---|---|---|
|2|spread|4tap_ls|120|4|4|1|0.0169|0.054758|
|2|spread|ridge_regularized_ls|120|4|4|1|0.016848|0.054909|
|2|clustered|4tap_ls|120|4|4|15.257|0.40391|1.3354|
|2|clustered|ridge_regularized_ls|120|4|4|15.257|0.25897|0.82933|
|2|full|4tap_ls|120|8|4|1|0.0085609|0.027939|
|2|full|ridge_regularized_ls|120|8|4|1|0.0085527|0.027829|
|4|spread|4tap_ls|120|4|4|1|0.014401|0.03376|
|4|spread|ridge_regularized_ls|120|4|4|1|0.014369|0.033047|
|4|clustered|4tap_ls|120|4|4|15.257|0.46303|1.6428|
|4|clustered|ridge_regularized_ls|120|4|4|15.257|0.2882|1.0209|
|4|full|4tap_ls|120|8|4|1|0.0076192|0.02313|
|4|full|ridge_regularized_ls|120|8|4|1|0.0076046|0.023217|
|8|spread|4tap_ls|120|4|4|1|0.26637|0.59202|
|8|spread|ridge_regularized_ls|120|4|4|1|0.26566|0.59021|
|8|clustered|4tap_ls|120|4|4|15.257|8.0908|21.867|
|8|clustered|ridge_regularized_ls|120|4|4|15.257|4.9373|13.53|
|8|full|4tap_ls|120|8|4|1|0.13238|0.29157|
|8|full|ridge_regularized_ls|120|8|4|1|0.13237|0.29154|

## 发现、失败与适用边界

- 秩、condition number与NMSE一起报告，观测数量不等于可辨识质量。
- ridge正则固定0.01与已知噪声，未在测试选参数；8tap是模型阶数失配。
- 理想频域仿真，无射频硬件/5G6G指标或现场性能。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project channel-est。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
