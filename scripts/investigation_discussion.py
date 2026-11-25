"""Evidence-led findings. Original result payloads stay frozen, analysis separate."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NEXT={
 'textguard':'后续用独立时间/语言来源评测真实概念漂移；不能只重加权旧标签。',
 'novelty-lab':'后续增大正常校准集并用新分布正常样本检验误报；当前12验证过少。',
 'vision-cal':'后续做按writer隔离和新设备数据；同数字数据集的交换性条件不能推到OCR。',
 'tiny-attention':'下一阶段先修复或重训查询相关性，再检验未见结构；当前无关值敏感是关键失败。',
 'lora-lab':'下一阶段每层组合分别训练而非屏蔽既有adapter，以分辨训练交互。',
 'dpo-lab':'下一阶段增加非规则偏好并独立标注；冻结输出头无法代表全模型RLHF。',
 'moe-lab':'下一阶段引入明确公平性/优先级分发，并在真实GPU测路由开销。',
 'spec-decode':'下一阶段真正多token随机验证与KV回滚，并用目标/draft的wall-clock比较，不只算调用。',
 'circuit-id':'下一阶段用独立采集、仪器噪声和未知多时间常数验证，不控制设备。',
 'channel-est':'下一阶段未知tap阶数选择与独立场景仿真；实际硬件需单独授权与测量。',
 'power-scope':'下一阶段用公开实测负荷并重新冻结时序分割；区间更新不解决点预测漂移。',
 'video-guard':'下一阶段获取可公开许可的自然视频和独立音画标注；当前只重分析合成轨迹。',
 'reliability-lab':'下一阶段跨进程并发与模拟外部服务协议，不把SQLite幂等当分布式exactly-once。',
 'cite-rag':'下一阶段独立人工审核自然语言任务与多模型对照；新ID不等于新语义分布。'}
def build():
 summary=[]
 for p in sorted((ROOT/'projects').glob('*/artifacts/investigation/results.json')):
  d=json.loads(p.read_text());name=d['project'];m=d['metrics'];find=[]
  if name=='tiny-attention':find.append('无关值改动导致的输出翻转均值 {:.1%}；相关值改动后正确率 {:.1%}。模型并未稳定学到查询相关性。'.format(sum(x['output_flip'] for x in m if x['intervention']=='irrelevant_value_change')/3,sum(x['intervened_accuracy'] for x in m if x['intervention']=='query_value_change')/3))
  if name=='dpo-lab':
   for policy in ['sft','dpo_0.1','dpo_0.5']:
    rr=[x for x in m if x['policy']==policy];find.append(policy+'：三种子平均pair win {:.1%}，chosen top1 {:.1%}，原规则保留 {:.1%}。'.format(sum(x['test_pair_win'] for x in rr)/3,sum(x['test_chosen_top1'] for x in rr)/3,sum(x['original_retention'] for x in rr)/3))
  if name=='vision-cal':
   find.append('校准集合与先前温度选择共用359条validation：模型并非独立于这些校准标签，因此即使干净集也不能声称严格split-conformal有限样本覆盖保证；这里只报告经验覆盖。')
   for x in m:
    if x['alpha']==.1:find.append(x['condition']+'：名义90%集合实际覆盖 {:.1%}，平均集合大小 {:.3f}。'.format(x['coverage'],x['mean_set_size']))
  if name=='circuit-id':
   rr=[x for x in m if x['tau_ms']==12 and x['noise']==.08];find+=['tau12ms噪声0.08，观察窗{}ms：MAE {:.3f}ms，启发式profile宽度 {:.3f}ms。'.format(x['horizon_ms'],x['mae_ms'],x['mean_profile_width_ms']) for x in rr]
  if name=='channel-est':
   rr=[x for x in m if x['actual_taps']==4 and x['method']=='4tap_ls'];find+=['4tap {}：条件数 {:.2f}，NMSE {:.4f}。'.format(x['geometry'],x['condition_number'],x['mean_nmse']) for x in rr]
  if name=='power-scope':find+=['{} {}：覆盖 {:.1%}、区间宽 {:.1f}kW、点预测MAE {:.1f}kW。'.format(x['condition'],x['method'],x['coverage'],x['mean_width_kw'],x['mae_kw']) for x in m]
  if name=='reliability-lab':
   rr=[r for r in d['records'] if r.get('kind')=='abrupt_exit'];find.append('18次真实进程退出恢复：retry重复副作用{}次，resilient {}次；仅局部SQLite边界。'.format(sum(x['duplicate_effects'] for x in rr if x['strategy']=='retry'),sum(x['duplicate_effects'] for x in rr if x['strategy']=='resilient')))
  if name=='cite-rag':find+=['{}：严格通过{}/{}，解析失败{}；最终拒答可能被guard纠正，不等于原始生成正确。'.format(x['mode'],x['correct'],x['n'],x['parse_failures']) for x in m]
  if name=='spec-decode':find.append('16上下文解析分布恒等式最大误差 {:.2e}；1000抽样经验TV最大 {:.4f}。没有做速度收益测量。'.format(max(x['analytic_max_error'] for x in m),max(x['total_variation'] for x in m)))
  if not find:find=d['findings'][:2]
  analysis={'project':name,'results_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'observations':find,'next_step':NEXT[name],'not_completed':NEXT[name],'no_best_condition_selected':True}
  (p.parent/'analysis.json').write_text(json.dumps(analysis,ensure_ascii=False,indent=2)+'\n')
  # Add a separate report, never replace original result payload.
  (p.parent/'DISCUSSION.md').write_text('# '+d['title']+'：结果讨论\n\n'+'\n\n'.join(find)+'\n\n## 仍未完成的下一阶段\n\n'+NEXT[name]+'\n\n[原始结果](results.json) · [实验协议与方法](REPORT.md)\n')
  summary.append({'project':name,'title':d['title'],'question':d['question'],'record_count':len(d['records']),'metric_conditions':len(m),'observations':find,'next_step':NEXT[name]})
 (ROOT/'docs/investigations-index.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print('discussions',len(summary))
if __name__=='__main__':build()
