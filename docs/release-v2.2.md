# v2.2 · Live asynchronous RL recovery

不是新增项目数量：专攻Laminar-Lab的未完成工程链路。原model.py、experiment.py、planes.py与旧输出字节不改；主页视觉、4业务事实和个人写作补充保持。

## 实际实现

- 同一单机coordinator并发4个token-level producer和1个learner，真实自回归MLP推断及Adam梯度训练。
- SQLite逐token保存actions、logprobs、RNG、policy version；每组4个回答使用同一不可变策略快照。
- Pending batch保存真实FIFO完成顺序与base版本；策略、Adam first/second moments与step、唯一消费记录在一个事务提交。
- 整个coordinator真实os._exit四类故障：partial token、commit之前、commit中、commit后，重启继续处理真实prefix和pending batch。
- 主矩阵20链：3seed×5故障/无故障，另容量6/12/32与staleness不限/2对照。12真实退出。
- 边界回归4链、4额外退出，直接在退出后/重启前读取实际SQLite。24链16退出，480个learner updates（每更新4Adam steps）本机全部精确逐步重放。
- 完整工作库存和唯一消费，奖励独立函数复算；2983个已存RNG状态独立重建核验；5类offline tamper probes。Hash链不是签名。
- 24个分运行自包含浏览页、Live Study索引、全模型/优化器快照、prefix/RNG、事件/session和hash证据。

## 重要观察与限制

1. 容量6=一batch，消除陈旧度的同时接近同步，无免费吞吐结论。单配置一次调度，不做稳定速度排序。
2. 同一seed的fault/no-fault最后分数可以不同：异步调度完成顺序不同，不能宣称恢复后相同最终模型，只核验实际已提交路径的模型与Adam数值。
3. 仍是有限符号MLP的真实RL，不是语言大模型LoRA微调；固定probe有已知prompt overlap，不称独立泛化。
4. 单机整coordinator恢复不是worker机器恢复、分布式exactly-once或生产可靠性承诺。
5. Hash链证明完整性线索，不证明可信作者、独立审计主体或有效业务reward。
6. 本机精确replay与跨平台容差检查分开；BLAS浮点实现可能不同，不用hash假设Linux==Mac。
7. 保留上一版30实训、9确定序恢复等，不混计为独立任务。

公开研究来源沿用项目README已核验Laminar论文/官方仓库；本轮没有复制任何公司资料、图纸或内部代码。
