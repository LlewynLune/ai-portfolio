# SpecDecode-Lab｜greedy块验证与真实开销｜方法与可证伪范围

## 与原论文的区别

此项目只实现**确定性greedy推测解码**：draft逐token提出k个候选，target一次因果forward得到这些前缀对应的next-token logits；依次比较argmax，接受匹配，首个不匹配输出target token并丢弃后续draft；全部接受时可再加target bonus token。

不实现带概率接受率/残差重采样的distribution-preserving sampling，不声称任意采样温度下保持分布。原论文是参考机制，项目范围需明确。

## 精确性核心

causal mask保证批验证位置的logits不依赖其未来draft。首个不匹配后不使用错误上下文的后续logits。无KV cache、无dropout，greedy先后路径保持一致；仍需测试float numerics和tie情形，不声称跨硬件bitwise输出永远相同。

## 数据与模型

本项目重新训练target(d32、2heads)和draft(d16、2heads)，不是使用键值任务模型或外部LM。模8递推 $z_t=(z_{t-1}+z_{t-2})\bmod8$，64组初态48train/8validation/8test，序列后段可能重合，所以分集不用于泛化率宣称。监督所有prefix位置，target700steps、draft250steps。

4token prompt输出8token，test8个prompt，k2/k4各3次配对，先warmup，用perf_counter实际计时，包含draft和验证。保存每prompt耗时、calls和exact check；CPU tiny模型的dispatch/额外计算可能比baseline慢。

## 评价不能偷换

减少target forward次数不等于降低token级计算，也不一定低延迟。actual speed_ratio=baseline_ms/speculative_ms，低于1就是变慢，不能转换成“提升”。所有3次原始值保留，没有GPU throughput、并发负载或商业ROI。

相等是对齐target模型的生成路径，不是算术真值或文本质量。Demo原生执行两模型，可检查每块draft/target/accept；网页不重现后端计时，参考实测单列。

## 参考

https://arxiv.org/abs/2211.17192

## 运行证据

[全部表](artifacts/REPORT.md)、[JSON](artifacts/results.json)留存分集/预测/损失/环境。模型结果与train.py、frontier_support.py哈希绑定，哈希只检测改动不是第三方真实性签名。修改共享基座后需重训所有依赖，不把旧评测重新打hash作为新实验。
