# 证据轨迹可回放示例

状态：可运行的确定性入门示例。它不是 AI 模型，也不是已完成的商业项目；作用是先建立“输入事件 → 证据检查 → 人工复核 → 可回放摘要”的基本工程习惯。

## 运行

在仓库根目录执行：

```bash
python3 examples/evidence-trace/evidence_trace.py examples/evidence-trace/sample-events.jsonl
```

输出到文件：

```bash
python3 examples/evidence-trace/evidence_trace.py examples/evidence-trace/sample-events.jsonl -o examples/evidence-trace/trace-summary.txt
```

## 输入格式

每行一个 JSON 对象，必须包含：

- case_id：同一文件只能有一个案例 ID。
- title：案例标题。
- actor：human、rule、system 或 model。
- status：当前状态。
- evidence：非空数组，记录可复核证据。
- note：可选说明。

## 示例证明了什么

- 每个步骤都有责任主体和证据。
- 最终状态需要人工 reviewed。
- 全部过程可以重新运行并生成摘要。
- 没有最终人工复核时，脚本会给出警告。

## 它还不能证明什么

- 不能证明 AI 回答准确。
- 不能证明模型性能、成本或可靠性。
- 不能替代真实用户访谈、对照实验或生产环境监控。

后续可以把 model 事件接入真实公开数据与评测，但必须保留数据来源、基线、失败样本和个人贡献说明。
