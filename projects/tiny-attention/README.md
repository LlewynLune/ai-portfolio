# TinyAttention｜从零训练因果注意力

<!-- project-navigation:start -->
[Project Page](https://llewynlune.github.io/ai-portfolio/projects/tiny-attention/project.html) · [运行 Demo](https://llewynlune.github.io/ai-portfolio/projects/tiny-attention/demo.html) · [深化分析](https://llewynlune.github.io/ai-portfolio/projects/tiny-attention/depth-demo.html) · [作品集](https://llewynlune.github.io/ai-portfolio/index.html#experiments)
<!-- project-navigation:end -->





状态：实际CPU训练/运行的机制复现，AI辅助实现；不是论文性能复现或原创算法。

[Demo](https://llewynlune.github.io/ai-portfolio/projects/tiny-attention/demo.html) · [原理与公式](METHOD.md) · [模型卡](MODEL_CARD.md) · [实测](artifacts/REPORT.md) · [逐样本证据](artifacts/results.json) · [参数](artifacts/model.json) · [哈希](artifacts/checksums.json)

## 真实运行

3000 train,500 validation,600 held-out3pair prefixes disjoint;600 authored5pair OOD. Fixed1000 Adam steps and no-attention ablation. Only final query value is supervised, not full language modeling.

## 重训

先按requirements-frontier.txt安装CPU torch及numpy/sklearn；不包含GPU依赖或任何模型密钥。

```bash
.venv/bin/python projects/tiny-attention/train.py
python3 scripts/build_frontier_demos.py
.venv/bin/python -m unittest discover -s tests -p test_frontier_projects.py -v
```

LoRA与DPO依赖tiny-attention/artifacts/model.json，需先训练TinyAttention；五项目结果齐全才能批量重建Demo。静态文件不需要安装torch，直接打开demo.html即可运行参数。PyTorchJSON为纯数字tensor，不用pickle加载不可信对象。

## 个人贡献与参考

用户选择扩充前沿算法，代码/文档/评测AI辅助完成；本人独立理解、改动、测试贡献待记录。不能作为过去论文/实习/生产项目。参考原论文：https://arxiv.org/abs/1706.03762。本批数字全部来自本仓库代码，不搬用论文结果。

## 深化批次：研究与工程验证

新增NumPy独立推断、逐前缀因果一致性、长度2–7/顺序/未知query压力；新前缀排除原训练/验证/测试ID。

[深化交互分析](https://llewynlune.github.io/ai-portfolio/projects/tiny-attention/depth-demo.html) · [新增实测报告](artifacts/depth/REPORT.md) · [新实验代码](depth.py) · [逐条新证据](artifacts/depth/results.json)

原模型和原报告保持冻结；本批结果只写artifacts/depth。所有参数扫描均为探索，不在测试上选择配置后声称独立评测；AI辅助实现与本人独立贡献分开。
