# 深化批次：复现与工程使用

## 安装

在仓库根目录建立隔离Python环境，按requirements-depth.txt安装NumPy、SciPy、scikit-learn。本批不要求PyTorch，不下载或运行远程大模型。

## 逐项目复现

进入任一项目目录运行python3 depth.py。结果只写本项目artifacts/depth；原artifacts/model.json、results.json、REPORT.md不覆盖。代码哈希、原始来源哈希和逐条结果保留。

前缀实验为NumPy独立模型推断：Attention/LoRA/DPO的新查找前缀排除原ID。视觉/异常使用公开数据的固定测试ID；PowerScope和VideoGuard明确为已有冻结证据的再分析。不能把相关条件/门限扫面、重复计时视为独立样本。

## 浏览器

运行python3 scripts/build_depth_demos.py生成14项depth-demo.html，双击离线打开即可。数据直接内联，不从file路径fetch，不需要API key、不上传输入、不重训。

Depth Study支持模型、实验条件和指标选择，失败/丢弃/未覆盖筛选，逐条证据下钻、分页和JSON导出。各项目专属diagnostic展示适配曲线、路由容量、报警时限、缺失导频、拟合参数、区间覆盖等实际结果；原Demo仍执行冻结模型推断。

## 本机只读API

在仓库根运行python3 scripts/depth_server.py。仅监听127.0.0.1:8766。

- GET /health：服务状态。
- GET /api/projects：14项项目名。
- GET /api/evidence?project=spec-decode&limit=50&offset=0：最多200行，可按model/condition筛选。
- POST返回405，不执行外部调用、训练、写文件、私有数据读取或设备控制。

这是本机证据接口，不是公网部署或认证完备的生产系统。

## 测试

python3 -m unittest discover -s tests -p test_depth_projects.py -v。

覆盖冻结输出parity、因果前缀、真实KV cache、LoRA增量、MoE容量、greedy推测路径、RC未知增益偏置拟合、缺失导频拒估、延迟预算事件匹配、RAG内容指纹、无假NLL、数据ID隔离、来源哈希、本机API边界及HTTP只读。

计时含预热与策略顺序轮换，仍受机器负载影响；不从一次本机小模型计时推断商业加速比或能耗收益。
