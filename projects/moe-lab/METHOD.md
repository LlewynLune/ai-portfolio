# SparseMoE-Lab｜真实稀疏执行与路由平衡｜方法与可证伪范围

## 稀疏实际执行

2D非线性回归，4个2→16 tanh→1专家。router是2→4线性softmax，top1选择后**只将该专家分配到的样本送进专家forward**，不先算全部expert再乘mask伪称节省计算。

输出 $p_e(x)E_e(x)$。所选probability提供router可导路径，argmax索引不可导。未选expert不获得该样本梯度。负载辅助项 $4\sum_e f_eP_e$，$f_e$为mini-batch top1比例、$P_e$为平均router概率；只对比权重0与0.03，不保证防止collapse。

## 参数和公平比较

router12参数，每个expert65，总272。单样本active估计77=router12+expert65，不等于实际FLOPs或内存加载。dense16=65参数作为active-like，dense64=257作为total-like，并非严格计算预算匹配。没有所有节点只执行一次的分布式推理或all-to-all。

2400训练、500验证、700测试，域内[-1,1]^2；skewOOD把x0集中0.6–1。700steps，负载参数仅验证RMSE选；均匀与偏斜各自报告RMSE、专家最大占比与路由entropy。

## 失败不是删除

小型MoE可能比dense差，平衡改善entropy却不必改善任务误差。OOD偏移会使大部分样本进入同expert，负载是数据与路由共同产物，不能自动解释“专家语义分工”。实际Python CPU分发可能慢，本项目没有速度结论。

## 范围

这是Switch思想的独立top1门控实验，不是Switch Transformer网络、T5训练、trillion模型、capacity掉token或分布式通信。标准库/torch模块提供底层算子。演示选专家和权重可核对，不包装为SOTA MoE。

## 参考

https://arxiv.org/abs/2101.03961

## 运行证据

[全部表](artifacts/REPORT.md)、[JSON](artifacts/results.json)留存分集/预测/损失/环境。模型结果与train.py、frontier_support.py哈希绑定，哈希只检测改动不是第三方真实性签名。修改共享基座后需重训所有依赖，不把旧评测重新打hash作为新实验。
