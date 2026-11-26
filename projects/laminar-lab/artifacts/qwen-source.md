# 来源与真实性边界

- 模型权重公开来源：https://huggingface.co/mlx-community/Qwen3-4B-Instruct-2507-4bit ，固定 revision 50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b。本机预下载 safetensors；没有下载后执行仓库自定义代码。模型身份为实验对象，不是作品集助手的身份。
- 框架机制参考：Laminar https://github.com/verl-project/laminar 及 https://arxiv.org/html/2510.12633v1 。本新增实验为个人AI辅助机制研究，未使用官方训练后端，未贡献官方代码，不宣称字节团队项目。
- 本地实验：公共模型通过MLX运行，LoRA rank4附加到末两层注意力q/v，行为概率取词表中A/B两token后归一化。中心化与温度都是本实验决策策略一部分。
- 数据：自建求和比较任务，训练/留出与更长输入均无完全相同或反向输入。共享语法、重复使用留出集和后验消融已披露。无内部资料、自然用户数据、API日志。
- 本地重新载入最终adapter，检查概率恢复；记录审计不包含GPU梯度回放。本机真实训练、静态展示、单token机制不冒充开放生成、多轮agent RL、真实集群吞吐或生产效果。
