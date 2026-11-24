# 人才参照与本批作品边界

本轮没有新找到权威“优秀实习生/校招生完整名录”，不设满分评分，也不将内部材料中的个人成果搬到公开仓库。

公开本人主页可核验的参照：

- 任抒怀：主页自述曾任 ByteDance Seed TopSeed Intern（2024.07–2024.12），按视觉理解/生成组织论文，每项附 Paper 与 Code & Model。本人自述不等于公司人事确认。https://renshuhuai-andy.github.io/
- 陈泽徽：主页自述 TopSeed 成员，经历分研究实习与研究员；成果按 PDF / Project / Code / Demo 下钻，分共一作者与共同作者。https://lovesnowbest.site/
- 聂小楠：主页将系统、技术报告与论文并列；系统实现和研究证据互相支撑。https://codecaution.github.io/

借鉴的是问题主线、实验完整性、可运行模型、贡献披露，不复制他人代码或身份。三个新项目都为独立学习实现：TextGuard（真实训练文本分类）、CiteRAG（检索问答与真实 LLM 接口）、NoveltyLab（多变量分布迁移识别）。FlowBench 加这三项共四个项目；基线模型和接口不重复计为新项目。

数据来源：
- SMS Spam Collection：https://archive.ics.uci.edu/dataset/228/sms+spam+collection
- Wine：https://archive.ics.uci.edu/dataset/109/wine

方法边界：
- 指标：https://scikit-learn.org/stable/modules/model_evaluation.html
- Novelty / Outlier：https://scikit-learn.org/stable/modules/outlier_detection.html

SMS 页面记录规模可能与实际下载文件不一致，报告用真实解析行数。SMS 原文可能含个人细节，仅私有缓存，不公开复制；模型词表与结果不包含原短信或电话号码。Wine 仅用于受控类别迁移，不宣称真实异常标签。CiteRAG 使用 FlowBench 共享的自建知识片段，明确披露作者选择偏差。
