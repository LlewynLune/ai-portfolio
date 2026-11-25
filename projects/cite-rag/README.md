# CiteRAG｜可追溯检索问答与真实大模型接口

<!-- project-navigation:start -->
[Project Page](https://llewynlune.github.io/ai-portfolio/projects/cite-rag/project.html) · [运行 Demo](https://llewynlune.github.io/ai-portfolio/projects/cite-rag/demo.html) · [深化分析](https://llewynlune.github.io/ai-portfolio/projects/cite-rag/depth-demo.html) · [作品集](https://llewynlune.github.io/ai-portfolio/index.html#experiments)
<!-- project-navigation:end -->





状态：原检索与摘录实验保持冻结；新增 **Source-backed Agent Memory** 已真实运行本地公开量化大模型，保存521次实际调用（512问答、6记忆整理、3预热）。远程付费LLM接口未调用。相同问题的策略/挑战/回归不是独立样本。

## 本轮代表作：来源可校验的 Agent 记忆

版本、撤销、冲突、namespace、token预算与独立校验；真实本地模型、受控记忆污染挑战、预算消融、传统强基线、v2修复回归。模型记忆与回放在原主实验同分，传统规则基线更强；不包装为通用Agent满分。

[项目说明](project.html) · [真实证据浏览器](memory-demo.html) · [方法与公开前沿来源](MEMORY_METHOD.md) · [真实实验全报告](artifacts/memory/REPORT.md) · [本地运行](LOCAL_LLM.md) · [记忆模块源码](memory_agent/core.py) · [核心测试](../../tests/test_memory_agent.py)


[Demo](https://llewynlune.github.io/ai-portfolio/projects/cite-rag/demo.html) · [本地评测](artifacts/REPORT.md) · [全部结果](artifacts/results.json) · [完整性](artifacts/checksums.json) · [真实接口](llm_adapter.py)

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

测试中的假 transport 仅验证旧HTTPS接口契约，不作为真实 LLM 评测。历史 artifacts/results.json 与 artifacts/depth 仍为 llm_used=false；新 artifacts/memory 含真实本地模型调用，逐条llm_used=true。

混合召回对困难词汇可能有效，也可能把不相关文档拉上来。RRF 分数不是真实相关概率；拒答启发式会漏拒。保留不利结果和作者偏差，不要求满分。

## 贡献

用户提出需求与混合方案，代码和文档 AI 辅助完成，个人独立实现贡献待记录。大模型接口是本项目一个模块，不重复计为独立新项目；下一阶段经用户配置后才运行真实调用、冻结问题集、人评支持率和费用记录。

## 深化批次：研究与工程验证

新增内容指纹去重的RRF检索模块，在重复文档与无关文档注入下对照排名、拒答和可追踪摘录。

[深化交互分析](https://llewynlune.github.io/ai-portfolio/projects/cite-rag/depth-demo.html) · [新增实测报告](artifacts/depth/REPORT.md) · [新实验代码](depth.py) · [逐条新证据](artifacts/depth/results.json)

原模型和原报告保持冻结；本批结果只写artifacts/depth。所有参数扫描均为探索，不在测试上选择配置后声称独立评测；AI辅助实现与本人独立贡献分开。


<!-- investigation-link -->
## 本轮专项深入研究

在此前未出现的源ID、团队与措辞上，v2来源校验仍能处理修订、冲突和计算吗？

[Deep Investigation](https://llewynlune.github.io/ai-portfolio/projects/cite-rag/deep-study.html) · [全部实测条件](artifacts/investigation/REPORT.md) · [结果讨论与未完成项](artifacts/investigation/DISCUSSION.md) · [原始证据](artifacts/investigation/results.json)

source_rag：严格通过28/48，解析失败11；最终拒答可能被guard纠正，不等于原始生成正确。

原模型、旧Depth和CiteRAG记忆证据保持冻结。新调查按各自协议区分训练、推断、合成仿真和历史再分析，不能以记录数证明泛化。
