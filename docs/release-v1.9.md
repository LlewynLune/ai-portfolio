# v1.9｜逐项目研究与工程深化

## 实际完成

14研究项目全部新增独立专项调查与证据页，4真实业务案例深化产品取舍、建议指标口径、验收方案和证据缺口。未新增项目数量、职位、日期、业务收益或内部实现；profile/resume.json不变。

完整入口：project-investigations.html。每研究项目有 deep-study.html、artifacts/investigation/{protocol.json,results.json,REPORT.md,DISCUSSION.md}。全部旧Depth、model.json、原始报告保留。

## 关键工程增量

- DPO：3种子×SFT/两beta，9次真实NumPy输出头训练；独立梯度有限差分和隐藏状态导出一致性；新训练/验证/测试在种子内及原split中无重叠。跨种子不声称完全独立。
- TinyAttention：相关/无关值直接输入干预；旧微型模型仍有无关敏感失败，不拿attention热图当因果解释。
- LoRA：q/v/head全部8组合消融，逐层奇异值；这是冻结adapter屏蔽，不是每组合单独训练。
- SpecDecode：16上下文×1000真实随机接受/修正抽样，分布恒等式与64条四token采样；不是多token并行或提速评测。
- MoE：3批×6排列、容量与drop/second，公开每样本是否始终被丢弃，不只看接收项误差。
- CircuitID：观察窗/时间常数/噪声的profile拟合；profile宽度是启发式，不是电气容差。
- ChannelEst：导频几何、秩/条件数与实际2/4/8tap失配；理想频域仿真，无设备。
- PowerScope：严格先预测后更新，仅过去残差更新区间，不改善点预测或给IID保证。
- VideoGuard：历史轨迹每个前缀检查已发报警不依赖未来，观察窗口丢失固定检测；无自然视频新标注。
- FlowBench：18真实子进程急停恢复＋36局部异步期限负载运行。SQLite边界幂等，不是分布式exactly-once。
- TextGuard：旧预测在5目标先验假设下重加权和概率odds校正，非真实用户新测试。
- Novelty：正常训练35条收缩协方差强基线，验证12条定阈值，校准规模不足公开。
- VisionCal：验证集分位数预测集合；校准标签与旧温度调优共用，因此不能宣称严格split-conformal覆盖保证。
- CiteRAG：8新namespace/48新问题，96真实生成＋1预热；旧521与新97分开，累计618实际模型调用。有限Setting语法仍适合传统解析，未做通用NLI。

## 验收

160tests通过，10对应依赖缺失跳过。17本轮专项测试含14证据包/网页一致、梯度、采样、容量、崩溃、时间泄漏与因果性质。38原始模型/结果/报告与HEAD逐字一致。完整原文hash/实现hash与DPO划分审计保留。

14深研页、4产品页在390px iframe逐项无溢出；分页大小、下一页、关键词筛选真实操作验证，无JS错误。界面不是完整LLM运行器，也不是视觉满分保证。

## 尚未完成

每项Next Uncompleted Work明确下一阶段，通常需独立自然数据、人工标注、真实设备或更多模型。未做SOTA、论文、生产服务、业务收益和真人能力验证。GitHub推送与Actions/Pages部署以远端实际状态核验，不由文件存在推定。

## 复现与公开

运行 scripts/run_investigations.py；旧输出存在时拒绝覆盖，复现用独立副本。权重、SQLite/private与临时密钥不进Git。仅公开合成/公开研究数据及代码；原业务素材不公开。新增页面读本地内联证据，不访问模型API或电气设备。
