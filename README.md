# 于跃｜Agent / AI 产品作品集

> 把高知识密度、强规则约束的业务流程拆解为可操作的产品模块，让 AI 输出可追溯、可复算。

[作品集主页](https://llewynlune.github.io/ai-portfolio/) · [GitHub 源码](https://github.com/LlewynLune/ai-portfolio) · [个人介绍](profile/README.md)

## 关于我

具备 AI 产品从 0—1 到上线试点的完整实践，擅长把高知识密度、强规则约束的业务流程拆解为可操作的产品模块。独立负责过审核工作台、混合审核策略、权限体系、数据看板和风险评分等功能设计，能够将专家经验沉淀为规则库、知识库与人工复核机制，让 AI 输出可追溯、可复算。

关注真实使用数据与 Badcase，习惯通过命中率、误报率、人工打回率和结论采纳率验证产品效果，并推动规则、Prompt 与知识库持续迭代。机电与电气工程背景，能读懂图纸和专业规范，可使用 Python、SQL 与 AI Coding 快速验证方案，适合需要领域理解、产品定义和 AI 落地判断的 Agent 产品岗位。

## 核心产品实践

|实践|本人职责|核心模块与结果|阶段|
|---|---|---|---|
|[AI 审图平台](business-cases/drawing-review/README.md)|立项发起；核心产品模块设计与上线|审核工作台、规则＋模型分级路由、账号权限、数据看板；11条规则、9条Prompt规则，6轮/300+ Badcase复盘，人工复核打回率低于1%|已上线、业务使用与迭代|
|[标准化线上平台](business-cases/standards-platform/README.md)|独立负责人；0—1自主搭建|条目级规则库、评审工作台、判定＋校验、人工复核、五级状态评分和风险看板|试点使用、配置化复用|
|[团队智能体技能空间与知识库](business-cases/skills-knowledge/README.md)|公共AI能力产品化|6个可复用Skill；10章、约446条术语；说明常驻、详情按需调用与版本回归|团队公共资产，支撑两项AI产品|
|[火山引擎 FORCE 大会宣传片](business-cases/force-aigc/README.md)|独立完整创作流程|创意、分镜、Prompt、主体/风格/衔接筛选与修正|文生视频草稿交付|

项目职责、阶段与指标来自本人提供并确认可公开的简历。未公开公司系统、图纸、客户材料、代码或原始统计记录；指标未在本仓库独立审计。打回率不改写为整体准确率，草稿不写成正式投放成果。

## 教育经历

- **新加坡南洋理工大学｜硕士在读，预计2028年毕业**。专业及入学日期未提供，不补写。
- **澳门大学｜科技学院·机电工程｜全日制本科，2021.08—2026.01**。
  模拟与混合信号超大规模集成电路国家重点实验室；校级学生干部。

## 产品方法

1. 领域规则结构化：明确适用范围、证据要求、偏离等级、责任人与操作权限。
2. 人机协作：规则/模型分级路由，判定与校验分层，低置信或证据不足转人工复核。
3. 数据闭环：任务与状态埋点、复核反馈、Badcase复盘，持续迭代规则、Prompt、知识召回和评分量表。
4. 可复用AI资产：将公共Skill、术语和规则分层管理，降低重复搭建与上下文占用。

## 研究与工程实验｜与业务实践分开展示

以下14项为AI辅助研究原型，代码、实验、日志与失败边界公开；不是上述业务平台的内部实现，也不包装成既往独立研发或生产成果。真实远程LLM接口未调用；Python实验仅本机运行，Pages是静态展示。

|实验|验证内容|入口|
|---|---|---|
|FlowBench|故障、有限重试、幂等恢复、BM25与崩溃回放|[Demo](projects/reliability-lab/demo.html) · [说明](projects/reliability-lab/README.md)|
|VideoGuard-Lab|音画同步、双塔对比、校准拒估、因果漂移定位；77项项目测试|[Demo](projects/video-guard/demo.html) · [定位](projects/video-guard/DRIFT.md) · [校准](projects/video-guard/CALIBRATION.md)|
|TextGuard|TF-IDF＋Logistic真实训练、留出与权重解释|[Demo](projects/textguard/demo.html) · [报告](projects/textguard/artifacts/REPORT.md)|
|CiteRAG|BM25/字符/RRF，引用、摘录与拒答|[Demo](projects/cite-rag/demo.html) · [报告](projects/cite-rag/artifacts/REPORT.md)|
|NoveltyLab|正常训练拟合、验证阈值、三模型与分布迁移|[Demo](projects/novelty-lab/demo.html) · [报告](projects/novelty-lab/artifacts/REPORT.md)|
|VisionCal|小型神经网络、温度校准与图像扰动|[Demo](projects/vision-cal/demo.html) · [报告](projects/vision-cal/artifacts/REPORT.md)|
|CircuitID|RC仿真辨识，物理/规则/学习对照|[Demo](projects/circuit-id/demo.html) · [报告](projects/circuit-id/artifacts/REPORT.md)|
|ChannelEst|理想频域导频估计、NMSE/BER和先验迁移|[Demo](projects/channel-est/demo.html) · [报告](projects/channel-est/artifacts/REPORT.md)|
|PowerScope|合成功率时序、计划特征消融、漂移失败|[Demo](projects/power-scope/demo.html) · [报告](projects/power-scope/artifacts/REPORT.md)|
|TinyAttention|因果注意力、真实CPU训练、无注意力消融与长度OOD|[Demo](projects/tiny-attention/demo.html) · [报告](projects/tiny-attention/artifacts/REPORT.md)|
|LoRA-Lab|冻结基座、rank1/4、合并校验与遗忘|[Demo](projects/lora-lab/demo.html) · [报告](projects/lora-lab/artifacts/REPORT.md)|
|DPO-Lab|reference、beta与SFT对照，偏好/准确率/KL分开|[Demo](projects/dpo-lab/demo.html) · [报告](projects/dpo-lab/artifacts/REPORT.md)|
|SparseMoE|真实top1专家分发、负载平衡与dense对照|[Demo](projects/moe-lab/demo.html) · [报告](projects/moe-lab/artifacts/REPORT.md)|
|SpecDecode|双模型训练、greedy块验证、逐token一致与CPU计时|[Demo](projects/spec-decode/demo.html) · [报告](projects/spec-decode/artifacts/REPORT.md)|

前三项前沿机制共享TinyAttention小型基座，不能视为独立大模型研究；电子/通信/功率项目为仿真与合成数据，非真实设备测试。数据和论文方法引用保留，不包含他人作品集或人才对标。

[前沿机制实验地图](docs/frontier-evidence.md) · [跨学科证据](docs/cross-disciplinary-evidence.md) · [数据与方法来源](docs/ai-project-reference.md) · [实验真实性](docs/ai-evidence.md)

## 复现与维护

- 结构、Markdown链接与敏感入口检查：python3 scripts/check_portfolio.py。
- 仓库回归：python3 -m unittest discover -s tests -v；各项目训练依赖与运行见对应README。
- VideoGuard：进入projects/video-guard，运行python3 -m unittest discover -s tests -v。
- 履历内容由profile/resume.json统一管理；python3 scripts/build_resume_portfolio.py重建主页面和四项案例文档，不重训模型。
- [公开披露与证据边界](PUBLISHING.md) · [GitHub维护](docs/github-setup-guide.md)。

当前内容版v0.9；发布状态以最新GitHub Actions为准。
