# 14项研究工程项目｜深化批次

本批为AI辅助代码增量、新压力实验与冻结证据再分析；不新增项目计数、不重训大模型、不修改四项真实业务履历。

## 每项实际增量

|项目|新增内容|记录|入口|
|---|---|---:|---|
|video-guard|新增同时约束定位容差与实际报警延迟的事件匹配，比较500–2000ms时限；明确回溯边界准确不等于及时报警。|7200|[Demo](https://llewynlune.github.io/ai-portfolio/projects/video-guard/depth-demo.html) / [报告](../projects/video-guard/artifacts/depth/REPORT.md)|
|reliability-lab|新增81次真实本地异步负载实验，分故障/并发/种子比较策略；增加SQLite重开后暂停恢复和重复副作用核验。|1296|[Demo](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/depth-demo.html) / [报告](../projects/reliability-lab/artifacts/depth/REPORT.md)|
|cite-rag|新增内容指纹去重的RRF检索模块，在重复文档与无关文档注入下对照排名、拒答和可追踪摘录。|150|[Demo](https://llewynlune.github.io/ai-portfolio/projects/cite-rag/depth-demo.html) / [报告](../projects/cite-rag/artifacts/depth/REPORT.md)|
|textguard|新增词项变形不变性、拼写/否定/未知语言探针；复查原测试的保留覆盖率与错误率，不将启发式门限当安全保证。|120|[Demo](https://llewynlune.github.io/ai-portfolio/projects/textguard/depth-demo.html) / [报告](../projects/textguard/artifacts/depth/REPORT.md)|
|novelty-lab|新增13维单特征标准化扰动与决策翻转；距离归因改为相对拟合中心的平方贡献，明确相关变体不能当独立样本。|8515|[Demo](https://llewynlune.github.io/ai-portfolio/projects/novelty-lab/depth-demo.html) / [报告](../projects/novelty-lab/artifacts/depth/REPORT.md)|
|vision-cal|新增8种图像噪声/平移/中心遮挡条件和置信门限风险覆盖曲线；保留测试温度失效与高置信错误。|5760|[Demo](https://llewynlune.github.io/ai-portfolio/projects/vision-cal/depth-demo.html) / [报告](../projects/vision-cal/artifacts/depth/REPORT.md)|
|tiny-attention|新增NumPy独立推断、逐前缀因果一致性、长度2–7/顺序/未知query压力；新前缀排除原训练/验证/测试ID。|960|[Demo](https://llewynlune.github.io/ai-portfolio/projects/tiny-attention/depth-demo.html) / [报告](../projects/tiny-attention/artifacts/depth/REPORT.md)|
|lora-lab|新增真实低秩增量重构、6档适配强度与新旧任务保留曲线，检查merged导出的数值一致性；不重训选最佳测试强度。|1920|[Demo](https://llewynlune.github.io/ai-portfolio/projects/lora-lab/depth-demo.html) / [报告](../projects/lora-lab/artifacts/depth/REPORT.md)|
|dpo-lab|新增冻结输出头的插值对照，分开报告pair win、chosen top1、KL与旧任务保留；新前缀排除原数据ID。|1080|[Demo](https://llewynlune.github.io/ai-portfolio/projects/dpo-lab/depth-demo.html) / [报告](../projects/dpo-lab/artifacts/depth/REPORT.md)|
|moe-lab|新增有限专家容量、丢弃及第二选择路由；同时报告全批误差、接收覆盖率与仅接收项误差，避免隐藏丢弃。|4096|[Demo](https://llewynlune.github.io/ai-portfolio/projects/moe-lab/depth-demo.html) / [报告](../projects/moe-lab/artifacts/depth/REPORT.md)|
|spec-decode|新增真实单层增量KV缓存，对照全前缀重算；24新探针、三次计时，k1/2/4精确greedy路径验证。|144|[Demo](https://llewynlune.github.io/ai-portfolio/projects/spec-decode/depth-demo.html) / [报告](../projects/spec-decode/artifacts/depth/REPORT.md)|
|circuit-id|新增增益/偏置未知条件下的变量投影物理拟合，对照单位输入拟合与冻结Ridge；保留长tau不可辨识风险。|1200|[Demo](https://llewynlune.github.io/ai-portfolio/projects/circuit-id/depth-demo.html) / [报告](../projects/circuit-id/artifacts/depth/REPORT.md)|
|channel-est|新增缺失导频输入与观测导频LS对照，少于4观测时显式拒估；零填充值不能冒充已观测数据。|1440|[Demo](https://llewynlune.github.io/ai-portfolio/projects/channel-est/depth-demo.html) / [报告](../projects/channel-est/artifacts/depth/REPORT.md)|
|power-scope|新增每日时间块偏差/尾差、区间宽度与覆盖率诊断、线性贡献复算；仅分析冻结预测，不控制电气设备。|5470|[Demo](https://llewynlune.github.io/ai-portfolio/projects/power-scope/depth-demo.html) / [报告](../projects/power-scope/artifacts/depth/REPORT.md)|

本批共39351条记录；其中含同一媒体的门限重分析、相关扰动和重复计时，不等于独立真实样本数量。

## 工程使用

- 原Demo继续运行模型推断；Depth Study用于条件/模型/指标选择、失败筛选、分页、逐条下钻、专属诊断与导出。
- 离线HTML内联全部证据，无账号、密钥或远程网络请求。
- scripts/depth_server.py是只读localhost分页API，提供health/projects/evidence；不公网部署、不执行模型训练或外部调用。
- 复现依赖见requirements-depth.txt，运行对应depth.py，再用scripts/build_depth_demos.py重建。
- NumPy独立Attention前缀/KV缓存、LoRA合并、MoE容量、导频拒估、RC拟合、API只读和来源哈希均有专项测试。

## 不能宣称

无真实LLM调用、生产服务、硬件实测、真实视频标注、原创论文或全部本人独立研发。固定公开数据、合成/仿真与旧结果再分析性质逐项保留。可运行和记录数不是满分证明。
