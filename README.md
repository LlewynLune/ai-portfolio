# 于跃 | AI Product Portfolio

Agent / AI 产品 · 机电与电气工程背景

[作品集主页](https://llewynlune.github.io/ai-portfolio/) · [GitHub 源码](https://github.com/LlewynLune/ai-portfolio) · [个人介绍](profile/README.md)

## 关于我

我关注专业知识密集、强规则约束场景中的 Agent 产品。我的实践从机电审图和技术标准评审出发：将专家经验转成规则与知识，再组织为可协作、可追溯、可复算的产品流程。

我负责过审核工作台、混合审核策略、权限、风险评分与数据看板的设计，推动产品上线或试点。工作中将判定与证据校验分层，以人工复核管理高风险结论，并通过真实使用数据和 Badcase 持续迭代。

此外，我在 AI 辅助下搭建了14项研究与工程原型，覆盖多模态可靠性、Agent工作流、知识检索、大模型算法机制，以及电子、通信与AI数据中心场景。源码、Demo、实验报告和失败记录公开；AI辅助实现与本人独立复核分开记录，不以项目数量代替独立能力证明。

## 产品实践

### [AI 审图平台](business-cases/drawing-review/README.md)
**于跃 · 立项发起 / 核心产品模块设计与上线**

已上线，业务使用与持续迭代。

审核工作台、规则＋模型分级路由、账号权限和数据看板。11 条结构化规则、9 条模型 Prompt 规则；6 轮、300+ Badcase 复盘，人工复核打回率低于 1%。

### [标准化线上平台](business-cases/standards-platform/README.md)
**于跃 · 独立负责人 / 0—1 自主搭建**

试点使用，配置化复用。

将技术标准应答与偏离评审线上化；条目级规则、判定＋校验、人工复核、五级状态评分和可复算风险看板。

### [团队智能体技能空间与知识库](business-cases/skills-knowledge/README.md)
**于跃 · AI 基建产品化 / 公共资产沉淀**

团队公共资产，服务两项 AI 产品。

6 个可复用 Skill；10 章、约 446 条术语。技能说明常驻、详细知识按需调用，版本更新同步回归。

### [火山引擎 FORCE 大会宣传片](business-cases/force-aigc/README.md)
**于跃 · 独立完整创作流程**

文生视频草稿交付。

从创意、分镜到 Prompt，按镜头筛选与修正主体、风格和衔接；交付状态不等于正式投放。

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
- 履历内容由 profile/resume.json 管理；python3 scripts/build_resume_portfolio.py 确定性重建主页，不修改既有案例文档或重训模型。
- [公开披露与证据边界](PUBLISHING.md) · [GitHub维护](docs/github-setup-guide.md)。

当前展示版 v1.2：固定深灰导航、星空首屏、半透明个人资料面板和左图右文成果排列。四项真实产品实践与14项AI辅助实验分开；研究缩略图来自实际Demo，业务图仅为模块示意。个人头像采用本人上传照片，按现有头像框等比适配并移除元信息。发布状态以最新 GitHub Actions 为准。
