# 于跃 / LlewynLune

> 十三个AI辅助研究项目：因果注意力、LoRA、DPO、稀疏MoE、推测解码和视觉/通信/电子/功率/工作流。小模型/共享基座/合成数据如实说明，不冒充大模型研究或既往独立成果。

## 关于我

我正在建设一个围绕真实用户问题、可验证实验和稳定交付的 AI 作品集。

当前状态：代码与静态展示已公开；AI 辅助实现与个人贡献分开记录。

## 我关注的问题

- 如何把 AI 能力放进真实工作流，而不是只生成一次性回答。
- 如何用基线、评测和失败样本判断 AI 是否真的有效。
- 如何通过可靠的工程机制处理异常、复现和成本问题。

## 作品集入口

[完整代码与文档](https://github.com/LlewynLune/ai-portfolio) · [作品集网站](https://llewynlune.github.io/ai-portfolio/) · [在线交互展示](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/demo.html)

## 项目

**FlowBench｜AI 工作流可靠性实验台**

围绕暂时性错误、永久错误、慢任务和提交应答丢失，比较重试、超时、检查点与幂等提交。包含本地运行时、固定故障清单、原始实测、交互页面与测试。

AI 辅助搭建；合成 I/O 而非模型推理，无生产降本结论。个人理解、修改和实验贡献待记录。

包含真实本机计时的原始实验、故障轨迹和复现说明；v0.2 新增本地 BM25、困难改写组、进程崩溃恢复与参数扫描。在线页面只展示实测，重新运行须启动本机 Python 服务。

## 前沿机制五项目

- TinyAttention：单块因果注意力、训练与消融，键值查找仍有明显失败。
- LoRA-Lab：rank1/4真实低秩更新、冻结与合并校验、原任务遗忘。
- DPO-Lab：规则单token偏好、reference与SFT对照，pair win与top1分开。
- SparseMoE：4expert真实top1分发、负载平衡和dense对照。
- SpecDecode：两模型CPU训练，greedy块验证和实际计时；并非随机采样分布保持。

源目录与原理见完整作品集v0.5，线上部署状态以最新GitHub Actions为准。经典机制学习复现，不是最新论文、大模型或生产成果；前三项共享小型基座。

## 跨学科四项目

- [VisionCal](https://llewynlune.github.io/ai-portfolio/projects/vision-cal/demo.html)：小型神经网、置信校准与图像扰动；公开数据训练，不是大型视觉模型。
- [CircuitID](https://llewynlune.github.io/ai-portfolio/projects/circuit-id/demo.html)：噪声RC阶跃的学习辨识，对照物理拟合；仿真，非台架实测。
- [ChannelEst](https://llewynlune.github.io/ai-portfolio/projects/channel-est/demo.html)：导频到信道数据驱动估计、BER/NMSE；理想频域仿真，非无线设备。
- [PowerScope](https://llewynlune.github.io/ai-portfolio/projects/power-scope/demo.html)：AI机房下一步功率预测，计划消融与漂移；合成时序，只读研究，不控制设备。

v0.5已纳入四个跨学科项目源码；部署状态以最新Actions为准。十三个项目均AI辅助，个人独立贡献如实待记录。

## 新三项目

- **TextGuard**：真实 TF-IDF＋Logistic 训练，去重、留出评测、误判、权重推断；[交互模型](https://llewynlune.github.io/ai-portfolio/projects/textguard/demo.html)。旧英文短信，不是现代诈骗检测。
- **CiteRAG**：BM25/字符/RRF，引用、摘录与拒答；[交互检索](https://llewynlune.github.io/ai-portfolio/projects/cite-rag/demo.html)。真实 LLM 接口未调用，不把本地摘录叫大模型效果。
- **NoveltyLab**：正常训练拟合、验证阈值、三模型对照；[交互推断](https://llewynlune.github.io/ai-portfolio/projects/novelty-lab/demo.html)。类别迁移不是工业故障标签。

四项目的代码/测试/文档 AI 辅助完成，本人独立修改与复核贡献待记录。基线模型不重复计成独立项目。

## 公开链接

[GitHub](https://github.com/LlewynLune)；未公开邮箱、工作经历、教育或内部资料。

## 原则

- 不把团队成果写成个人独立成果。
- 不把未测量的预期收益写成真实数字。
- 不上传内部文档、代码、数据、截图或凭证。
- 原型、模拟、复现和上线分别标注。
