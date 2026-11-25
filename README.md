# 于跃 · AI Product Portfolio

**Agent 产品 / 领域知识产品化 / AI 工程验证**
机电工程背景，关注强规则、重证据的业务流程如何落地为可协作的 AI 产品。

[进入作品集](https://llewynlune.github.io/ai-portfolio/) · [产品实践](https://llewynlune.github.io/ai-portfolio/index.html#projects) · [研究与 Demo](https://llewynlune.github.io/ai-portfolio/index.html#experiments) · [个人介绍](profile/README.md)

## 从哪里开始

|你想了解的内容|建议阅读路径|
|---|---|
|我的产品职责与上线实践|先看 AI 审图和标准化评审两个案例|
|多模态实验与模型可靠性|运行 VideoGuard，再检查校准、定位和报警时限|
|Agent 执行框架与工程判断|查看 FlowBench 的故障策略、证据轨迹和恢复边界|
|前沿算法与工程交叉|阅读下方实验索引，按领域进入源码和冻结报告|

## Work Experience · 字节跳动

**ByteDance · 字节跳动｜工作经历**

领域 AI 产品实践：审核工作台、混合审核策略、标准评审、知识与 Skill。以下四项均由本人确认属于字节跳动工作经历；不标注实习或未经确认的正式职位、团队与任职日期。

[查看工作经历与项目成果](https://llewynlune.github.io/ai-portfolio/index.html#projects)

### [AI 审图平台](business-cases/drawing-review/README.md)
**立项发起 · 核心产品模块设计与上线**

将机电图纸审核组织为工作台、规则与模型分级路由、权限留痕和数据看板。完成 11 条规则、9 条审核 Prompt；经 6 轮、300+ Badcase 复盘，人工复核打回率低于 1%。

### [标准化线上平台](business-cases/standards-platform/README.md)
**独立负责人 · 0—1 搭建并投入试点**

将技术标准应答与偏离评审线上化：条目规则、证据校验、人工复核、五级状态评分和可复算风险看板，支持配置化复用。

### [团队 Skill 与知识空间](business-cases/skills-knowledge/README.md)
**AI 公共能力产品化**

沉淀 6 个可复用 Skill、10 章约 446 条术语，统一知识与调用口径；说明常驻、详细内容按需加载，服务两个产品。

### [FORCE 大会 AIGC 宣传片](business-cases/force-aigc/README.md)
**创意 · 分镜 · Prompt · 草稿交付**

独立完成创意到文生视频草稿的流程，围绕主体一致性、风格和镜头衔接进行筛选与修正。

> 以上职责、阶段和指标来自本人提供并确认可公开的履历。仓库不公开内部代码、图纸、客户材料或原始统计；打回率不等于整体准确率，草稿不等于正式投放。

## 两项代表性工程实验

### VideoGuard-Lab · 音画事件同步与可靠性

从 RGB / PCM 事件估计延时，比较相关性、MLP 与双塔表示；继续检查预测集合、局部矛盾、漂移定位与报警时限。

[Project Page](https://llewynlune.github.io/ai-portfolio/projects/video-guard/project.html) · [模型演示](https://llewynlune.github.io/ai-portfolio/projects/video-guard/demo.html) · [深化分析](https://llewynlune.github.io/ai-portfolio/projects/video-guard/depth-demo.html) · [代码与方法](projects/video-guard/README.md) · [定位报告](projects/video-guard/artifacts/drift-localization/REPORT.md)

### FlowBench · Agent 工作流可靠性

在同一故障清单下比较单次执行、有限重试与幂等恢复，追踪排队、失败、提交副作用和 SQLite 恢复。

[Project Page](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/project.html) · [交互实验台](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/demo.html) · [深化分析](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/depth-demo.html) · [源码与架构](projects/reliability-lab/README.md) · [工程报告](projects/reliability-lab/results/advanced/REPORT.md)

**这些实验为 AI 辅助实现的研究原型，不是上述业务平台的内部系统，也不包装成既往独立研发或生产成果。**

## 实验索引

<details>
<summary>展开全部 14 项 · 按领域查看</summary>

### 模型评测与知识检索

|项目|要验证的问题|阅读入口|
|---|---|---|
|TextGuard|词项变形、留出误判和可解释推断|[Demo](https://llewynlune.github.io/ai-portfolio/projects/textguard/demo.html) / [源码](projects/textguard/README.md)|
|VisionCal|置信校准与噪声、平移、遮挡|[Demo](https://llewynlune.github.io/ai-portfolio/projects/vision-cal/demo.html) / [源码](projects/vision-cal/README.md)|
|NoveltyLab|阈值、分布迁移与逐维扰动|[Demo](https://llewynlune.github.io/ai-portfolio/projects/novelty-lab/demo.html) / [源码](projects/novelty-lab/README.md)|
|CiteRAG|混合检索、内容去重与证据不足拒答|[Demo](https://llewynlune.github.io/ai-portfolio/projects/cite-rag/demo.html) / [源码](projects/cite-rag/README.md)|
|VideoGuard-Lab|音画同步、拒估、定位与报警时限|[Demo](https://llewynlune.github.io/ai-portfolio/projects/video-guard/demo.html) / [源码](projects/video-guard/README.md)|
|FlowBench|故障恢复、幂等和副作用证据|[Demo](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/demo.html) / [源码](projects/reliability-lab/README.md)|

### 算法机制

|项目|要验证的问题|阅读入口|
|---|---|---|
|TinyAttention|因果注意力、消融与长度外推|[Demo](https://llewynlune.github.io/ai-portfolio/projects/tiny-attention/demo.html) / [源码](projects/tiny-attention/README.md)|
|LoRA-Lab|低秩适配、合并与新旧任务取舍|[Demo](https://llewynlune.github.io/ai-portfolio/projects/lora-lab/demo.html) / [源码](projects/lora-lab/README.md)|
|DPO-Lab|偏好赢率、Top-1、KL 与遗忘|[Demo](https://llewynlune.github.io/ai-portfolio/projects/dpo-lab/demo.html) / [源码](projects/dpo-lab/README.md)|
|SparseMoE|专家容量、负载与丢弃|[Demo](https://llewynlune.github.io/ai-portfolio/projects/moe-lab/demo.html) / [源码](projects/moe-lab/README.md)|
|SpecDecode|逐 token 一致、真实 KV 缓存与开销|[Demo](https://llewynlune.github.io/ai-portfolio/projects/spec-decode/demo.html) / [源码](projects/spec-decode/README.md)|

### 电子、通信与电气 AI

|项目|要验证的问题|阅读入口|
|---|---|---|
|CircuitID|RC 参数、未知增益与偏置拟合|[Demo](https://llewynlune.github.io/ai-portfolio/projects/circuit-id/demo.html) / [源码](projects/circuit-id/README.md)|
|ChannelEst|缺失导频、NMSE 与欠定拒估|[Demo](https://llewynlune.github.io/ai-portfolio/projects/channel-est/demo.html) / [源码](projects/channel-est/README.md)|
|PowerScope|时间留出、负荷漂移与区间覆盖|[Demo](https://llewynlune.github.io/ai-portfolio/projects/power-scope/demo.html) / [源码](projects/power-scope/README.md)|

</details>

[14 项深化清单](docs/project-depth.md) · [复现与本机 API](docs/depth-engineering.md) · [数据与方法来源](docs/ai-project-reference.md)

## 教育与方向

- **南洋理工大学** · 硕士在读，预计 2028 年毕业。
- **澳门大学** · 科技学院机电工程本科，2021.08—2026.01；模拟与混合信号超大规模集成电路国家重点实验室，校级学生干部。
- **产品方法** · 规则与证据结构化、人机协同、Badcase 数据闭环、公共知识与 Skill 复用。

## 运行与证据

项目源码、测试和运行指南在各项目 README；主页与 Demo 是静态展示。原始协议、冻结模型、失败记录和新旧证据保留。

- 结构与链接检查：python3 scripts/check_portfolio.py。
- 仓库测试：python3 -m unittest discover -s tests -v。
- 履历事实源：profile/resume.json；主页生成器不重训模型或修改案例事实。

<details>
<summary>贡献与适用边界</summary>

研究代码与实验由 AI 辅助实现，本人独立理解、修改与复核贡献应如实记录。LoRA / DPO 共享 TinyAttention 小型基座；电子、通信和电力为仿真或合成数据，未做设备实测。真实 LLM 接口未调用，静态发布不是 Python 后端或生产上线。

同一输入的扰动、门限分析与重复计时并非独立样本；高分和记录数不证明泛化。本人教育未提供的专业和入学月份不补写。

[完整披露](PUBLISHING.md) · [实验真实性](docs/ai-evidence.md) · [前沿机制证据](docs/frontier-evidence.md)

</details>

展示版本 v1.7 · 四项真实产品成果归入本人确认的字节跳动工作经历，采用公司标识、经历信息与项目贡献的展示方式。研究项目与实验数据不变。
