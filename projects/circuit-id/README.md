# CircuitID｜噪声RC阶跃的学习型系统辨识

<!-- project-navigation:start -->
[运行 Demo](https://llewynlune.github.io/ai-portfolio/projects/circuit-id/demo.html) · [深化分析](https://llewynlune.github.io/ai-portfolio/projects/circuit-id/depth-demo.html) · [作品集](https://llewynlune.github.io/ai-portfolio/index.html#experiments)
<!-- project-navigation:end -->


状态：核心真实训练/数值评测与本地模型推断已完成；AI辅助研究原型，不是生产项目或过往本人独立履历。

**方向：电子科学与技术 / 信号处理 / 系统辨识**

## 值得追问的问题

已知输入和采样条件时，学习回归是否优于简单阈值？物理拟合在哪些分布变化下更可靠？

## 完整入口

[交互Demo](https://llewynlune.github.io/ai-portfolio/projects/circuit-id/demo.html) · [方法与评测](METHOD.md) · [模型卡](MODEL_CARD.md) · [全部实测](artifacts/REPORT.md) · [逐条结果](artifacts/results.json) · [参数](artifacts/model.json) · [哈希](artifacts/checksums.json)

## 实现结构

理想RC阶跃生成 → 随机tau/增益/噪声 → 32点观测 → 63%规则/物理拟合/Ridge/MLP → 验证选型 → 多seed与OOD → 波形重建和残差带。

## 复现

仓库根目录先按 requirements-ml.txt 建立隔离环境。

```bash
.venv/bin/python projects/circuit-id/train.py
python3 scripts/build_cross_demos.py
.venv/bin/python -m unittest discover -s tests -p test_cross_projects.py -v
```

第一次批量重建页面需全部四个结果文件存在。直接双击demo.html即可推断；不连接设备，不上传输入，不需要密钥。训练代码与共享数值函数都在仓库内。

## 下一步本人可完成的深度贡献

本人可在新版本加入未知增益/偏置联合物理拟合，公平比较；或用授权低压台架测量集独立验证，但必须保留硬件条件、校准和测量权限，不替换本批仿真结果。

## 参考与归属

概念/数据参考：https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits。本实验结果只由本仓库代码产生，不是参考材料作者的结果。用户选方向；代码、实验、文档与展示由AI辅助完成，本人亲自修改/复核贡献待记录。没有虚构作者、论文、实习身份或上线指标。

## 深化批次：研究与工程验证

新增增益/偏置未知条件下的变量投影物理拟合，对照单位输入拟合与冻结Ridge；保留长tau不可辨识风险。

[深化交互分析](https://llewynlune.github.io/ai-portfolio/projects/circuit-id/depth-demo.html) · [新增实测报告](artifacts/depth/REPORT.md) · [新实验代码](depth.py) · [逐条新证据](artifacts/depth/results.json)

原模型和原报告保持冻结；本批结果只写artifacts/depth。所有参数扫描均为探索，不在测试上选择配置后声称独立评测；AI辅助实现与本人独立贡献分开。
