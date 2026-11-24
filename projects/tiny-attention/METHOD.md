# TinyAttention｜从零训练因果注意力｜方法与可证伪范围

## 问题与任务

前沿模型的核心机制需要理解，而不是用模型名填简历。本实验训练单个微型因果块，任务为三组键值对+query。key词表0–7，value词表8–15，标记16；只监督最后query的value，不训练自然语言或全部序列next-token。

$\mathrm{Attention}(Q,K,V)=\mathrm{softmax}(QK^\top/\sqrt{d_h}+M)V$；$M$为严格上三角负无穷，保证位置t不看未来。d32、2heads，每头16；pre-layernorm、residual、ReLU FFN64，16个学习位置embedding，线性输出18类。

## 训练隔离和对照

3000训练、500验证、600测试前缀去重且不相交，固定seed和1000steps。无注意力消融保留相同parameter对象，但q/k/v等未参与forward不获得梯度；**登记参数相同不等于有效参数/FLOPs相同**。消融旨在观察信息跨位置传递，不证明最优架构。

5pair OOD长序列不是随机测试，包含未在3pair训练出现的位置embedding与更长信息干扰。所有准确率与NLL单列，原始预测保留，不重复看测试调超参。

## 不利结果与解释

本次单层注意力模型并未可靠解决键值绑定；在无注意力基线上有改善，但多数答案仍可能错误。单层最后位置看到key和value却未形成充分内容绑定，是学习失败分析，不是“达到推理能力”。attention权重仅展示关联，不能作为因果解释。

## 实现与范围

独立PyTorch前向/因果mask/训练循环，autograd不是本人手写微分框架。JSON保存张量数据，浏览器原生实现layernorm、多头注意力、FFN和softmax，测试逐例对照。不是完整encoder-decoder、KV缓存、FlashAttention、RoPE、自然语言模型或原创论文。

## 参考

https://arxiv.org/abs/1706.03762

## 运行证据

[全部表](artifacts/REPORT.md)、[JSON](artifacts/results.json)留存分集/预测/损失/环境。模型结果与train.py、frontier_support.py哈希绑定，哈希只检测改动不是第三方真实性签名。修改共享基座后需重训所有依赖，不把旧评测重新打hash作为新实验。
