# CircuitID｜噪声RC阶跃的学习型系统辨识｜模型卡

## 模型与预期用途

理想RC阶跃生成 → 随机tau/增益/噪声 → 32点观测 → 63%规则/物理拟合/Ridge/MLP → 验证选型 → 多seed与OOD → 波形重建和残差带。

默认导出类型：linear；输入维数32。仅离线学习、参数推断、复现与失败分析。

## 数据、训练与测试

Independent synthetic RC step waveforms: train1800, validation400, 4 test groups x3 seeds x160. Tau0.5–3ms train; slow OOD4–6ms. Ridge alpha and default model chosen only validation; physical solver does not train.

[实际指标](artifacts/REPORT.md)不是生产指标，也没有第三方审计。训练环境记录在[结果](artifacts/results.json)中，代码和数据/参数哈希不证明专业资质。

## 禁止外推

- All ideal analytic RC simulations; no measured board/oscilloscope/hardware validation.
- Only tau=RC identifiable from normalized step; cannot identify R and C separately.
- Known unit input assumption; gain drift/offset break model and physical baseline.
- Sampling fixed10ms/32points; no parasitics, inductance, temperature or device aging modeled.
- Validation residual interval coverage has no guarantee for OOD; not certified tolerance.
- No physical device control or high-voltage actions. AI assisted learning prototype.

## 人机分工与退出

页面只显示模型输出和假设；缺失输入/维数错误/非有限数拒绝。修改输入后不再显示预设样本标签作为真值。分布外、无真实标签、数据可用性不足时必须人工调查，不把模型倾向写成事实。

## 贡献与许可

AI辅助学习实现，用户提出范围；本人独立贡献尚待亲自修改与验证，不以此冒充已掌握的研究经历。数据/参考许可分别适用，仓库暂未统一授予开源许可证。
