# PowerScope｜AI数据中心电力负荷的离线预测与漂移

状态：核心真实训练/数值评测与本地模型推断已完成；AI辅助研究原型，不是生产项目或过往本人独立履历。

**方向：AI数据中心 / 电气工程 / 时序机器学习**

## 值得追问的问题

下一5分钟电力需求能否利用作业计划更好预测？突变与冷却漂移会不会使经验区间失效？

## 完整入口

[交互Demo](demo.html) · [方法与评测](METHOD.md) · [模型卡](MODEL_CARD.md) · [全部实测](artifacts/REPORT.md) · [逐条结果](artifacts/results.json) · [参数](artifacts/model.json) · [哈希](artifacts/checksums.json)

## 实现结构

合成作业计划/室外温度 → 透明IT/冷却/损耗模型 → 当前及历史特征 → 时间留出Ridge/持久性/季节基线 → 计划特征消融 → 峰值标记和漂移分析 → 只读Dashboard。

## 复现

仓库根目录先按 requirements-ml.txt 建立隔离环境。

```bash
.venv/bin/python projects/power-scope/train.py
python3 scripts/build_cross_demos.py
.venv/bin/python -m unittest discover -s tests -p test_cross_projects.py -v
```

第一次批量重建页面需全部四个结果文件存在。直接双击demo.html即可推断；不连接设备，不上传输入，不需要密钥。训练代码与共享数值函数都在仓库内。

## 下一步本人可完成的深度贡献

本人可用有权限的脱敏遥测另建独立数据版本（先确认可以公开），引入计划预测误差/数据缺失/多步预测；实际控制和工程验收需专业安全流程，不能由作品集模型直接执行。

## 参考与归属

概念/数据参考：https://www.energy.gov/cmei/femp/energy-efficiency-data-centers。本实验结果只由本仓库代码产生，不是参考材料作者的结果。用户选方向；代码、实验、文档与展示由AI辅助完成，本人亲自修改/复核贡献待记录。没有虚构作者、论文、实习身份或上线指标。
