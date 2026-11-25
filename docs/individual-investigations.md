# 每个项目深入到具体研究问题

本轮14研究工程项目全部完成一项专项调查，4业务案例深化产品取舍与建议验收。不是新项目数量或统一准确率。

|项目|本轮研究问题|完整条件|阅读入口|
|---|---|---:|---|
|channel-est|观测数量够了是否就可可靠估计？导频几何和错误四径假设带来什么风险？|18|[深研页](../projects/channel-est/deep-study.html) / [实测报告](../projects/channel-est/artifacts/investigation/REPORT.md) / [讨论](../projects/channel-est/artifacts/investigation/DISCUSSION.md)|
|circuit-id|观察窗短于时间常数时，低残差为何仍可能给出不可靠RC参数？|36|[深研页](../projects/circuit-id/deep-study.html) / [实测报告](../projects/circuit-id/artifacts/investigation/REPORT.md) / [讨论](../projects/circuit-id/artifacts/investigation/DISCUSSION.md)|
|cite-rag|在此前未出现的源ID、团队与措辞上，v2来源校验仍能处理修订、冲突和计算吗？|2|[深研页](../projects/cite-rag/deep-study.html) / [实测报告](../projects/cite-rag/artifacts/investigation/REPORT.md) / [讨论](../projects/cite-rag/artifacts/investigation/DISCUSSION.md)|
|dpo-lab|偏好目标和单token正确率如何随真实训练变化，而非只做权重插值？|9|[深研页](../projects/dpo-lab/deep-study.html) / [实测报告](../projects/dpo-lab/artifacts/investigation/REPORT.md) / [讨论](../projects/dpo-lab/artifacts/investigation/DISCUSSION.md)|
|lora-lab|适配收益究竟来自query、value还是输出头？哪些组合破坏旧任务？|24|[深研页](../projects/lora-lab/deep-study.html) / [实测报告](../projects/lora-lab/artifacts/investigation/REPORT.md) / [讨论](../projects/lora-lab/artifacts/investigation/DISCUSSION.md)|
|moe-lab|同一批输入仅改变排队顺序，哪些样本会持续被丢弃？|84|[深研页](../projects/moe-lab/deep-study.html) / [实测报告](../projects/moe-lab/artifacts/investigation/REPORT.md) / [讨论](../projects/moe-lab/artifacts/investigation/DISCUSSION.md)|
|novelty-lab|忽略特征相关性的中心距离，和只在正常训练拟合的协方差基线有什么差异？|3|[深研页](../projects/novelty-lab/deep-study.html) / [实测报告](../projects/novelty-lab/artifacts/investigation/REPORT.md) / [讨论](../projects/novelty-lab/artifacts/investigation/DISCUSSION.md)|
|power-scope|只用过去误差在线更新区间，冷却漂移下能否恢复覆盖，而代价多大？|4|[深研页](../projects/power-scope/deep-study.html) / [实测报告](../projects/power-scope/artifacts/investigation/REPORT.md) / [讨论](../projects/power-scope/artifacts/investigation/DISCUSSION.md)|
|reliability-lab|真正进程退出发生在提交与检查点之间时，重启会重复副作用吗？|54|[深研页](../projects/reliability-lab/deep-study.html) / [实测报告](../projects/reliability-lab/artifacts/investigation/REPORT.md) / [讨论](../projects/reliability-lab/artifacts/investigation/DISCUSSION.md)|
|spec-decode|greedy一致性之外，随机草稿接受/修正能否保持目标token分布？|16|[深研页](../projects/spec-decode/deep-study.html) / [实测报告](../projects/spec-decode/artifacts/investigation/REPORT.md) / [讨论](../projects/spec-decode/artifacts/investigation/DISCUSSION.md)|
|textguard|低发生率部署下，旧测试准确率是否掩盖精确率失效？|30|[深研页](../projects/textguard/deep-study.html) / [实测报告](../projects/textguard/artifacts/investigation/REPORT.md) / [讨论](../projects/textguard/artifacts/investigation/DISCUSSION.md)|
|tiny-attention|改变被查询值和无关值，模型是否只对真正相关的信息做出响应？|6|[深研页](../projects/tiny-attention/deep-study.html) / [实测报告](../projects/tiny-attention/artifacts/investigation/REPORT.md) / [讨论](../projects/tiny-attention/artifacts/investigation/DISCUSSION.md)|
|video-guard|未来窗口是否改变已经发出的报警？少量观测窗口丢失会损害及时检测吗？|36|[深研页](../projects/video-guard/deep-study.html) / [实测报告](../projects/video-guard/artifacts/investigation/REPORT.md) / [讨论](../projects/video-guard/artifacts/investigation/DISCUSSION.md)|
|vision-cal|不在测试上挑置信门槛，预测集合在干净和迁移图像上还能覆盖真值吗？|9|[深研页](../projects/vision-cal/deep-study.html) / [实测报告](../projects/vision-cal/artifacts/investigation/REPORT.md) / [讨论](../projects/vision-cal/artifacts/investigation/DISCUSSION.md)|

## 关键深化而非数据规模

- DPO：3种子×SFT与两beta，9次真实NumPy输出头训练；基座冻结。梯度独立有限差分测试，训练/验证/测试由新合成前缀划分。
- SpecDecode：16上下文每个1000抽样，解析接受＋修正分布恒等式验证；另64四token轨迹。不宣称多token并行或加速。
- FlowBench：18次真实子进程退出，加36受控异步期限负载运行；不是生产事故或LLM实验。
- CiteRAG：8新namespace48题，两策略96问答＋1预热。旧521调用单独保留；累计618真实本地调用仍来自有限已知设置语法。

## 4业务案例

业务深化说明已有产品取舍、建议指标定义、建议验收和原始证据缺口，不新增未经提供的实现或历史指标。
- [AI 审图平台](../business-cases/drawing-review/case.html) / [产品分析](../business-cases/drawing-review/PRODUCT_ANALYSIS.md)。
- [标准化线上平台](../business-cases/standards-platform/case.html) / [产品分析](../business-cases/standards-platform/PRODUCT_ANALYSIS.md)。
- [团队智能体技能空间与知识库](../business-cases/skills-knowledge/case.html) / [产品分析](../business-cases/skills-knowledge/PRODUCT_ANALYSIS.md)。
- [火山引擎 FORCE 大会宣传片](../business-cases/force-aigc/case.html) / [产品分析](../business-cases/force-aigc/PRODUCT_ANALYSIS.md)。

## 验证与复现

在独立仓库副本运行 scripts/run_investigations.py，模型只在CiteRAG需要。原输出目录已存在时拒绝覆盖；不要删除历史证据替换为更好结果。核心依赖requirements-depth.txt，本地LLM依赖requirements-local-llm.txt。

新专项测试 tests/test_investigations.py 检查：冻结hash、独立DPO梯度、隐藏状态导出、采样恒等式、容量、真实崩溃、prequential无当前真值泄漏、流式前缀与新题隔离。测试通过不代表模型泛化或履历真实性。

## 仍未做的工作

各项目的Next Uncompleted Work已逐项明确。没有自然视频/真实设备/真人偏好/多日Agent/生产收益；不自动训练更大模型或宣称SOTA。
