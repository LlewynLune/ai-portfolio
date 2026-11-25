# VisionCal｜小型神经网络校准与鲁棒性

<!-- project-navigation:start -->
[Project Page](https://llewynlune.github.io/ai-portfolio/projects/vision-cal/project.html) · [运行 Demo](https://llewynlune.github.io/ai-portfolio/projects/vision-cal/demo.html) · [深化分析](https://llewynlune.github.io/ai-portfolio/projects/vision-cal/depth-demo.html) · [作品集](https://llewynlune.github.io/ai-portfolio/index.html#experiments)
<!-- project-navigation:end -->





状态：核心真实训练/数值评测与本地模型推断已完成；AI辅助研究原型，不是生产项目或过往本人独立履历。

**方向：AI算法 / 视觉分类 / 概率校准**

## 值得追问的问题

网络准确率更高时，置信度是否更可信？验证集选择的温度能否迁移到噪声和平移数据？

## 完整入口

[交互Demo](https://llewynlune.github.io/ai-portfolio/projects/vision-cal/demo.html) · [方法与评测](METHOD.md) · [模型卡](MODEL_CARD.md) · [全部实测](artifacts/REPORT.md) · [逐条结果](artifacts/results.json) · [参数](artifacts/model.json) · [哈希](artifacts/checksums.json)

## 实现结构

公开8×8灰度样本 → 固定训练/验证/测试 → 64输入/48 ReLU隐藏/10类别MLP → 验证温度搜索 → 清洁/噪声/平移对照 → 高置信度错误分析 → JSON参数与浏览器推断。

## 复现

仓库根目录先按 requirements-ml.txt 建立隔离环境。

```bash
.venv/bin/python projects/vision-cal/train.py
python3 scripts/build_cross_demos.py
.venv/bin/python -m unittest discover -s tests -p test_cross_projects.py -v
```

第一次批量重建页面需全部四个结果文件存在。直接双击demo.html即可推断；不连接设备，不上传输入，不需要密钥。训练代码与共享数值函数都在仓库内。

## 下一步本人可完成的深度贡献

本人可新增一个只在验证集选择的噪声增强模型，保留本批原始对照；独立实现ECE，解释一个高置信错例。不能在测试上反复调温度后仍称独立留出。

## 参考与归属

概念/数据参考：https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html。本实验结果只由本仓库代码产生，不是参考材料作者的结果。用户选方向；代码、实验、文档与展示由AI辅助完成，本人亲自修改/复核贡献待记录。没有虚构作者、论文、实习身份或上线指标。

## 深化批次：研究与工程验证

新增8种图像噪声/平移/中心遮挡条件和置信门限风险覆盖曲线；保留测试温度失效与高置信错误。

[深化交互分析](https://llewynlune.github.io/ai-portfolio/projects/vision-cal/depth-demo.html) · [新增实测报告](artifacts/depth/REPORT.md) · [新实验代码](depth.py) · [逐条新证据](artifacts/depth/results.json)

原模型和原报告保持冻结；本批结果只写artifacts/depth。所有参数扫描均为探索，不在测试上选择配置后声称独立评测；AI辅助实现与本人独立贡献分开。
