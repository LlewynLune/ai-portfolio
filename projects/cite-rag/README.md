# CiteRAG｜可追溯检索问答与真实大模型接口

状态：本地检索/摘录已实测，真实 LLM HTTPS 调用模块已实现但未配置、未调用评测；不把测试桩或本地摘录当作大模型成果。

[Demo](demo.html) · [本地评测](artifacts/REPORT.md) · [全部结果](artifacts/results.json) · [完整性](artifacts/checksums.json) · [真实接口](llm_adapter.py)

## 已实现

- BM25 精确词项匹配、字符三元组余弦和 Reciprocal Rank Fusion。
- 检索排名下钻到证据ID；本地输出直接摘录首条证据，不做虚构生成。
- 固定启发式证据门槛，证据不足拒答；逐条报告无答案问题失败。
- 15 篇自建英文说明与 25 个问题，明确部分共享 FlowBench 样本，分 development/evaluation/challenge/unanswerable；不是标准数据集或独立外部验证。
- LLM 模块真实发送 OpenAI-compatible HTTPS chat/completions，一次上限、输出 token 上限、无自动重试；强制 JSON schema 和引用ID，保留实际 usage。

## 本地运行

```bash
python3 projects/cite-rag/app.py
python3 scripts/build_ai_demos.py
```

浏览器 Demo 自包含，无密钥，无后台，不上传输入。

## 真实 LLM：需本人配置

在个人终端/密钥管理中设置 LLM_BASE_URL、LLM_MODEL、LLM_API_KEY，**不要把值发进聊天、写入网页或 Git**。endpoint 必须 HTTPS，不在 URL 中嵌入凭证。

```bash
python3 projects/cite-rag/llm_adapter.py --query "retry transient bounded attempts" --execute-paid-call --output private/llm-result.json
```

运行前建立输出 private/ 目录，确定服务商价格和预算。一次调用上限与 token 上限不是精确金钱上限；目前没有价格表或真实费用结论。LLM 未配置时必须失败，不降级为“模拟成功”。引用ID存在不等于语义支持，真实答案还需人工核对。

## 测试和评测边界

测试中的假 transport 仅验证请求/响应契约、调用上限和拒绝伪引用；不作为真实 LLM 评测数据。当前 artifacts 的 llm_used 始终为 false。

混合召回对困难词汇可能有效，也可能把不相关文档拉上来。RRF 分数不是真实相关概率；拒答启发式会漏拒。保留不利结果和作者偏差，不要求满分。

## 贡献

用户提出需求与混合方案，代码和文档 AI 辅助完成，个人独立实现贡献待记录。大模型接口是本项目一个模块，不重复计为独立新项目；下一阶段经用户配置后才运行真实调用、冻结问题集、人评支持率和费用记录。
