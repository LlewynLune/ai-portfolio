# LoRA-Lab｜参数高效微调与遗忘｜方法与可证伪范围

## 真实低秩更新

共享本仓库TinyAttention已训练基座，适配规则变为value+1模8。$W=W_0+BA/r$，rank为1或4，$A$随机小值、$B=0$，起点与基座一致。只训练q/v/head的A/B，冻结所有基座embedding、FFN和原weight/bias。训练后assert基座权重未变。

实际训练参数rank1=178、rank4=712，对照全量微调10226与不更新基座。不同参数量不等于等FLOPs/等内存；没有GPU显存或推理时延的外推数字。

## 对照与选型

新规则1000训练、300验证、500测试within-task前缀去重，450steps同样optimizer；rank仅由验证准确率选。原规则500与5pair OOD300独立评测，揭示遗忘和长度迁移。各分集种子与基座训练不同，但共享合成生成器；不能称真实新领域知识。适配样本不保证与预训练集合完全跨阶段去重，已披露家族依赖。

## 合并与验证

浏览器使用 $W_\mathrm{merged}=W_0+BA/r$，保留adapter A/B张量和scale说明。PyTorch合并前后logits逐例校验，float32小误差不等于bitwise一致。输出合并只避免额外分支，没有测量真正生产延迟。

## 不利结果

rank增大可能提高新规则准确率，同时降低旧规则保留；LoRA不自动防止遗忘。输出层映射也可完成大量任务迁移，本实验不证明q/v最优。基座查找能力有限，微调难以修复所有绑定错误。全量更新更贵但未因此固定“输给LoRA”。

不含QLoRA、量化训练、真实大模型或外部语料；仅机制与对照。参数合并、冻结验证、rank对照是本项目深度，不把两种rank算两个项目。

## 参考

https://arxiv.org/abs/2106.09685

## 运行证据

[全部表](artifacts/REPORT.md)、[JSON](artifacts/results.json)留存分集/预测/损失/环境。模型结果与train.py、frontier_support.py哈希绑定，哈希只检测改动不是第三方真实性签名。修改共享基座后需重训所有依赖，不把旧评测重新打hash作为新实验。
