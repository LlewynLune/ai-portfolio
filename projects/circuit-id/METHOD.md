# CircuitID｜噪声RC阶跃的学习型系统辨识｜原理、对照与失败

## 物理任务而非算法名字

理想归一化输入阶跃下，$v(t)=1-\exp(-t/\tau)$，$\tau=RC$。单个归一化阶跃只能辨识乘积RC；本实验不会输出独立R和C，也不把tau称为元件寿命或故障概率。

固定0–10ms共32采样点。训练/验证tau0.5–3ms，增益0.98–1.02，独立高斯噪声幅度0.005–0.025。生成器解析公式是模型假设，不是测量数据。所有测试seed不与训练验证重合，同seed各方法共享同一波形。

### 四个对照

- 63%穿越规则：第一次超过 $1-e^{-1}$ 的采样时刻；采样离散会偏差。
- 物理曲线拟合：最小化单位指数响应误差，在logtau区间0.1–12ms求解。已知函数族且搜索范围更宽，不是完全同条件学习对照。
- Ridge：标准化只fit训练，学习logtau，alpha仅验证从0.1/1/10选择。
- MLP：32→48 tanh→1，训练logtau；对比非线性模型不自动代表更强。

只比较两类学习模型的验证MAE，确定默认模型；物理法始终在完整测试表展示。学习输出经过exp还原，确保正tau。浏览器按导出参数推断，不依赖后端或预设答案。

### 泛化与不确定性

训练1800，验证400；4个组×3seed×160测试：同分布、强噪声、+0.10固定偏置、慢tau4–6ms。报告MAE、RMSE、绝对误差95分位；各seed不只报一个漂亮结果。每组保留最坏示例，说明采样/范围/模型假设如何失败。

残差带从验证绝对误差有限样本90%分位计算，仅作为经验区间。分布外偏置/慢响应不满足相同条件，实际覆盖率可接近0；不称“90%可靠”或元件验收公差。

### 工程边界

没有SPICE、PCB、示波器、真实ADC/寄生参数/温漂/量化模型；不是电路设计签核。32点采样已假设对齐，缺失采样和输入幅值误差未解决。项目只在离线低压归一化数学仿真中学习，不接触实际设备或高压电气操作。

## 本批原始证据

Independent synthetic RC step waveforms: train1800, validation400, 4 test groups x3 seeds x160. Tau0.5–3ms train; slow OOD4–6ms. Ridge alpha and default model chosen only validation; physical solver does not train.

[完整表](artifacts/REPORT.md)保留所有组与seed；[JSON](artifacts/results.json)保留逐项预测、样本与运行环境。SHA校验只能发现变更，不是第三方签名。重新修改train.py或共享生成器后必须重跑，不得把旧结果重新打hash当新证据。

来源：https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits
