# PowerScope｜AI数据中心电力负荷的离线预测与漂移｜原理、对照与失败

## 数据的真实边界

本项目完全是作者仿真，没有字节机房遥测或公开真实AI机房数据。36天、5分钟粒度，日周期与随机批作业形成IT功率；冷却/损耗系数是源码明确的玩具假设，不能作为供应商设备曲线、工程额定或节能依据。

IT计划来自生成器作业schedule，加35kW噪声；使用下一时段计划而不是下一时段实测功率。仿真假设计划可提前知道，因此比完全不可知突变拥有额外信息；真实scheduler误差和延迟未验证。必须对“无计划”模型消融，否则优势来源不清楚。

### 时间因果协议

第1天用作lag288预热，前20天训练、后6天验证、最后10天测试。输入当前/滞后1/12/288时段总功率、当前IT、当前温度、时钟sin/cos与下一期计划IT。目标是下一步总功率，删掉跨训练/验证边界的目标行，不把未来目标引入fit。lag可使用已观测过去值，测试采用滚动一步预测，不是10天开放式多步预测。

StandardScaler只fit训练；Ridge alpha按验证MAE选。时间序列禁止随机打散Kfold。新增冷却漂移OOD是独立seed10天序列，冷却功率变为额外线性项+高温阶跃，不重新fit。

### 模型和结果

- Persistence：下一期等于当前值，强短期基线。
- 同日时刻lag288：当天同一时刻代替未来，验证作业随机性影响。
- Ridge_no_plan：移除计划特征，固定alpha10。
- Ridge_full：完整9维，预先规定其作为部署展示模型，即使验证MAE或测试MAE未胜出也不偷偷换口径。

MAE、RMSE、绝对误差95分位不等价：计划可降低突变的大误差，但平稳时引入噪声，提高MAE。必须分别解释，不能挑一个“提升率”。

验证残差90%经验带与玩具1200kW阈值只做离线标记，报告TP/FP/FN。不保证90%覆盖：时序相关破坏exchangeability，漂移会显著失效。其他模型共享该残差带仅作为统一flag规则，不代表各自校准区间。

### 电气工程底线

仅区间平均kW，不评估毫秒级电力暂态、电能质量、谐波、短路、保护配合、N+1/2N冗余、UPS/autonomy、切换控制或额定容量。窗口能量按5分钟求和折算kWh；同窗口facility/IT比值不是审计的年度PUE。不给真实控制指令，不输出设备设定值或投运建议。没有实测降本收益，也没有模型自动闭环。

## 本批原始证据

Authored synthetic36days at5min; train first20days, validation next6days, test last10days; lag288 requires firstday warmup. One-step forecasts use known-now sensors and noisy planned-next-IT input, never measured future facility power. Fixed cooling-drift10day OOD independent seed.

[完整表](artifacts/REPORT.md)保留所有组与seed；[JSON](artifacts/results.json)保留逐项预测、样本与运行环境。SHA校验只能发现变更，不是第三方签名。重新修改train.py或共享生成器后必须重跑，不得把旧结果重新打hash当新证据。

来源：https://www.energy.gov/cmei/femp/energy-efficiency-data-centers
