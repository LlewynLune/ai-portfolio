# 本地大模型运行与复现

## 状态

已在Apple Silicon / 48GB统一内存电脑上真实运行公开4bit模型。隔离环境位于 /tmp/portfolio-llm-env；权重在个人Hugging Face缓存，不打包、不上传GitHub。该隔离环境是临时目录，重启或清理后需要重建。

## 固定模型

- 模型来源：mlx-community/Qwen3-4B-Instruct-2507-4bit。
- 固定revision：50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b。
- 原始模型来源：Qwen/Qwen3-4B-Instruct-2507，公开Apache-2.0标记；量化版本由社区提供，不代表本人训练。
- 加载safetensors；trust_remote_code=false；只读取预下载本地目录。

## 复现步骤

在仓库根目录建立个人隔离Python3.11环境，不覆盖系统Python。安装requirements-local-llm.txt。需要macOS26及Apple Silicon；其他系统可运行核心测试，但当前推断适配器不是跨平台后端。

首先用huggingface_hub.snapshot_download按上述模型名与revision下载公开权重，显式token=False，不读取账户密钥。模型目录传给以下命令，替换MODEL_PATH为个人实际目录。

从 projects/cite-rag 目录执行：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python -m memory_agent.ask --model-path MODEL_PATH --namespace maple --key review_budget --question "What is the current review_budget?"
```

主实验：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python -m memory_agent.evaluate --model-path MODEL_PATH --output private/reproduced-primary --split all
```

探索性挑战：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python -m memory_agent.challenges --model-path MODEL_PATH --primary private/reproduced-primary --output private/reproduced-challenges
```

v2回归（非独立留出）：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python -m memory_agent.evaluate_v2 --model-path MODEL_PATH --output private/reproduced-v2
```

输出目录必须不存在；脚本拒绝覆盖原运行。不运行build_dataset重新生成答案，episodes.json与manifest是冻结数据。复现结果因系统、版本与推断数值差异可能不同；本轮只运行单个量化模型单次greedy，不宣称统计稳定性。

从仓库根目录执行核心测试：

```bash
python3 -m unittest discover -s tests -p test_memory_agent.py -v
```

## 开销与资源

固定证据预算1600tokens，单Prompt最多8192；问答最多200输出tokens，整理最多1024。实际Prompt和输出token、首次token时间、整体生成秒与GPU峰值由每条call记录，不把最大输出当实际消耗。模型加载及整理开销独立记录，没有API费用；本机电力和设备占用不是零成本。

## 安全与公开

不要将公司材料导入实验。不要将模型权重、sqlite数据库、密钥或完整个人环境上传。公开仓库保留虚构数据、代码和真实生成证据；网页是静态证据浏览，不是公网推断API。namespace隔离测试不等于用户权限和多租户安全认证。
