# v2.3 · Qwen LoRA reward signal study

基线7c93b57，包含已在本机完成的v2.2实时异步恢复继续工作：24条运行链、16次真实整进程退出、480个提交更新回放、2983个RNG状态检查。该部分与Qwen实验严格分开，不宣称Qwen已经接入实时异步恢复。

## 新增实际实验

固定公开Qwen3-4B 4-bit本地模型，最后两层q/v rank4 LoRA，81,920可训练参数。12条采样优化链共144批、288步Adam、9216动作抽样；动作限制在两个真实词表token，因此是语言模型驱动的contextual bandit，不是开放推理或多轮Agent RL。

第一批6链，组内奖励有差异5/576；两套留出均全选A，32/64。追加批次仅用训练输入的冻结模型logit中位数做偏置校准，获得545/576有差异的奖励组。校准本身改善基线，不能混成RL提升；各seed/lag结论方向不一，保留seed19 lag0全选B的失败。已有评估集合被重复使用，不称预注册或全新盲测。

CPU独立复算：抽样、奖励、版本链接、数据去重、评价/NLL。校准版6份adapter重载相同基座，全部768题的概率和决策与记录相同。不是训练梯度的独立重放，hash也不是可信签名。

## 交付与边界

QWEN_STUDY.md、qwen-study.html、qwen-policy/与qwen-centered/原数据、原始执行快照、qwen-audit.json、qwen-reload.json，运行器llm_policy.py与qwen_reload.py。仓库不发布基座和adapter，可用运行器复现；全部旧项目、原业务事实、公众号播客简介保持。

单机顺序切换快照来注入lag，没有GPU异步分布式运行；不能写Laminar论文性能、大模型训练稳定性或自然语言泛化成绩。确定性求和规则全正确，任务只用于机制验证，不证明LLM必要性。
