# 公开研究地图：为什么专精音画事件同步

检索基准：2026-11-24。**仅保留公开可复查来源**。内部检索用于找线索，不将内部链接、GTM材料、业务指标、员工身份和私有模型参数发布到仓库。未把个人项目称为官方成果，也不将检索到的营销能力当作独立评测结论。

## 1. 字节创新与视频多模态：确认的入口

### Seedance 2.5：多参考与时间戳控制

官方发布材料描述30秒单次音视频生成、多轮延长、最多30图/10视频/10音频参考与时间戳级编辑，同时明确复杂运动物理合理性和多主体互动仍有提升空间。来源：[官方发布](https://research.doubao.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)。

本项目借鉴的是“把时间控制变成可检验条件”，**未调用Seedance，也没有生成模型**。目前只检验闪光/敲击事件延时，无法验证官方整个能力体系。

### VEBench：从看懂视频到精确编辑操作

公开论文作者列表包含ByteDance Intelligent Creation与UCF；定义剪辑技术识别和素材选择/时间定位两个任务。论文报告3.9K视频、257小时、3080人工核验QA，覆盖7种剪辑技术，强调真实编辑中的多视频和时序推理困难。来源：[论文](https://arxiv.org/html/2605.03276)。

这不等同于另一项目VE-Bench。本仓库未使用VEBench数据，未运行其评测。借鉴“选对对象”和“定位正确”要分开评估的思想，不把事件相关性当作语义剪辑能力。

### LatentSync：音频条件唇形生成

公开仓库介绍音频条件潜在扩散、Whisper音频表示、U-Net cross-attention及SyncNet等监督，并强调评估数据必须经过对应预处理。来源：[官方仓库](https://github.com/bytedance/LatentSync)。

此项目提醒**分数依赖训练分布和预处理**。VideoGuard不处理人脸、声纹或口型，也没有使用LatentSync权重。

### BAGEL：统一多模态理解与生成

官方仓库提供训练/评测说明，描述7B活跃/14B总参数模型与大规模交错预训练、图像编辑、多视图与导航能力，并有公开Demo入口。来源：[仓库](https://github.com/ByteDance-Seed/Bagel)。

借鉴研究项目要同时公开代码、评测、模型与失败案例的结构；没有把225参数测量特征模型包装为BAGEL式基础模型。

### DeerFlow：长时任务的工程证据

公开仓库当前为长时SuperAgent harness，支持memory/tools/skills/subagents；2.0与1.x代码分开，并有read-only showcase，提示部署前关注安全边界。来源：[仓库](https://github.com/bytedance/deer-flow)。

借鉴运行轨迹与可回放成果，而非复制整个Agent产品。VideoGuard目前是确定性实验工具，不是多智能体自动研究系统。

## 2. Anthropic：访谈线索必须落到可核验一手材料

用户希望从最新科技访谈寻找选题。访谈转载只能作为线索，**本轮没有核验到覆盖最新项目的完整一手访谈逐字稿，不能把二手摘要当作CEO原话或“最新访谈结论”**。以下为实际核验的官方项目/工程材料，不能标成“已复现”。

### Agents 官方索引与记忆/具身方向

官方Agents索引在检索时列出2026-11-06的The components of agent memory（dreaming整理记忆与纠错）、Project EVE，以及Project Fetch: Phase two等探索。来源：[官方主题索引](https://www.anthropic.com/search?topic=agents)。

这些方向涉及长时智能体与行动，并非视频生成技术。对本项目的价值是审慎区分模型输出、行动后结果及失败边界。当前未做dreaming算法和真实机器人实验。

### 电子原型：从软件输出到物理验证仍有缺口

官方electronics-design材料描述三个电子设备设计/原型以及PCB routing、结构/固件等协作；同时明确原型未经过电气验证、天线调优、热测试或认证，物理制作测试仍由工程师完成。来源：[官方项目文章](https://www.anthropic.com/research/claude-electronics-design)。

这个方向与电子/数据中心兴趣相关，但本轮选择**音画同步可靠性**单一领域，不再另堆PCB项目。不能用生成了设计文件替代硬件正确性证明。

### Evals：评分输出不等于验证最终状态

Anthropic工程文章区分task、trial、grader、transcript/trace和outcome，强调代码、模型、人类三类grader各有优缺点，模型grader需要与人校准。来源：[Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)。

本仓库用客观代码核验梯度、数据隔离、参数导出、媒体链路和失败样本；未接入真实Claude grader，所以没有“Anthropic评分”或“真人对齐”结果。

## 3. 相邻评测研究与方法边界

- **VBench**：16维评估，而非一个FVD总分；包含主体/背景、flicker、运动和平滑度，指出静态视频可在时序一致性上取巧。来源：[论文](https://arxiv.org/pdf/2311.17982)。本项目不是VBench实现，未计算DINO/CLIP/RAFT指标。
- **VBench-2.0**：引入内在忠实度、物理与常识等更高级方面。来源：[论文](https://arxiv.org/pdf/2503.21755v1.pdf)。本项目没有物理真实性判别器，分窗延时矛盾不等于世界模型评测。
- **T2AV-Compass**：公开论文将视频、音频、跨模态语义和时序同步区分，谈及Synchformer等同步度量。来源：[论文](https://arxiv.org/html/2512.21094v2)。本项目仅实现信号事件级延时，未计算CLAP、ImageBind、FAD、FVD或唇形同步。
- **Direct Motion Models / TRAJAN**：讨论点轨迹的时序信息与帧级分数限制。来源：[论文](https://arxiv.org/pdf/2505.00209)。当前没有训练点轨迹模型。
- **Calibrated controllable video / C3**：探讨视频置信与OOD并明确可交换性/分布限制。来源：[论文](https://arxiv.org/html/2512.05927v1)。本项目只做小型分类温度/集合，不是生成模型的像素不确定性。

## 4. 做深的选择

从以上公开项目归纳的**个人判断**：在没有授权大数据与GPU训练条件时，最有说服力的作品不是“复刻基础模型”的宣称，而是把一个可证伪、可复现的小问题做深。音画事件同步有明确时序真值、可控故障、适合CPU实验、可观察交互和真实媒体接口。

VideoGuard的当前证据支持：某些干扰下复杂特征有帮助；ID不胜过相关性；双塔未稳定胜出；简单校准集不保证拒估或OOD覆盖。完整结果与负例应成为项目主角，而不是只展示成功率。

## 5. 下一阶段验收而非空承诺

必须取得授权真实闪光/敲击视频，按拍摄会话划分，独立标注时间误差和声源。评估多设备、压缩、帧率、多个声源，并同时报告“有证据可估比例”“保留部分误差”“所有样本误差”。此之前不填写真实世界准确率和生产价值。
