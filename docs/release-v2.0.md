# v2.0 · Laminar-Lab related mechanism study

以 v1.9 为基线，原14研究模型/原报告与4业务事实不改。新增第15个独立项目 Laminar-Lab，而不是复制官方代码当本人既往项目。

官方来源公开核验：论文 arXiv:2510.12633v1；仓库 https://github.com/verl-project/laminar。只读参考固定 19333d00b8d794a145a07b6c082a1fa3cf84c42e。当前开源与论文 v1 机制细节有差异，README明确区分。

## 新增内容

- 独立 NumPy 13→24→4 MLP 的实际 autoregressive sampling、group-relative clipped token-ratio RL、reference KL、行为 logprob、梯度曲线、模型指纹。
- 异步 producer/learner、不可变 Relay、有限队列、消费/生成陈旧度、同版本组、SQLite partial/checkpoint/experience。
- 12探索＋12公平控制＋6去token延迟＝30次真实训练，每运行40次learner update，每次4梯度更新。不是30独立任务，不是自然语言大模型后训练。
- 300自写同版本双容量packing；100固定官方未改动pure planner合约。无GPU KV迁移或官方训练完整运行。
- 6真实强制子进程退出与恢复：prefix重算、同权重版本、dedup记录；非分布式exactly-once。
- 12个冻结模型×128新长度OOD探针，原长1/2/4/8，新长12/16；各模型共用探针，不是1536独立样本。真实分数和概率留存，不掩盖弱项。
- 学术正文 project.html、完整内联证据 evidence.html、主页新增行、研究总入口新增行、代码与复现文档。

## 边界与负结果

固定学习探针存在大量完全重合 prompt；旧字段heldout_*不能宣称独立留出。已保存逐运行overlap审计。长度OOD无完全重合，仍是同简单语法的后续探索。传统parser全正确，神经模型不是该任务必需。

异步更快不一定学得更好，取消token延迟后部分异步种子更差。wall time包含注入的I/O及每update 2ms，不是GPU throughput。保留首探索的worker倍率与无ratio损失记录缺陷，controlled单独修正，不回填历史结果。

公开大模型LoRA-RL、实际RDMA/UCX权重服务、GPU roofline profiling、真实KV迁移、完整训练故障恢复均未完成。
