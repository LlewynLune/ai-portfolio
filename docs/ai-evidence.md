# 实验与真实性清单

## 当前事实

四个项目，不把模型对照/模块拆成独立项目。所有为 AI 辅助的学习研究实现，未验证本人独立研发能力、论文贡献或生产上线。

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
