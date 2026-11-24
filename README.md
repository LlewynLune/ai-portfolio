# 于跃｜AI 作品集

> 十四个 AI 辅助研究项目：新增专精音画同步可靠性的 VideoGuard-Lab，加已有十三项机制与跨学科研究原型。真实CPU训练、合成数据、共享基座与未验证边界分别披露；不是大模型训练、原创突破或生产成果，真实远程LLM未调用。当前本地源码 v0.7；GitHub 与 Pages 是否已更新以最新提交/部署记录为准。

## 专精主项目：VideoGuard-Lab（v0.7）

新增[校准纵深方法](projects/video-guard/CALIBRATION.md)与[实测](projects/video-guard/artifacts/calibration-depth/REPORT.md)：五种集合方法、24轮独立重复、八组新留出、风险—保留曲线。模型冻结，旧版证据保留，项目数仍14。

[交互Demo](projects/video-guard/demo.html) · [代码与复现](projects/video-guard/README.md) · [实测报告](projects/video-guard/artifacts/REPORT.md) · [方法](projects/video-guard/METHOD.md) · [公开研究对照](projects/video-guard/RESEARCH.md)

单一主线：音画事件同步与拒估。自建RGB/PCM、手写共享MLP和双塔InfoNCE、三seed训练、同场基线、校准集合、滑窗矛盾、八类条件、四组负对照与本地FFmpeg入口。ID不优于简单相关性、双塔未稳定胜出、集合覆盖与拒估均有失败；不把合成满分包装为SOTA。项目不依赖旧模型，不复制字节/Anthropic私有实现。

## 五项前沿机制：本批v0.5

|作品|实际训练与核验|深入入口|
|---|---|---|
|[TinyAttention](projects/tiny-attention/README.md)|单块因果多头、查找任务、无attention消融/长度OOD|[Demo](projects/tiny-attention/demo.html) · [报告](projects/tiny-attention/artifacts/REPORT.md)|
|[LoRA-Lab](projects/lora-lab/README.md)|冻结基座、A/B rank1/4、全量基线、合并与遗忘|[Demo](projects/lora-lab/demo.html) · [报告](projects/lora-lab/artifacts/REPORT.md)|
|[DPO-Lab](projects/dpo-lab/README.md)|真实DPO损失、reference、beta与SFT、win/top1/KL|[Demo](projects/dpo-lab/demo.html) · [报告](projects/dpo-lab/artifacts/REPORT.md)|
|[SparseMoE](projects/moe-lab/README.md)|真正top1分发、负载辅助、dense双基线、skewOOD|[Demo](projects/moe-lab/demo.html) · [报告](projects/moe-lab/artifacts/REPORT.md)|
|[SpecDecode](projects/spec-decode/README.md)|独立训练target/draft、greedy块验证、逐token一致、实际CPU计时|[Demo](projects/spec-decode/demo.html) · [报告](projects/spec-decode/artifacts/REPORT.md)|

[前沿机制阅读地图与完整结果](docs/frontier-evidence.md)。前三项共享TinyAttention基座，不宣称独立数据/大模型研究。原论文用于概念对照，本批数字来自本仓库；2017–2023经典机制复现，不是2026最新前沿综述。

## 跨学科四项目：本批v0.4

|方向|独立作品|可验证核心|边界|
|---|---|---|---|
|AI算法|[VisionCal](projects/vision-cal/README.md)|真实小型神经网、温度校准、噪声/平移、可编辑像素[Demo](projects/vision-cal/demo.html)|公开8×8图像，不是大型视觉模型|
|电子科学与技术|[CircuitID](projects/circuit-id/README.md)|RC辨识，规则/物理/学习对照、OOD和波形[Demo](projects/circuit-id/demo.html)|纯数学仿真，无硬件实测|
|信息与通信工程|[ChannelEst](projects/channel-est/README.md)|导频估计，NMSE/BER，多SNR/先验/长delay [Demo](projects/channel-est/demo.html)|理想频域，无真实无线设备|
|AI数据中心/电气工程|[PowerScope](projects/power-scope/README.md)|下一步负荷预测、时间留出、计划消融、漂移[Demo](projects/power-scope/demo.html)|合成时序，只读预测，非容量设计/控制|

[跨学科实验阅读指南](docs/cross-disciplinary-evidence.md)说明全部结果、不利发现与同场景公平对照。

## 新三项目：可运行，不虚报上线

|作品|实际实现|证据入口|状态边界|
|---|---|---|---|
|[TextGuard](projects/textguard/README.md)|TF-IDF＋Logistic，训练/验证/测试、NB对照、权重推断|[Demo](projects/textguard/demo.html) · [报告](projects/textguard/artifacts/REPORT.md)|旧英文短信；不是现代诈骗识别|
|[CiteRAG](projects/cite-rag/README.md)|BM25/字符/RRF，引用、摘录、拒答与真实HTTPS接口|[Demo](projects/cite-rag/demo.html) · [报告](projects/cite-rag/artifacts/REPORT.md)|自建小语料；本地非LLM，真实LLM未调用|
|[NoveltyLab](projects/novelty-lab/README.md)|正常训练拟合、验证阈值、3模型对照、13维推断|[Demo](projects/novelty-lab/demo.html) · [报告](projects/novelty-lab/artifacts/REPORT.md)|类别迁移非故障标签；非生产效果|

