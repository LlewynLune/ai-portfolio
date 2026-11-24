# ChannelEst｜导频驱动的学习型信道估计

状态：核心真实训练/数值评测与本地模型推断已完成；AI辅助研究原型，不是生产项目或过往本人独立履历。

**方向：信息与通信工程 / 数字信号处理 / 通信AI**

## 值得追问的问题

从稀疏导频学出的线性映射是否能降低信道误差及误码？与拥有信道先验的LMMSE相比差在哪里？

## 完整入口

[交互Demo](demo.html) · [方法与评测](METHOD.md) · [模型卡](MODEL_CARD.md) · [全部实测](artifacts/REPORT.md) · [逐条结果](artifacts/results.json) · [参数](artifacts/model.json) · [哈希](artifacts/checksums.json)

## 实现结构

Rayleigh多径仿真 → 32频点/8单位导频/24 QPSK数据 → 复AWGN → 导频特征 → 插值/学习Ridge/先验LMMSE/真CSI → 固定均衡 → NMSE与BER。

## 复现

仓库根目录先按 requirements-ml.txt 建立隔离环境。

```bash
.venv/bin/python projects/channel-est/train.py
python3 scripts/build_cross_demos.py
.venv/bin/python -m unittest discover -s tests -p test_cross_projects.py -v
```

第一次批量重建页面需全部四个结果文件存在。直接双击demo.html即可推断；不连接设备，不上传输入，不需要密钥。训练代码与共享数值函数都在仓库内。

## 下一步本人可完成的深度贡献

本人可新建不同导频间隔或错误噪声先验的消融，重新生成独立实验；再补时域IFFT/CP等模块时必须验证频域等效性，不能把本批改名为完整射频链路。

## 参考与归属

概念/数据参考：https://wirelesspi.com/channel-estimation-in-ofdm-systems/。本实验结果只由本仓库代码产生，不是参考材料作者的结果。用户选方向；代码、实验、文档与展示由AI辅助完成，本人亲自修改/复核贡献待记录。没有虚构作者、论文、实习身份或上线指标。

## 深化批次：研究与工程验证

新增缺失导频输入与观测导频LS对照，少于4观测时显式拒估；零填充值不能冒充已观测数据。

[深化交互分析](depth-demo.html) · [新增实测报告](artifacts/depth/REPORT.md) · [新实验代码](depth.py) · [逐条新证据](artifacts/depth/results.json)

原模型和原报告保持冻结；本批结果只写artifacts/depth。所有参数扫描均为探索，不在测试上选择配置后声称独立评测；AI辅助实现与本人独立贡献分开。
