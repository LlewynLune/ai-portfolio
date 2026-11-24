# CiteRAG 本地检索评测

15 篇自建文档、25 个问题；共享 FlowBench 样本来源明确披露。大模型未调用。

|方法|集合|问题|Recall@3|MRR@3|拒答正确率|
|---|---|---:|---:|---:|---:|
|bm25|development|6|1.000|1.000|—|
|bm25|evaluation|13|1.000|1.000|—|
|bm25|challenge|4|0.500|0.750|—|
|bm25|unanswerable|2|—|—|0.500|
|char|development|6|1.000|1.000|—|
|char|evaluation|13|1.000|1.000|—|
|char|challenge|4|0.625|0.458|—|
|char|unanswerable|2|—|—|1.000|
|hybrid|development|6|1.000|1.000|—|
|hybrid|evaluation|13|1.000|1.000|—|
|hybrid|challenge|4|0.750|0.750|—|
|hybrid|unanswerable|2|—|—|0.500|

固定拒答门槛是启发式，会失败；所有病例逐条保留，引用有效不等于答案语义正确。
[全部结果](results.json) · [完整性](checksums.json)
