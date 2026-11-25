# TextGuard｜可解释短文本分类

<!-- project-navigation:start -->
[运行 Demo](https://llewynlune.github.io/ai-portfolio/projects/textguard/demo.html) · [深化分析](https://llewynlune.github.io/ai-portfolio/projects/textguard/depth-demo.html) · [作品集](https://llewynlune.github.io/ai-portfolio/index.html#experiments)
<!-- project-navigation:end -->


状态：真实本地训练 + 留出评测 + 浏览器模型推断；AI 辅助实现，不是字节上线系统、现代诈骗检测或论文成果。

## 看作品

[交互 Demo](https://llewynlune.github.io/ai-portfolio/projects/textguard/demo.html) · [实测报告](artifacts/REPORT.md) · [模型参数](artifacts/model.json) · [原始结果](artifacts/results.json) · [完整性](artifacts/checksums.json)

## 问题与方案

目标是展示从公开数据到训练、验证、误判与模型部署的闭环，而不是把模型名罗列成技能。使用英语短信的旧研究数据训练 TF-IDF 词项/二元词项与 Logistic Regression，比较多数类基线与 MultinomialNB。展示模型倾向和词项 logit 贡献，未知词表或阈值附近交人工复核。

## 真实训练协议

1. URL、邮箱、数字归一化，完全重复文本先去重；标签冲突移除。
2. 固定随机种子分 60% 训练、20% 验证、20% 测试，记录每个样本哈希。
3. TF-IDF 只在训练拟合；CV 用 Pipeline 每折拟合，不提前看验证/测试词表。
4. 正则强度预设 C=4，不按测试调参；决策阈值只最大化验证 F1。
5. 测试 Precision/Recall/F1、ROC-AUC、Brier 和混淆矩阵全部保留。NB 和 Logistic 的阈值方案不同，明确报告，不宣称等条件SOTA。
6. 导出安全 JSON 词表、IDF、权重、截距；Python 导出推断与训练估计器在每个测试样本对照，最大误差写入结果。

## 运行

仓库根目录：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-ml.txt
.venv/bin/python projects/textguard/train.py
python3 scripts/build_ai_demos.py
```

首次训练从 UCI 下载公开数据到本项目 private/；该目录禁止提交和打包。重建 Demo 需其他两个项目的结果也存在。

## 数据与公开边界

来源：https://archive.ics.uci.edu/dataset/228/sms+spam+collection

数据页规模与下载实际行数可能不同，报告按解析结果。公开只保存模型参数、样本哈希和预测，不保存原短信、联系人、电话或原数据包。来源数据版权和原研究限制仍适用；本仓库未替原数据授予许可。

## 局限与不利结果

旧英语短信，不代表中文或现代诈骗；完全去重不消除语义近重复。概率未校准，Brier 只用于比较，不作为人身财产安全保证。Logistic 可能较高召回但误报更多；NB 可以零误报但漏掉更多 spam，全部记录，不挑漂亮数字。

## 贡献

用户提出作品集目标与本地＋大模型方向；代码、评测与文档由 AI 辅助完成。本人独立理解、改动和实验贡献待记录，不包装为过去独立研发经历。下一步应独立修改正则强度或归一化方案，只在训练/验证上选型，再一次性评测新的冻结测试协议。

## 深化批次：研究与工程验证

新增词项变形不变性、拼写/否定/未知语言探针；复查原测试的保留覆盖率与错误率，不将启发式门限当安全保证。

[深化交互分析](https://llewynlune.github.io/ai-portfolio/projects/textguard/depth-demo.html) · [新增实测报告](artifacts/depth/REPORT.md) · [新实验代码](depth.py) · [逐条新证据](artifacts/depth/results.json)

原模型和原报告保持冻结；本批结果只写artifacts/depth。所有参数扫描均为探索，不在测试上选择配置后声称独立评测；AI辅助实现与本人独立贡献分开。
