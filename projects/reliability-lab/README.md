# FlowBench｜AI 工作流可靠性实验台

<!-- project-navigation:start -->
[Project Page](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/project.html) · [运行 Demo](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/demo.html) · [深化分析](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/depth-demo.html) · [作品集](https://llewynlune.github.io/ai-portfolio/index.html#experiments)
<!-- project-navigation:end -->





> 状态：本地可运行研究原型（0.2.0），AI 辅助搭建；支持合成 I/O 和实际本地 BM25 检索，不含真实 LLM。不是公司业务平台或生产上线成果。

面向正在搭建 Agent/AI 工作流的人，回答一个小而可验证的问题：**模型之外的执行框架，如何让暂时失败可恢复、永久错误可解释、提交副作用不重复？**

## 30 秒看成果

- [交互展示](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/demo.html)：离线查看参考实测、按策略/任务追踪事件、导出/导入 JSON。本机服务启动后可重新运行。
- [研究故事](RESEARCH_STORY.md)：成功率、重复副作用、参数公平性与检索泛化的四个问题。
- [v0.2 深化报告](results/advanced/REPORT.md)：本地检索、困难改写组、实际子进程崩溃恢复、并发与单次超时参数矩阵。
- [评测报告](results/reference/REPORT.md)：6 类负载、4 种策略、每种 5 次重复；原始事件完整保留。
- [汇总结果](results/reference/benchmark.json) 与 [完整性清单](results/reference/checksums.json)。
- [架构与决策](ARCHITECTURE.md) · [产品假设](PRODUCT.md) · [实验方法](EVALUATION.md) · [讲解与自验证](WALKTHROUGH.md) · [贡献与限制](CONTRIBUTIONS.md) · [方法依据](../../docs/reliability-benchmark-design.md)。

## 快速开始

Python 3.11+，仅标准库，无需 pip、GPU、模型密钥或数据库服务。在本项目目录运行：

```bash
python3 -m reliability_lab run --profile mixed --count 24 --policy resilient
python3 -m reliability_lab run --worker retrieval --profile clean --count 20
python3 -m reliability_lab deepen --output results/advanced-reproduced
python3 -m reliability_lab serve
```

服务仅监听本机环回地址，终端打印打开地址；按 Ctrl+C 关闭。不要用它直接对公网提供服务。

## 复现实验

```bash
python3 -m reliability_lab suite --output results/reproduced --repeats 5
```

同一 seed 固定故障清单，真实时间随机器负载变化。4 策略轮换顺序运行，避免总是让一个策略先运行；仍不能消除全部机器负载偏差。

## 跨进程恢复

```bash
python3 -m reliability_lab run --profile clean --count 8 --database results/local-state.sqlite3 --pause-after analyze
python3 -m reliability_lab run --profile clean --count 8 --database results/local-state.sqlite3
```

第一次在 analyze 后保存并暂停；第二次复用完成节点，只运行 validate 和 commit。数据库作用域绑定配置和版本，修改配置时需使用新 scope 或新数据库，不能复用不匹配输出。

## 测试

在作品集仓库根目录运行：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_portfolio.py
```

测试覆盖参数边界、固定故障清单、并发上限、重试、永久错误、输出拒绝、超时取消、预算、幂等冲突、持久化和跨进程重启。CI 已配置并完成首次远程运行，结果可在 [GitHub Actions](https://github.com/LlewynLune/ai-portfolio/actions) 复核。

## 实验配置

|字段|默认|含义|
|---|---:|---|
|count|24|工作流数，CLI 上限 200，交互上限 48|
|concurrency|4|整个 DAG 活跃工作流上限，非线程/进程数|
|seed|42|任务/节点固定故障和持续时间的散列种子|
|timeout_ms|70|单次尝试超时，no_timeout 策略除外|
|budget_ms|1000|提交起算的整体截止时间，包含排队|
|attempts|3|最多尝试次数（包含首次）|
|base_ms|12|正常节点合成等待基数|
|backoff_ms|8|指数退避基数，带固定种子抖动|

## 四种策略

- baseline：单次执行，超时即失败；仍使用同样并发和预算。
- retry：只对暂时错误/单次超时有限重试；应答丢失可能重复提交。
- resilient：同 retry，增加持久检查点和 SQLite 提交幂等。
- no_timeout：同 retry，但移除单次超时；仍有整个工作流预算，作为消融对照。

## 六类负载

clean / transient / mixed / ack_loss / permanent / slow。故障定义见 [config.py](reliability_lab/config.py)。每个原始 JSON 包含配置、故障哈希、事件序列、任务状态、成功与全部请求延迟、重试和提交次数。

## 不能据此声称

不是模型准确率评测、不是 RL 训练、不是生产集群、不是远程 exactly-once、没有 token 费用或业务收益；控制暂停不是主机断电证明。研究部分是方法比较与工程实验，不是发表论文或新算法。

你的个人贡献目前仅可明确为提出作品集需求、选定方向；代码和实验由 AI 辅助完成。独立讲解、修改、复核后才能补充本人承担的真实部分。

## 深化批次：研究与工程验证

新增81次真实本地异步负载实验，分故障/并发/种子比较策略；增加SQLite重开后暂停恢复和重复副作用核验。

[深化交互分析](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/depth-demo.html) · [新增实测报告](artifacts/depth/REPORT.md) · [新实验代码](depth.py) · [逐条新证据](artifacts/depth/results.json)

原模型和原报告保持冻结；本批结果只写artifacts/depth。所有参数扫描均为探索，不在测试上选择配置后声称独立评测；AI辅助实现与本人独立贡献分开。


<!-- investigation-link -->
## 本轮专项深入研究

真正进程退出发生在提交与检查点之间时，重启会重复副作用吗？

[Deep Investigation](https://llewynlune.github.io/ai-portfolio/projects/reliability-lab/deep-study.html) · [全部实测条件](artifacts/investigation/REPORT.md) · [结果讨论与未完成项](artifacts/investigation/DISCUSSION.md) · [原始证据](artifacts/investigation/results.json)

18次真实进程退出恢复：retry重复副作用6次，resilient 0次；仅局部SQLite边界。

原模型、旧Depth和CiteRAG记忆证据保持冻结。新调查按各自协议区分训练、推断、合成仿真和历史再分析，不能以记录数证明泛化。
