# VideoGuard-Lab — 音画事件同步与拒估研究

> AI 辅助搭建的可复现研究原型。主线只有一个：由观察到的视觉与音频估计事件延时，并验证何时不该给出唯一答案。不是 Seedance/Claude 复刻，不是唇形同步系统，不是生产视频审核服务。

## 从这里进入

- [交互实验台](demo.html)：真实导出参数在浏览器运行；改变延时、干扰和增益；查看概率、预测集合及分窗矛盾。页面单文件离线可用。
- [实际实验报告](artifacts/REPORT.md)：同场基线、消融、三随机种子、八类条件、负对照和不利发现。
- [方法与公式](METHOD.md)：数据生成、相关性、共享排名 MLP、双塔 InfoNCE、校准、拒估协议。
- [研究来源与选题](RESEARCH.md)：字节公开创新项目、视频多模态研究、Anthropic 可核实公开工程材料；公开来源与自建贡献分开。
- [模型卡](MODEL_CARD.md) · [贡献边界](CONTRIBUTIONS.md)。

## 校准纵深更新（0.2 / 作品集v0.7）

[纵深方法](CALIBRATION.md) · [新增实测](artifacts/calibration-depth/REPORT.md)。保留原v0.6模型与证据，新增LAC、对数LAC、随机APS、保守crossing、top1补全五方法；八组各600新留出，24轮独立校准/测试，置信门限风险曲线、零错例二项上界。不是新模型或新项目，不把集合大/无空集解释为更可靠。项目全部55项测试通过，新增JS/Python288个集合与32个风险计数一致。

重建包含纵深页的当前Demo：python3 enhance_demo.py；原build_demo.py只恢复旧版展示，仍保留用于历史复现。

## 为什么不再多堆项目

视频多模态系统存在多种不同失败：音频滞后、视觉曝光干扰、多个声源、周期歧义、静音、局部延时变化。一个漂亮的“总体质量分”会掩盖差别。本项目把问题收窄到 **闪光/敲击式事件的音画同步**，不假装以小模型解决视频语义、美学、人物身份和物理世界建模。

可证伪问题：

1. 手工测量特征的学习模型是否优于原始相关性？
2. 双塔时序表示学习是否真的值得增加复杂度？
3. 在噪声与局部变化下，置信概率和候选集合是否可靠？
4. 在无对应证据时，是否会自信地给出错配？

**答案必须看实测，不预设“AI 更强”。** ID 下相关性与主模型同为满分；复杂模型并不稳定获胜。拒估能降低保留估计量，但仍有负对照漏过，不能证明安全。

## 快速复现

在本项目目录运行（Python 3.11+；本次训练实测 Python 3.14 / NumPy 2.5.4）：

```sh
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 check_js_parity.py
```

重新训练建议输出到新目录，避免覆盖冻结证据：

```sh
python3 -m videoguard.experiment --out reproduced-main
python3 -m videoguard.experiment --quick --out reproduced-quick
```

双塔与诊断脚本默认生成 artifacts 下对应证据；如要严格保持冻结文件，先在仓库副本中运行：

```sh
python3 -m videoguard.train_contrastive
python3 -m videoguard.diagnostics
python3 build_demo.py
```

三主模型 optimizer seed：7 / 19 / 31。三双塔 seed：43 / 57 / 71。选择 checkpoint 仅用验证 NLL；主模型固定 seed 7，不按测试结果选“最好的一次”。所有模型均 CPU 实际训练。

## 本地真实媒体入口

安装 FFmpeg 后，对**自己拥有或已授权的本地视频**运行：

```sh
python3 -m videoguard.media my-owned-clip.mp4 --out local-report.json
```

再在 Demo 左侧选择导入 JSON。原始媒体不上传网络；浏览器只读取本地选定文件。1.2–30 秒、100 MiB 上限、必须有音频/视频；统一到 20 fps 与 8 kHz 单声道。真实视频一律未知分布，报告强制人工复核。不会修改源视频，不能声称已校准到真实拍摄数据。

[自建编码视频与解码烟雾证据](artifacts/media-smoke.json)验证的是 MP4→RGB/PCM→特征→报告链路，不是自然视频准确率。

## 深度产物，而非空目录

- 独立生成 RGB 帧与 PCM 音频；数据 seeds / SHA-256 清单。
- 12维测量特征、13个候选延时，手写 MLP 梯度与 Adam。
- 两个独立时序编码器、单位归一化 embedding、InfoNCE 损失与梯度。
- 三种简单基线、原始相关性特征消融、三次训练重复。
- 温度校准、ECE/NLL/Brier、候选集合覆盖、选择性预测。
- 1.6秒滑窗定位、时序矛盾、八组条件与四组负对照。
- 梯度有限差分、标签盲性、哈希、分组隔离、JS/Python一致性、媒体链路测试。
- 原始逐样本预测、失败记录、模型参数、训练日志与报告。

## 坚持的边界

所有视频是本项目脚本生成的几何打击垫/闪光合成数据，没有私人视频、人脸、公司资料或用户声纹。公开仓库只含公开研究引用和本项目代码。未下载或运行 BAGEL、LatentSync、Depth Anything 权重，未执行真实 LLM/生成视频 API。代码与研究整理由 AI 辅助，本人的独立理解、修改和复核须继续记录。
