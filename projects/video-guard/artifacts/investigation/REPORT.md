# VideoGuard · 流式因果验证与观测丢失

未来窗口是否改变已经发出的报警？少量观测窗口丢失会损害及时检测吗？

## 预声明实验协议

{
  "kind": "prefix_causality_and_observation_dropout",
  "groups": [
    "step",
    "multiple",
    "quiet_gap",
    "stable"
  ],
  "clips_per_group": 30,
  "methods": [
    "raw",
    "onset",
    "mlp"
  ],
  "drop_every": [
    0,
    3,
    5
  ],
  "event_delay_frames": 20,
  "tolerance_frames": 16,
  "original_configs_frozen": true,
  "kind_of_evidence": "historical trajectories, no new media"
}

## 全部条件结果

|condition|method|drop_every|n|tp|fp|fn|f1|
|---|---|---|---|---|---|---|---|
|step|raw|0|30|3|27|27|0.1|
|step|raw|3|30|1|29|29|0.033333|
|step|raw|5|30|1|29|29|0.033333|
|step|onset|0|30|1|29|29|0.033333|
|step|onset|3|30|0|30|30|0|
|step|onset|5|30|0|30|30|0|
|step|mlp|0|30|3|27|27|0.1|
|step|mlp|3|30|0|30|30|0|
|step|mlp|5|30|1|29|29|0.033333|
|multiple|raw|0|30|6|56|54|0.098361|
|multiple|raw|3|30|0|60|60|0|
|multiple|raw|5|30|6|55|54|0.099174|
|multiple|onset|0|30|3|57|57|0.05|
|multiple|onset|3|30|0|60|60|0|
|multiple|onset|5|30|3|57|57|0.05|
|multiple|mlp|0|30|6|55|54|0.099174|
|multiple|mlp|3|30|0|60|60|0|
|multiple|mlp|5|30|6|54|54|0.1|
|quiet_gap|raw|0|30|0|30|30|0|
|quiet_gap|raw|3|30|0|30|30|0|
|quiet_gap|raw|5|30|0|30|30|0|
|quiet_gap|onset|0|30|0|30|30|0|
|quiet_gap|onset|3|30|0|30|30|0|
|quiet_gap|onset|5|30|0|30|30|0|
|quiet_gap|mlp|0|30|0|30|30|0|
|quiet_gap|mlp|3|30|0|30|30|0|
|quiet_gap|mlp|5|30|0|30|30|0|
|stable|raw|0|30|0|0|0|0|
|stable|raw|3|30|0|0|0|0|
|stable|raw|5|30|0|0|0|0|
|stable|onset|0|30|0|0|0|0|
|stable|onset|3|30|0|0|0|0|
|stable|onset|5|30|0|0|0|0|
|stable|mlp|0|30|0|0|0|0|
|stable|mlp|3|30|0|0|0|0|
|stable|mlp|5|30|0|0|0|0|

## 发现、失败与适用边界

- 逐前缀重新检测与完整运行已发报警精确一致，测试的是无未来信息正确性。
- 观测丢失固定跳过窗口，时间戳不重写；报警错过时限不补信用。
- 历史媒体轨迹再分析，不是新增真实视频；不重选阈值。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project video-guard。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