[公开人才形式参照及数据来源](docs/ai-project-reference.md) · [实验与真实性清单](docs/ai-evidence.md) · [独立掌握路线](docs/learning-roadmap.md)


我的作品集将围绕一条主线组织：从真实用户问题出发，用可检验的方法设计 AI 方案，再用工程机制把结果稳定交付。

## 先从这里看

打开 index.html 查看个人主页。先从旗舰项目 [FlowBench 可靠性实验台](projects/reliability-lab/README.md) 开始，查看 [交互展示](projects/reliability-lab/demo.html)、[实测报告](projects/reliability-lab/results/reference/REPORT.md)、[v0.2 深化实验](projects/reliability-lab/results/advanced/REPORT.md)、[架构](projects/reliability-lab/ARCHITECTURE.md) 和 [贡献边界](projects/reliability-lab/CONTRIBUTIONS.md)。

本地启动：macOS 可运行根目录的启动可靠性实验台.command；或进入 projects/reliability-lab 后执行 python3 -m reliability_lab serve。服务仅监听本机，终端给出打开地址，Ctrl+C 停止。网页离线可看结果；GitHub Pages 不会运行 Python 后端。

先运行 [证据轨迹示例](examples/evidence-trace/README.md)，理解“责任主体、证据、复核和可回放”如何组织；它是确定性入门示例，不是 AI 模型或已完成商业项目。

先完成一个可信项目，再扩展覆盖面；不要用模板数量代替成果数量。

## 三类项目入口

- [产品与工作流](projects/product-workflow/README.md)：用户与场景、非目标、AI/规则/人的分工、正常与异常流程、Demo、试点证据。
- [算法与评测](projects/research-evaluation/README.md)：可证伪问题、基线、改进方法、消融、失败样本、可复现实验。
- [基础设施与运行](projects/infra-runtime/README.md)：性能瓶颈、可靠性、调度、追踪、成本、测量环境与复现条件。

## 每个项目必须能回答

1. 我解决什么具体问题？为什么值得做？
2. 哪一部分是我独立完成，哪一部分依赖团队、开源或 AI 工具？
3. 相对什么基线，在哪个样本与环境下得到什么结果？
4. 失败边界是什么，何时必须停止自动化并交给人？
5. 别人如何运行、观察并复核我的结论？

## 身份与内容待补

- 公开显示的姓名与英文写法：待本人确认。
- 教育、工作和日期：待本人确认，不自动引用内部简历。
- 联系方式：仅填写愿意公开的地址；不要使用默认公司邮箱。
- 已有旗舰项目：AI 辅助实现的 FlowBench 本地原型；亲自复核、修改和实验贡献待补。
- 内部工作/教育/联系方式不会自动搬入公开仓库。

## 本地检查

在仓库根目录运行 python3 scripts/check_portfolio.py，检查目录、主页、Markdown 本地链接、状态声明和不可公开的常见链接。它不是保密审查，也不能证明没有敏感内容。

运行 python3 -m unittest discover -s tests，执行骨架测试。

运行 python3 examples/evidence-trace/evidence_trace.py examples/evidence-trace/sample-events.jsonl，验证可回放示例。

## 建号与建仓

账号已完成登录与安全验证；作品集已上传至 [LlewynLune/ai-portfolio](https://github.com/LlewynLune/ai-portfolio)，GitHub Pages 已配置为 main 根目录。后续维护见 [建仓与上传指南](docs/github-setup-guide.md)。提交使用账户 noreply 身份，仅更改本仓库 Git 配置。

## 案例矩阵

[Seed/Top Seed 青年人才作品集形式矩阵](docs/portfolio-case-matrix.md) 整理了公开可核验的个人主页、论文、代码、项目和 Demo 形式。身份信息来自本人主页，不写成公司官方人事确认。

## 上传前

请阅读 [公开发布检查](PUBLISHING.md)。已公开的是合成研究原型，不是生产上线经历；个人复核与真实贡献仍需继续补齐。

## 形式参考（公开来源，不代表与本人有关）

完整公开入口和逐人形式见 [案例矩阵](docs/portfolio-case-matrix.md)。以下两个入口适合先读：

- [Wanjun Zhong 个人主页](https://zhongwanjun.github.io/cn/)：本人主页自述参与 TopSeed；按研究方向分组成果，结合职责、论文与代码。
- [Ziniu Li 个人主页](http://www.liziniu.org/) 与 [Bio](http://www.liziniu.org/bio.html)：Bio 自述曾任 Top Seed Intern；独立域名分设 Bio、Publication、Blog、Talk、CV。

这些是展示逻辑的参考，不是复制他人简介、项目代码或成果。个人自述不等于公司官方人事确认。
