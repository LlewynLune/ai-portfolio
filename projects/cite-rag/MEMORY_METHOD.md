# CiteRAG · Source-backed Agent Memory

本轮只深化现有 CiteRAG，不把模型接口、记忆模块和实验阶段拆成新项目。

## 研究问题

跨任务保留的模型笔记是否仍可当作事实？来源撤销、修订、互相冲突或记忆污染时，生成器能否给出有证据的结论；上下文预算是否会破坏证据完整性？

产品背景来自本人重规则、重证据的AI产品实践；实验内容全部为自建虚构软件设置，不是公司项目的数据或内部规范。

## 前沿来源与本作品的差别

2026-11-25核验公开原始资料。

- Anthropic：[The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory)（2026-11-06）。区分跨session笔记、原始记录检索和离线整理，讨论记忆纠错、层级与失效；本文实现来源回放与有限格式检查，没有复刻Claude的学习能力或专有实现。
- Anthropic：[Harness design for long-running apps](https://www.anthropic.com/research/harness-design-long-running-apps)（2026-03-24）。强调执行与评估分工、结构化交接、组件消融及开销；本文使用独立确定性校验器，不把同一LLM自评当真值。
- Kimi：[K3.1 Pro技术博客](https://www.kimi.ai/blog/kimi-k3-1-pro)（官网入口标2026-10-24）。长程任务、工具使用与端到端交付是主要方向之一；本作品不是旗舰运行或RL复现，不引用其榜单数字作本项目结果。
- Seed：[公开论文目录](https://seed.bytedance.com/zh/public_papers?view_from=ICLR)列出Cortex、HarnessDev等近期方向。只核验目录，不声称已阅读/复现其全文，也不将目录标题自动当技术实现依据。

可访问内部材料只用于选题，不进入公开仓库、Prompt、训练或结果包；可访问不等于获准公开。公开机制与本作品代码自行实现，未复制内部源码。

## 架构取舍

1. 来源事件：不可变ID、namespace、条目key、修订号、撤销状态、文本。
2. 模型整理：真实本地模型输出notes，附source IDs与原文quotes；原始输出冻结。
3. 来源回放：检查模型note是否可被当前原文支持，旧/撤销/跨namespace/错值记录审计；按来源重建当前记忆，冲突不静默覆盖。
4. 上下文：固定token预算下检索；v1按单条装入，v2按条目组原子装入，减少冲突证据被拆开。
5. 本地模型生成：预下载safetensors、离线MLX、固定greedy、有限Prompt与输出token，不访问工具或付费API。
6. 独立校验：schema、引用可见性、版本、撤销、全源冲突、精确单位与双证据整数加法；无法核验就显式拒答。
7. 持久化与审计：SQLite、幂等来源写入、原文hash、追加hash链；关闭后重开验证。不是完整鉴权系统。

## 为什么保留传统代码基线

这里的Setting语法是有限且已知的，传统解析器可完成全部题目。模型不是必要条件。作品验证的是“来源、上下文与生成契约”的可靠性，不把小合成数据上的高分当作通用Agent智能。

## 版本与失败

主实验、污染挑战、预算消融、v2修复各用独立目录。v1失败不回填修复结果，v2是在看过同模板结果后开发的探索性回归，不称独立留出泛化。

初轮数字JSON类型错误、过小上下文隐藏冲突、模型记忆与回放同分等不利结论全部保留。汇总结果见 [实测报告](artifacts/memory/REPORT.md)，运行界面为真实证据回放而非网页内跑完整LLM。

## 贡献与适用边界

用户提出项目目标和产品背景，代码、实验设计与文档由AI辅助实现并在本机运行；不能写为既往独立研发、论文或生产平台。没有真人测试、自然语言NLI、数日自主学习、parametric memory、LLM预训练或RL。无内部数据、付费API或电气设备控制。
