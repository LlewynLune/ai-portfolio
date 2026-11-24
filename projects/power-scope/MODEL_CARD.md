# PowerScope｜AI数据中心电力负荷的离线预测与漂移｜模型卡

## 模型与预期用途

合成作业计划/室外温度 → 透明IT/冷却/损耗模型 → 当前及历史特征 → 时间留出Ridge/持久性/季节基线 → 计划特征消融 → 峰值标记和漂移分析 → 只读Dashboard。

默认导出类型：linear；输入维数9。仅离线学习、参数推断、复现与失败分析。

## 数据、训练与测试

Authored synthetic36days at5min; train first20days, validation next6days, test last10days; lag288 requires firstday warmup. One-step forecasts use known-now sensors and noisy planned-next-IT input, never measured future facility power. Fixed cooling-drift10day OOD independent seed.

[实际指标](artifacts/REPORT.md)不是生产指标，也没有第三方审计。训练环境记录在[结果](artifacts/results.json)中，代码和数据/参数哈希不证明专业资质。

## 禁止外推

- All traces/scheduler forecasts/cooling/loss factors are authored simulation, no real ByteDance or external facility telemetry.
- 5min interval average power; cannot evaluate subsecond electrical transients.
- Toy1200kW threshold not equipment rating, redundancy margin or breaker limit.
- Interval from chronological validation residuals; autocorrelation violates exchangeability, no guaranteed90% coverage.
- Same-window ratio not audited annual PUE; no measured energy saving.
- Forecast only: no control commands, switchgear/cooling setpoints, UPS/protection coordination or safety approvals.
- AI assisted research prototype; offline only and human review required.

## 人机分工与退出

页面只显示模型输出和假设；缺失输入/维数错误/非有限数拒绝。修改输入后不再显示预设样本标签作为真值。分布外、无真实标签、数据可用性不足时必须人工调查，不把模型倾向写成事实。

## 贡献与许可

AI辅助学习实现，用户提出范围；本人独立贡献尚待亲自修改与验证，不以此冒充已掌握的研究经历。数据/参考许可分别适用，仓库暂未统一授予开源许可证。
