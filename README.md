# 于跃｜AI 作品集

> 现已包含 FlowBench 可靠性实验台：本地可运行、可测试、有真实计时的合成实验与交互展示。代码由 AI 辅助搭建，用户个人实现与复核贡献尚待记录；三类旧目录仍是待填模板。未连接远程仓库，未公开发布。

我的作品集将围绕一条主线组织：从真实用户问题出发，用可检验的方法设计 AI 方案，再用工程机制把结果稳定交付。

## 先从这里看

打开 index.html 查看个人主页。先从旗舰项目 [FlowBench 可靠性实验台](projects/reliability-lab/README.md) 开始，查看 [交互展示](projects/reliability-lab/demo.html)、[实测报告](projects/reliability-lab/results/reference/REPORT.md)、[架构](projects/reliability-lab/ARCHITECTURE.md) 和 [贡献边界](projects/reliability-lab/CONTRIBUTIONS.md)。

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

你目前还没有 GitHub 账号。请先按 [GitHub 建号、建仓与上传指南](docs/github-setup-guide.md) 本人完成注册、二次验证和远程仓库创建；账号创建后，我可以继续协助连接、检查和上传。

## 案例矩阵

[Seed/Top Seed 青年人才作品集形式矩阵](docs/portfolio-case-matrix.md) 整理了公开可核验的个人主页、论文、代码、项目和 Demo 形式。身份信息来自本人主页，不写成公司官方人事确认。

## 上传前

请先阅读 [公开发布检查](PUBLISHING.md)。现在还不适合当作完成版投递或公开发布。

## 形式参考（公开来源，不代表与本人有关）

完整公开入口和逐人形式见 [案例矩阵](docs/portfolio-case-matrix.md)。以下两个入口适合先读：

- [Wanjun Zhong 个人主页](https://zhongwanjun.github.io/cn/)：本人主页自述参与 TopSeed；按研究方向分组成果，结合职责、论文与代码。
- [Ziniu Li 个人主页](http://www.liziniu.org/) 与 [Bio](http://www.liziniu.org/bio.html)：Bio 自述曾任 Top Seed Intern；独立域名分设 Bio、Publication、Blog、Talk、CV。

这些是展示逻辑的参考，不是复制他人简介、项目代码或成果。个人自述不等于公司官方人事确认。
