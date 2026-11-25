# LoRA-Lab · 层级增量全因子消融

适配收益究竟来自query、value还是输出头？哪些组合破坏旧任务？

## 预声明实验协议

{
  "kind": "layer_factorial_ablation",
  "layers": [
    "q",
    "v",
    "head"
  ],
  "all_8_subsets": true,
  "seeds": [
    192001,
    192002,
    192003
  ],
  "n_per_seed": 128,
  "no_retraining": true
}

## 全部条件结果

|subset|seed|n|old_accuracy|new_accuracy|
|---|---|---|---|---|
|base|192001|128|0.46875|0.078125|
|base|192002|128|0.5|0.046875|
|base|192003|128|0.46094|0.046875|
|head|192001|128|0.40625|0.17188|
|head|192002|128|0.36719|0.17188|
|head|192003|128|0.4375|0.16406|
|v|192001|128|0.375|0.17969|
|v|192002|128|0.40625|0.10938|
|v|192003|128|0.32812|0.21875|
|v+head|192001|128|0.25781|0.28906|
|v+head|192002|128|0.23438|0.25|
|v+head|192003|128|0.26562|0.32812|
|q|192001|128|0.10156|0.085938|
|q|192002|128|0.16406|0.085938|
|q|192003|128|0.13281|0.16406|
|q+head|192001|128|0.1875|0.21875|
|q+head|192002|128|0.20312|0.25|
|q+head|192003|128|0.21875|0.35156|
|q+v|192001|128|0.14844|0.11719|
|q+v|192002|128|0.19531|0.09375|
|q+v|192003|128|0.17969|0.17188|
|q+v+head|192001|128|0.09375|0.41406|
|q+v+head|192002|128|0.125|0.35938|
|q+v+head|192003|128|0.17188|0.42969|

## 发现、失败与适用边界

- 8种层组合全部报告，不在测试上选最佳子集。
- 低秩奇异值解释参数增量的有效秩，不证明通用语义结构。
- 从已训练adapter屏蔽层，不等于独立训练每个结构，因果范围限冻结权重干预。

## 原始证据与复现

[全部逐条记录](results.json) · [预声明协议](protocol.json)

从仓库根目录运行 python3 scripts/run_investigations.py --project lora-lab。输出拒绝覆盖已有artifacts/investigation；复现时先在独立仓库副本运行，不能删除原结果来替换。

AI-assisted local investigation. Data/model/experiment limitations in per-project protocol. Not production, independent publication, hardware measurements or fully personal independent development.
