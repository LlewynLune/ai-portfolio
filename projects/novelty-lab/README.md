# NoveltyLab｜多变量新颖性检测

状态：实际拟合三类本地模型 + 数值推断 Demo；AI 辅助实现。不是工业异常检测、欺诈识别、生产业务或原创算法。

[Demo](demo.html) · [实测报告](artifacts/REPORT.md) · [部署模型](artifacts/model.json) · [全部结果](artifacts/results.json) · [完整性](artifacts/checksums.json)

## 定义的任务

Wine 公共数据有 178 行 13 维化学特征、三个类别。把类别 0 **人为定义**为正常分布，其他两类定义为未知类别迁移；类改变不是数据原有异常标签。因此这是演示 novelty 协议的受控实验。

来源：https://archive.ics.uci.edu/dataset/109/wine

## 模型与协议

- 正常类别分固定训练、正常验证、正常测试，未知类别只放测试。
- StandardScaler 仅拟合正常训练；新点用同一个缩放参数，不重新 fit。
- 拟合 centroid distance、Isolation Forest 和 One-Class SVM，阈值各自仅用正常验证 95 分位选取。
- 默认部署 centroid distance 是预先选择的可解释基线，不按测试最高分改名为胜出算法。
- 保存每个测试分数、决策、标签与混淆矩阵；ROC-AUC、PR-AUC、Precision/Recall、正常误报分别报告。
- Demo 用训练输出的标准化参数与中心直接运行，可显示哪些标准化特征偏离大；不是因果解释。

## 复现

```bash
.venv/bin/python projects/novelty-lab/train.py
python3 scripts/build_ai_demos.py
```

先在仓库根目录建立 .venv 并安装 requirements-ml.txt。sklearn 的内置 Wine 数据无需远程下载。

## 失败与限制

测试正常点只有 12 条，零误报不能推出生产零误报；类分离本来很容易，高 AUC 不代表真实异常能力。正常验证少，阈值不稳定；测试迁移比例高，precision 受比例影响。距离是非负分数，不是校准概率。默认模型会漏掉部分迁移样本，复杂模型也不必然更优。

## 人机分工

机器仅给分布差异和特征提示；人工决定是否需要调查，不自动拒绝业务或认定欺诈。没有用户访谈和试点业务。

代码、实验和文档 AI 辅助完成，本人贡献待亲自验证和修改后补充。各基线只算一个项目的实验对照，不拆分成多个项目计数。

## 深化批次：研究与工程验证

新增13维单特征标准化扰动与决策翻转；距离归因改为相对拟合中心的平方贡献，明确相关变体不能当独立样本。

[深化交互分析](depth-demo.html) · [新增实测报告](artifacts/depth/REPORT.md) · [新实验代码](depth.py) · [逐条新证据](artifacts/depth/results.json)

原模型和原报告保持冻结；本批结果只写artifacts/depth。所有参数扫描均为探索，不在测试上选择配置后声称独立评测；AI辅助实现与本人独立贡献分开。
