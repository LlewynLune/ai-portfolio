# Laminar-Lab · Trajectory-Level Async RL Mechanisms

个人 AI 辅助研究与工程项目；**不是 Laminar 官方实现的作者或贡献者，不是字节生产项目，不是完整 CUDA/Ray 集群复现**。

本项目围绕一个问题展开：rollout 不等 learner 时，怎样保持轨迹版本、测量陈旧度并避免把系统吞吐误当学习效果？

## 已经实际做了什么

- NumPy 13→24→4 条件自回归 MLP，先监督学习 copy，再用 sampled reward 学习 symbol shift；不是 Transformer 或公开大语言模型微调。
- 独立 asyncio producer/learner loops，4 个 worker、有限 FIFO 队列、不可变权重 Relay、同一 prompt 四回答组成同版本组。
- token-level clipped GRPO-like surrogate、group-relative advantage、精确 categorical reference KL；保存实际 behavior logprob、每轮梯度、ratio、clip 与权重指纹。
- 同步、异步 ratio、异步无 ratio、显式 staleness≤2 四组，3 种子×40 learner updates；公平延迟修正版为 artifacts/controlled，首轮探索保存在 artifacts/runs，不删除不利结果。
- 300 个自写同版本双容量 packing 场景；直接加载 **未改动官方纯 planner** 跑了 100 个合约场景。只执行这段 CPU 纯函数，不声称跑了官方 trainer 或完整 test suite。
- 6 个真实子进程强制退出与重启测试，检查冻结版本、已存 prefix、完整轨迹、SQLite 去重。prefix 重新计算，不是 KV-cache 恢复。
- 10 项初始单元合约含有限差分梯度检查；全部训练与事件 JSON 可回读复算。
- 另6次取消 token sleep 的真实训练，保留每更新2ms控制开销；异步部分种子更差，不能把速度当质量。
- 12个冻结模型 ×128个长度12/16 OOD探针，训练长度上限8，确无完全相同训练prompt。追加探针仍是已见合成语法，不是通用语言盲测。

## 本轮继续深化

- **学习器原子恢复**：3种子×3故障阶段，共9个真实强制退出的学习进程。快照和消费账本在SQLite同一事务提交；提交前/事务内/提交后恢复到与未中断基线一致的模型指纹、12更新和72组唯一消费。采用确定顺序批次，不是实时异步worker恢复，不作分布式exactly-once保证。
- **同样本配对重放**：3种子×ratio/no_ratio两路重新优化，使用完全相同冻结轨迹、behavior logprob与顺序；ratio精确重构旧结果。no_ratio并非总是更差：seed41固定探针更高。这是离线损失机制消融，不是在线同分布随机对照。
- 新证据：artifacts/system/durable-learner.json、artifacts/paired-replay.json。新源码：laminar_lab/durable.py、paired.py。

运行：python -m laminar_lab.durable --output artifacts/my-recovery；python -m laminar_lab.paired（默认immutable输出，已有结果不会覆盖）。原30次训练证据保持，不把恢复/重放记录并成独立任务样本。

## v2.3：本地 Qwen LoRA 与奖励饱和

[Qwen 实验与逐批证据](qwen-study.html) · [方法、反例与复现](QWEN_STUDY.md)。在固定公开 4B 量化基座上做真实 LoRA 强化学习：原始二选一策略几乎只选 A；用训练输入做中心化后，奖励有区分度的组从 5/576 增至 545/576，但留出表现仍随种子变化，且出现全选 B。采样、奖励、版本和评分已独立复算；校准版六个适配器已在本机重载检查。Qwen 部分是单 GPU、单 token 奖励和显式版本滞后，**没有接入下方实时异步故障恢复链路**。

## v2.2：实时异步训练与持久化恢复

本轮将“实时异步”与“恢复”接入同一真实运行coordinator，而不是确定顺序的独立恢复玩具。新增代码live.py、live_audit.py、run_live.py、crash_boundaries.py、verify_rng.py、portable_replay.py；原experiment.py、model.py、planes.py及旧证据不修改。

- 4个producer逐token自回归采样，每token保存prefix、行为logprob、RNG状态和固定policy版本；失败恢复从已存RNG继续生成，不重算prefix token。
- Learner从完成FIFO组取batch；保留pending batch及其base版本；真实Adam更新，参数、first/second moments、step和消费账本一次事务提交。
- 主矩阵20组运行，12次真实整个coordinator进程退出；边界回归4组、4次额外退出，保存退出后且重启前的SQLite快照。总共24运行链、16次退出，不是独立任务样本。
- 每链20个learner版本、每更新四Adam步；480次提交更新全部在本机逐步精确重放，行为logprob与reward独立复算，2983个已存RNG状态检查。跨平台CI用1e-9级数值容差，不声称跨BLAS浮点hash相同。
- 每链120组消费、未完成/丢弃/已消费全量守恒，未发现重复消费。奖励manifest与5种篡改探针（reward、logprob、version、event hash、Adam step）保留；hash链只是篡改痕迹，不是签名或第三方证明。
- 容量6/12/32与不限/最大2陈旧度对照：容量6等于一batch使异步接近同步，不能把低陈旧度当免费吞吐收益。单条件单次调度，不能做稳定速度或质量排名。

