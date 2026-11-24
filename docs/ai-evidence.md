# 实验与真实性清单

## 当前事实

当前仓库包含四项履历产品案例，以及14项AI辅助研究与工程原型，两者不混合计数。以下具体评测表保留早期三个项目的实验口径；其余项目证据见下方完整入口。对照模型和模块不拆为新项目，不将AI辅助实现写成本人独立研发、论文贡献或生产上线。

## 完整实验入口

- 多模态与模型评估：[VideoGuard-Lab](../projects/video-guard/README.md)、[VisionCal](../projects/vision-cal/README.md)、[NoveltyLab](../projects/novelty-lab/README.md)、[TextGuard](../projects/textguard/README.md)。
- Agent与检索：[FlowBench](../projects/reliability-lab/README.md)、[CiteRAG](../projects/cite-rag/README.md)。
- 算法机制：[TinyAttention](../projects/tiny-attention/README.md)、[LoRA-Lab](../projects/lora-lab/README.md)、[DPO-Lab](../projects/dpo-lab/README.md)、[SparseMoE](../projects/moe-lab/README.md)、[SpecDecode](../projects/spec-decode/README.md)。
- 跨学科仿真：[CircuitID](../projects/circuit-id/README.md)、[ChannelEst](../projects/channel-est/README.md)、[PowerScope](../projects/power-scope/README.md)。

AI辅助生成与执行的代码、报告，不等于本人已经独立掌握全部实现。本人后续重跑、修改和解释应另记证据，不以主页包装替代复核。

TextGuard 与 NoveltyLab 已在云端实际训练/拟合，CiteRAG 已运行本地检索评测；FlowBench 原有计时来自先前 Mac 实测。两批环境不同，不比较彼此延迟。

## 文件证据

各新项目 artifacts/results.json 保留分集与逐条预测；artifacts/checksums.json 校验已发布参数/结果。哈希用于检测改动，不是结果真实性的第三方签名。重新训练会改变产物，需重新构建 Demo 并运行测试。

## 必须能检查

|项目|训练隔离|对照|失败|可复现|
|---|---|---|---|---|
|TextGuard|规范化后去重再分集；词表仅训练；阈值仅验证；CV逐折fit|majority、NB、Logistic|每个测试预测，24个Logistic误判哈希；未知词人工复核|源包SHA、分集哈希、导出推断parity、参数JSON|
|CiteRAG|作者自建语料与问题，不声称独立测试；门槛固定|BM25、char、RRF|困难组逐条结果、无答案拒答失败|文档哈希、全部问题、排序规则、浏览器同算法|
|NoveltyLab|仅正常训练拟合StandardScaler/模型；正常验证阈值|centroid、IsolationForest、OneClassSVM|逐点分数、漏检、正常小样本限制|公开内置数据哈希、分集行号、导出中心与阈值|

TextGuard 的 NB 与 Logistic 参数/阈值选择不完全等价，不声称统一调优竞赛；概率未校准。Novelty 的测试迁移比例高，Precision 不外推真实业务。CiteRAG 引用ID只防伪造引用，不能证明答案被证据支持。

## 环境和后续

原始结果记录 scikit-learn 版本；requirements-ml.txt 固定 sklearn。numpy/scipy 范围可能在未来引起数值差异，精确本批版本记录在 environment-ml.json。大模型模块真实调用次数为0；契约测试的假响应不是模型评测。

源码核心变化与历史实测之间的关系必须保留；不得重新计算一个哈希然后把旧结果标成新代码重测。外部可用性、用户体验、真实费用、业务价值都未被验证。

## 发布内容

不提交SMS原文/zip、公司账号信息、内部链接、API密钥、虚构个人经历。可运行不等于生产级；作品多不等于与优秀人才水平等同。
