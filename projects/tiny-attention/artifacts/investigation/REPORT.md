# TinyAttention · 相关与无关信息的因果干预

改变被查询值和无关值，模型是否只对真正相关的信息做出响应？

## 预声明实验协议

{
  "kind": "causal_counterfactual_interventions",
  "seeds": [
    191001,
    191002,
    191003
  ],
  "pairs": 3,
  "n_per_seed": 128,
  "interventions": [
    "query_value_change",
    "irrelevant_value_change"
  ],
  "excludes_original_split_ids": true
}

## 全部条件结果

|seed|intervention|n|baseline_accuracy|intervened_accuracy|output_flip|mean_kl|
|---|---|---|---|---|---|---|
|191001|query_value_change|128|0.40625|0.42969|0.60156|1.4927|
|191001|irrelevant_value_change|128|0.40625|0.41406|0.625|1.4321|
|191002|query_value_change|128|0.35938|0.42969|0.5625|1.4068|
|191002|irrelevant_value_change|128|0.35938|0.35938|0.59375|1.4082|
|191003|query_value_change|128|0.45312|0.47656|0.69531|1.5406|
|191003|irrelevant_value_change|128|0.45312|0.4375|0.625|1.426|

## 发现、失败与适用边界

- 直接修改输入值、按生成规则重算真值，是受控任务干预，不把attention权重当因果解释。
- 新前缀排除原训练/验证/测试ID；共享语法不等于自然语言泛化。
- 输出翻转不总是错误：相关值改变应翻转，无关值改变不应翻转。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project tiny-attention。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
