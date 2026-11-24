"""Project-specific method cards; evidence comes from real CPU experiments."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D={
 'tiny-attention':('TinyAttention｜从零训练因果注意力','https://arxiv.org/abs/1706.03762',r'''## 问题与任务

前沿模型的核心机制需要理解，而不是用模型名填简历。本实验训练单个微型因果块，任务为三组键值对+query。key词表0–7，value词表8–15，标记16；只监督最后query的value，不训练自然语言或全部序列next-token。

$\mathrm{Attention}(Q,K,V)=\mathrm{softmax}(QK^\top/\sqrt{d_h}+M)V$；$M$为严格上三角负无穷，保证位置t不看未来。d32、2heads，每头16；pre-layernorm、residual、ReLU FFN64，16个学习位置embedding，线性输出18类。

## 训练隔离和对照

3000训练、500验证、600测试前缀去重且不相交，固定seed和1000steps。无注意力消融保留相同parameter对象，但q/k/v等未参与forward不获得梯度；**登记参数相同不等于有效参数/FLOPs相同**。消融旨在观察信息跨位置传递，不证明最优架构。

5pair OOD长序列不是随机测试，包含未在3pair训练出现的位置embedding与更长信息干扰。所有准确率与NLL单列，原始预测保留，不重复看测试调超参。

## 不利结果与解释

本次单层注意力模型并未可靠解决键值绑定；在无注意力基线上有改善，但多数答案仍可能错误。单层最后位置看到key和value却未形成充分内容绑定，是学习失败分析，不是“达到推理能力”。attention权重仅展示关联，不能作为因果解释。

## 实现与范围

独立PyTorch前向/因果mask/训练循环，autograd不是本人手写微分框架。JSON保存张量数据，浏览器原生实现layernorm、多头注意力、FFN和softmax，测试逐例对照。不是完整encoder-decoder、KV缓存、FlashAttention、RoPE、自然语言模型或原创论文。
'''),
 'lora-lab':('LoRA-Lab｜参数高效微调与遗忘','https://arxiv.org/abs/2106.09685',r'''## 真实低秩更新

共享本仓库TinyAttention已训练基座，适配规则变为value+1模8。$W=W_0+BA/r$，rank为1或4，$A$随机小值、$B=0$，起点与基座一致。只训练q/v/head的A/B，冻结所有基座embedding、FFN和原weight/bias。训练后assert基座权重未变。

实际训练参数rank1=178、rank4=712，对照全量微调10226与不更新基座。不同参数量不等于等FLOPs/等内存；没有GPU显存或推理时延的外推数字。

## 对照与选型

新规则1000训练、300验证、500测试within-task前缀去重，450steps同样optimizer；rank仅由验证准确率选。原规则500与5pair OOD300独立评测，揭示遗忘和长度迁移。各分集种子与基座训练不同，但共享合成生成器；不能称真实新领域知识。适配样本不保证与预训练集合完全跨阶段去重，已披露家族依赖。

## 合并与验证

浏览器使用 $W_\mathrm{merged}=W_0+BA/r$，保留adapter A/B张量和scale说明。PyTorch合并前后logits逐例校验，float32小误差不等于bitwise一致。输出合并只避免额外分支，没有测量真正生产延迟。

## 不利结果

rank增大可能提高新规则准确率，同时降低旧规则保留；LoRA不自动防止遗忘。输出层映射也可完成大量任务迁移，本实验不证明q/v最优。基座查找能力有限，微调难以修复所有绑定错误。全量更新更贵但未因此固定“输给LoRA”。

不含QLoRA、量化训练、真实大模型或外部语料；仅机制与对照。参数合并、冻结验证、rank对照是本项目深度，不把两种rank算两个项目。
'''),
 'dpo-lab':('DPO-Lab｜偏好、概率排序与模型漂移','https://arxiv.org/abs/2305.18290',r'''## 目标函数

共享TinyAttention基座，偏好为value+2模8，rejected为原value，是人为规则而非人类反馈。每个response只有1token，序列logprob恰好简化为一个token logprob；这不是完整多token对话对齐。

$\mathcal L=-\log\sigma(\beta[(\log\pi_\theta(y_w|x)-\log\pi_\theta(y_l|x))-(\log\pi_\mathrm{ref}(y_w|x)-\log\pi_\mathrm{ref}(y_l|x))])$。

固定reference在no_grad下计算，不参与优化。只训练policy head，beta0.1/0.5各400steps；SFT_chosen对照同样head和步数。beta仅通过validation(pair_win-.05KL)选，组合系数预设，不查看测试选“最好”。

## 应报告四件不同的事

1. Pair win：chosen概率是否高于rejected，不等于chosen高于全部18候选。
2. Chosen top1：是否真的生成chosen。
3. 原top1保留：旧任务与新偏好冲突，所以下降可能是目标冲突，不是安全性结论。
4. KL到reference：policy||reference，用完整18类概率计算；不是训练目标显式KL惩罚，也不保证固定KL预算。

1000训练、300验证、500测试within-task不相交，保存每项chosen/rejected与概率。DPO排序提升可能伴随严重漂移，而SFT的top1可能更好；全部保留。

## 关键测试

相同policy/reference起点DPO loss应为log2；梯度应提升chosen/rejected相对差；翻转偏好改变梯度方向。权重不训练到reference，测试不能仅看loss下降。

## 不包含

不是PPO、在线RLHF、reward模型训练或真人标注。不代表模型伦理/安全/有用性，不使用敏感对话和个人数据。项目为偏好目标实现与可证伪对照，不是原创对齐算法或论文复现性能。
'''),
 'moe-lab':('SparseMoE-Lab｜真实稀疏执行与路由平衡','https://arxiv.org/abs/2101.03961',r'''## 稀疏实际执行

2D非线性回归，4个2→16 tanh→1专家。router是2→4线性softmax，top1选择后**只将该专家分配到的样本送进专家forward**，不先算全部expert再乘mask伪称节省计算。

输出 $p_e(x)E_e(x)$。所选probability提供router可导路径，argmax索引不可导。未选expert不获得该样本梯度。负载辅助项 $4\sum_e f_eP_e$，$f_e$为mini-batch top1比例、$P_e$为平均router概率；只对比权重0与0.03，不保证防止collapse。

## 参数和公平比较

router12参数，每个expert65，总272。单样本active估计77=router12+expert65，不等于实际FLOPs或内存加载。dense16=65参数作为active-like，dense64=257作为total-like，并非严格计算预算匹配。没有所有节点只执行一次的分布式推理或all-to-all。

2400训练、500验证、700测试，域内[-1,1]^2；skewOOD把x0集中0.6–1。700steps，负载参数仅验证RMSE选；均匀与偏斜各自报告RMSE、专家最大占比与路由entropy。

## 失败不是删除

小型MoE可能比dense差，平衡改善entropy却不必改善任务误差。OOD偏移会使大部分样本进入同expert，负载是数据与路由共同产物，不能自动解释“专家语义分工”。实际Python CPU分发可能慢，本项目没有速度结论。

## 范围

这是Switch思想的独立top1门控实验，不是Switch Transformer网络、T5训练、trillion模型、capacity掉token或分布式通信。标准库/torch模块提供底层算子。演示选专家和权重可核对，不包装为SOTA MoE。
'''),
 'spec-decode':('SpecDecode-Lab｜greedy块验证与真实开销','https://arxiv.org/abs/2211.17192',r'''## 与原论文的区别

此项目只实现**确定性greedy推测解码**：draft逐token提出k个候选，target一次因果forward得到这些前缀对应的next-token logits；依次比较argmax，接受匹配，首个不匹配输出target token并丢弃后续draft；全部接受时可再加target bonus token。

不实现带概率接受率/残差重采样的distribution-preserving sampling，不声称任意采样温度下保持分布。原论文是参考机制，项目范围需明确。

## 精确性核心

causal mask保证批验证位置的logits不依赖其未来draft。首个不匹配后不使用错误上下文的后续logits。无KV cache、无dropout，greedy先后路径保持一致；仍需测试float numerics和tie情形，不声称跨硬件bitwise输出永远相同。

## 数据与模型

本项目重新训练target(d32、2heads)和draft(d16、2heads)，不是使用键值任务模型或外部LM。模8递推 $z_t=(z_{t-1}+z_{t-2})\bmod8$，64组初态48train/8validation/8test，序列后段可能重合，所以分集不用于泛化率宣称。监督所有prefix位置，target700steps、draft250steps。

4token prompt输出8token，test8个prompt，k2/k4各3次配对，先warmup，用perf_counter实际计时，包含draft和验证。保存每prompt耗时、calls和exact check；CPU tiny模型的dispatch/额外计算可能比baseline慢。

## 评价不能偷换

减少target forward次数不等于降低token级计算，也不一定低延迟。actual speed_ratio=baseline_ms/speculative_ms，低于1就是变慢，不能转换成“提升”。所有3次原始值保留，没有GPU throughput、并发负载或商业ROI。

相等是对齐target模型的生成路径，不是算术真值或文本质量。Demo原生执行两模型，可检查每块draft/target/accept；网页不重现后端计时，参考实测单列。
''')}

def main():
 guide=['# 前沿算法机制实验｜五项阅读地图','', '这些是2017–2023公开经典机制在当代大模型工程中的学习复现，不是2026最新论文榜单，也不是论文大规模性能复现。新增五个问题主线与独立代码目录；前三项共享TinyAttention基座明确披露，不能视为五个彼此独立数据集。共十三个项目，模块/基线不重复计数。','', '|作品|实际深度|核心边界|','|---|---|---|','|TinyAttention|因果多头/层归一/残差/训练、无注意力消融、长度OOD|单微型块查找仍有失败，不是自然语言预训练|','|LoRA-Lab|真实A/B低秩、冻结、rank、全量对照、合并parity、遗忘|小型基座共享，不是大模型/量化微调|','|DPO-Lab|真实DPO损失、reference、beta、SFT、win/top1/KL|规则单token偏好非人类对齐|','|SparseMoE|真实稀疏expert分发、门控梯度、负载辅助、dense对照|非Transformer或分布式MoE|','|SpecDecode|两模型真实训练、greedy块验证、exact path、actualCPU计时|非概率采样算法/商业加速|']
 for p,(title,url,method) in D.items():
  folder=ROOT/'projects'/p;r=json.loads((folder/'artifacts/results.json').read_text())
  (folder/'README.md').write_text(f'# {title}\n\n状态：实际CPU训练/运行的机制复现，AI辅助实现；不是论文性能复现或原创算法。\n\n[Demo](demo.html) · [原理与公式](METHOD.md) · [模型卡](MODEL_CARD.md) · [实测](artifacts/REPORT.md) · [逐样本证据](artifacts/results.json) · [参数](artifacts/model.json) · [哈希](artifacts/checksums.json)\n\n## 真实运行\n\n{r["protocol"]}\n\n## 重训\n\n先按requirements-frontier.txt安装CPU torch及numpy/sklearn；不包含GPU依赖或任何模型密钥。\n\n```bash\n.venv/bin/python projects/{p}/train.py\npython3 scripts/build_frontier_demos.py\n.venv/bin/python -m unittest discover -s tests -p test_frontier_projects.py -v\n```\n\nLoRA与DPO依赖tiny-attention/artifacts/model.json，需先训练TinyAttention；五项目结果齐全才能批量重建Demo。静态文件不需要安装torch，直接打开demo.html即可运行参数。PyTorchJSON为纯数字tensor，不用pickle加载不可信对象。\n\n## 个人贡献与参考\n\n用户选择扩充前沿算法，代码/文档/评测AI辅助完成；本人独立理解、改动、测试贡献待记录。不能作为过去论文/实习/生产项目。参考原论文：{url}。本批数字全部来自本仓库代码，不搬用论文结果。\n',encoding='utf-8')
  (folder/'METHOD.md').write_text('# '+title+'｜方法与可证伪范围\n\n'+method+'\n## 参考\n\n'+url+'\n\n## 运行证据\n\n[全部表](artifacts/REPORT.md)、[JSON](artifacts/results.json)留存分集/预测/损失/环境。模型结果与train.py、frontier_support.py哈希绑定，哈希只检测改动不是第三方真实性签名。修改共享基座后需重训所有依赖，不把旧评测重新打hash作为新实验。\n',encoding='utf-8')
  (folder/'MODEL_CARD.md').write_text('# '+title+'｜模型卡\n\n## 使用边界\n\n仅离线学习与实验复现。\n\n'+r['protocol']+'\n\n## 限制与风险\n\n'+'\n'.join('- '+l for l in r['limits'])+'\n\n## 输入和人机分工\n\n词表/数值输入需符合Demo声明，超过范围拒绝。输出是模型倾向，不保证语义正确；自定义输入无预设真值。全部张量在静态页面内联，无API/账号/密钥、无数据外发。\n\n## 贡献与证据\n\nAI辅助生成，个人独立贡献待记录；非本人已完成论文/工作或生产成果。原研究版权/引用单列，库许可证独立适用，仓库尚未统一授予开源许可证。\n',encoding='utf-8')
  guide+=['','## '+title,'',r['protocol'],'',f'[Demo](../projects/{p}/demo.html) · [原理](../projects/{p}/METHOD.md) · [报告](../projects/{p}/artifacts/REPORT.md)','', '|'+ '|'.join(r['metrics'][0])+'|','|'+ '|'.join(['---']*len(r['metrics'][0]))+'|']
  for row in r['metrics']:guide.append('|'+ '|'.join(f'{v:.5f}' if isinstance(v,float) else str(v) for v in row.values())+'|')
  guide+=['', '原论文：'+url]
 guide+=['','## 不利结果必须留下','', '- 微型单块attention没有可靠解决完整绑定任务，长度OOD显著差。','- LoRA学新规则同时丢失旧规则，低rank不等于没有遗忘。','- DPO pair win提升不等于chosen top1正确，KL/旧任务冲突需分别看。','- MoE在小型任务上不必超过dense，平衡不等于语义分工或速度。','- 推测解码减少target calls但可能CPU更慢，真实3次计时全保留。','', '后续本人深度贡献：重跑一项、手算一个forward/梯度、改变明确训练条件并预先冻结验证协议，解释一条失败后才填写“本人实现”。不盲目靠数量代替能力。前沿不是标题，重点是实现和可核验边界。GitHub新版发布尚未核验，真实远程LLM未调用。']
 (ROOT/'docs/frontier-evidence.md').write_text('\n'.join(guide)+'\n',encoding='utf-8');print('Documented5 frontier experiments')
if __name__=='__main__':main()
