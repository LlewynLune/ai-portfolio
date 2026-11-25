# CiteRAG · 新namespace与乱序修订迁移

在此前未出现的源ID、团队与措辞上，v2来源校验仍能处理修订、冲突和计算吗？

## 预声明实验协议

{
  "kind": "fresh_namespace_transfer_after_v2",
  "namespaces": 8,
  "queries_per_namespace": 6,
  "modes": [
    "source_rag",
    "release_v2"
  ],
  "budget": 800,
  "source_order": "current revision first, older event arrives last",
  "new_source_ids": true,
  "grammar": "same explicit Setting grammar, not independent natural-language validation",
  "not_tuning_after_results": true
}

## 全部条件结果

|mode|n|correct|parse_failures|wrong_answers|mean_prompt_tokens|
|---|---|---|---|---|---|
|source_rag|48|28|11|0|836.83|
|release_v2|48|48|2|0|942.46|

## 发现、失败与适用边界

- 数据在首次本批推断前写入dataset.json；48新问题实例/8namespace不与原48题重合。
- 仍使用同一已知Setting语法；语言模板变化与新ID不是通用语义泛化。
- source_rag保留v1严格字符串契约，release含整数适配与guard；差异为整系统而非单组件收益。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project cite-rag。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