[Live Study与24个独立证据浏览页](live-study.html)。每个证据页内联原JSON，离线可读；索引不一次加载全部32MB证据。这里的“独立”指各文件可单独打开，不指统计独立样本。

运行：python -m laminar_lab.run_live --output artifacts/my-live-run。既有路径拒绝覆盖。命令创建临时SQLite、实际执行训练/强制退出/重启，再导出JSON；不执行设备控制，不使用付费API或公司数据。

### 恢复的边界

实测是单机整coordinator进程中断恢复，不是多机worker fault、Ray恢复或分布式exactly-once。调度顺序在重启后可能改变，**不宣称与未中断基线相同最终模型**；只能声称恢复后的每次已提交更新可以从真实消费样本和保存优化器状态复算。Toy MLP不是语言大模型，未接入LoRA-RL；KV迁移、RDMA、UCX与集群吞吐未完成。初始固定probe存在已披露prompt overlap，不能包装成能力泛化。

## 最重要的负结果与边界

三个种子的学习结果并不一致；更快的异步时间线没有稳定地达到更高任务分数。staleness 上限是额外消融，不是 Laminar 论文原始设计的必须配置。token ratio clipping 不是无偏的 full-trajectory importance sampling，更不是 V-trace。

学习探针用不同 RNG seed，但有限字母语法出现大量完全相同 prompt；artifacts/audit.json 逐运行记录 overlap。因此旧字段名 heldout_* 实際应读作**固定学习探针**，不能宣称独立留出泛化。四符号 shift 的确定性 parser 100% 是强基线，此任务不需要神经模型；它仅适合检验训练与系统机制。

每 token 的 asyncio sleep 是透明注入的 I/O/环境延迟，wall time 包含这些延迟与 Python 调度；不外推真实 GPU 吞吐、RDMA、KV migration 或 Laminar 论文的加速倍数。主训练按完整 prompt group 入队；比分散逐 trajectory 的官方 admission 粒度更粗。

## 运行

隔离 Python 3.11+ 环境安装 NumPy；在本目录执行：

```bash
python -m venv .venv
.venv/bin/python -m pip install 'numpy>=2.0,<3'
.venv/bin/python -m laminar_lab.experiment --output artifacts/my-run --updates 40
.venv/bin/python -m laminar_lab.recovery --output artifacts/my-system
.venv/bin/python -m laminar_lab.study --output artifacts/my-system --audit artifacts
```

最后一条默认校验已冻结 controlled 证据；若要直接执行官方纯 planner，另外 clone 官方仓库并 checkout 固定 revision，然后加 --upstream PATH。不会安装官方 CUDA 依赖。

## 项目文件

- project.html：方法、全种子对照、负结果和系统边界。
- evidence.html：逐运行、逐 learner update、group/trajectory、原始事件浏览器；导出当前证据，静态页面不训练。
- laminar_lab/model.py：真实训练与 token-ratio surrogate。
- laminar_lab/experiment.py：实际异步调度与权重固定。
- laminar_lab/planes.py：Relay、partial/experience/checkpoint SQLite、packing。
- laminar_lab/recovery.py：真实 os._exit 与恢复。
- laminar_lab/study.py：packing stress、官方 planner 合约与证据审计。
- artifacts/controlled：正式透明控制批次；artifacts/runs：探索批次。
- artifacts/audit.json：指纹、计数、score 复算及 prompt overlap。
- artifacts/system：packing、upstream contracts、进程恢复。

## 公开研究依据及版本差异

1. [Laminar 论文 v1](https://arxiv.org/html/2510.12633v1) 与 [arXiv元信息](https://arxiv.org/abs/2510.12633)：轨迹级异步、Relay、同版本重打包、inherent staleness，2025论文。
2. [官方公开实现](https://github.com/verl-project/laminar)，实际核验固定 revision **19333d00b8d794a145a07b6c082a1fa3cf84c42e**。README明确称论文开源实现。当前源码并非论文 v1 的逐行重现。
3. 官方 src/laminar/multi_version_rollout/repack.py 当前纯 planner 按 stale version、source/destination KV阈值与active runtime过滤；并非直接使用论文的 ramp-down＋roofline请求数双约束。本项目把两者分别执行与记录，不偷换为相同算法。
4. 官方 README还支持 mixed-version partial rollout 与 long-horizon SWE recipe；本项目只做 version-consistent toy机制，不调用工具沙箱、不执行外部Agent任务，不沿用官方SWE分数。

未把内部文档、图、代码、人员资料或未授权训练数据放入公开仓库。AI辅助实现不等于本人已经独立掌握所有算法与系统代码。
