"""Aggregate frozen runs with denominator, parsing and paired-effect checks."""
import json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from memory_agent.ask import deterministic_reference
from memory_agent.evaluate import score

def readlines(path):return [json.loads(s) for s in path.read_text().splitlines()]
def aggregate(rows):
 n=len(rows);good=sum(r['score']['correct'] for r in rows)
 return {'n':n,'correct':good,'accuracy':good/n if n else None,'parse_failures':sum(r['parsed'] is None for r in rows),
  'abstentions':sum(bool(r['final'] and r['final']['status']=='abstain') for r in rows),'verifier_failures':sum(not r['verifier_pass'] for r in rows),
  'wrong_final_answers':sum(r['score']['wrong_answer'] for r in rows),'mean_prompt_tokens':statistics.mean(r['call']['prompt_tokens'] for r in rows) if rows else None,
  'mean_seconds':statistics.mean(r['call']['elapsed_seconds'] for r in rows) if rows else None,'p50_seconds':statistics.median(r['call']['elapsed_seconds'] for r in rows) if rows else None,
  'max_gpu_bytes':max((r['call']['peak_gpu_memory_bytes'] for r in rows),default=0)}
def build():
 dest=ROOT/'artifacts/memory';primary=readlines(dest/'run-primary/runs.jsonl');challenges=readlines(dest/'run-challenges/challenges.jsonl');budgets=readlines(dest/'run-challenges/budgets.jsonl')
 data=json.loads((ROOT/'data/memory/episodes.json').read_text());provenance=json.loads((dest/'run-primary/provenance.json').read_text());challenge_prov=json.loads((dest/'run-challenges/provenance.json').read_text())
 metrics=[]
 for split in ('development','evaluation'):
  for mode in ('raw_window','source_rag','model_memory','verified_replay'):
   rows=[r for r in primary if r['split']==split and r['mode']==mode];metrics.append(dict(split=split,mode=mode,**aggregate(rows)))
 cmetrics=[dict(mode=m,**aggregate([r for r in challenges if r['mode']==m])) for m in ('unverified_notes','source_replay')]
 bmetrics=[dict(budget=b,mode=m,**aggregate([r for r in budgets if r['mode']==m and r['budget']==b])) for b in (160,400,800) for m in ('source_rag','verified_replay')]
 reference=[]
 for q in data['queries']:
  if q['split']=='evaluation':reference.append({'id':q['id'],'prediction':deterministic_reference(data['sources'],q['namespace'],q['key']),'score':score(deterministic_reference(data['sources'],q['namespace'],q['key']),q)})
 v2=readlines(dest/'run-v2/runs.jsonl');v2_prov=json.loads((dest/'run-v2/provenance.json').read_text())
 v2metrics=[dict(budget=b,mode='release_guard_v2',normalized_integers=sum(r['normalized_integer'] for r in v2 if r['budget']==b),**aggregate([r for r in v2 if r['budget']==b])) for b in (160,400,1600)]
 summary={'project':'CiteRAG / Source-backed Agent Memory','v2_exploratory':v2metrics,'primary':metrics,'challenges':cmetrics,'budgets':bmetrics,'deterministic_reference':{'n':len(reference),'correct':sum(r['score']['correct'] for r in reference),'llm_used':False,'scope':'reads all current source records using the SAME known setting grammar, an appropriate strong baseline for this artificial task'},
  'primary_calls':provenance['calls'],'challenge_calls':challenge_prov['calls'],'total_actual_llm_calls':provenance['calls']+challenge_prov['calls']+v2_prov['calls'],'v2_calls':v2_prov['calls'],
  'unique_queries':48,'heldout_queries':32,'primary_query_generations':192,'challenge_query_generations':32,'budget_query_generations':192,
  'limits':['synthetic shared template; not an independent natural-language benchmark','verified replay is source extraction, not model-only dreaming or parametric memory','primary memory vs replay scores equal','pure deterministic setting parser is stronger than LLM on this task','fixed string schema rejects correct numeric JSON outputs; no posthoc rescore','160-token budget can hide one conflicting record','no multi-day autonomous execution or cross-session learning gain evaluated','one 4bit model, one greedy run; no model comparisons or independent repetitions','latency excludes consolidation and loading; note construction amortization unspecified']}
 (dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (dest/'deterministic-reference.json').write_text(json.dumps(reference,indent=2)+'\n')
 lines=['# CiteRAG：真实本地大模型记忆工程实验','',
  '## 核心判断','',
  '不要把“模型写下的记忆”自动当作事实。本实验以来源回放、版本管理、显式拒答与输出契约检查来控制错误，但原始整理记忆与回放策略在主实验中同分。受控污染测试支持回放修复机制，不支持通用 Agent 能力、长期自主学习或生产效果结论。','',
  f'实际本地模型调用 {summary["total_actual_llm_calls"]} 次：主实验192问答＋6整理＋1预热；挑战32＋预算消融192＋1预热；v2独立保存96问答＋1预热。48个问题模板实例，其中32留出；512问答轨迹不是512个独立问题。公开4bit权重，离线推断，没有付费API。','',
  '## 主实验：结果不挑最佳','',
  '|集合|策略|正确/分母|严格通过率|类型/解析失败|校验失败|平均Prompt tokens|平均生成秒|','|---|---|---:|---:|---:|---:|---:|---:|']
 for m in metrics:lines.append(f'|{m["split"]}|{m["mode"]}|{m["correct"]}/{m["n"]}|{m["accuracy"]:.3f}|{m["parse_failures"]}|{m["verifier_failures"]}|{m["mean_prompt_tokens"]:.1f}|{m["mean_seconds"]:.3f}|')
 lines+=['','通过定义：状态、字符串值与引用集合同时正确。输出数字23而非字符串“23”是契约失败，即使数值运算正确也未计通过。原始输出保留，可区分数学能力与接口可靠性。平均生成时间不含模型加载或记忆整理，不能据此宣称端到端加速。','',
  '### 必须报告的强基线','',f'不调用模型、直接解析当前Setting记录的确定性基线通过 {summary["deterministic_reference"]["correct"]}/32。此有限规则任务可被传统代码完全解决；LLM不是必要条件。本作品验证上下文与生成契约，不主张模型优于规则。','',
  '## 污染记忆挑战：探索性测试','',
  '主实验结束后预先声明四种干预：旧版本、跨namespace、错误值与缺失证据。只改模型记忆，不改原始sources或答案标签。每种在4个留出namespace各1题，16配对 × 2策略 = 32真实生成。','',
  '|策略|通过/分母|解析失败|校验失败|','|---|---:|---:|---:|']
 for m in cmetrics:lines.append(f'|{m["mode"]}|{m["correct"]}/{m["n"]}|{m["parse_failures"]}|{m["verifier_failures"]}|')
 lines+=['','回放策略读取完整当前源记录，未校验策略只能依赖污染后的notes，信息可得性不同。这正是来源保留的产品价值，也意味着该对照不能证明LLM自身学会纠错。','',
  '## 上下文预算消融','',
  '|预算tokens|策略|通过/32|解析失败|校验失败|实际Prompt tokens均值|','|---:|---|---:|---:|---:|---:|']
 for m in bmetrics:lines.append(f'|{m["budget"]}|{m["mode"]}|{m["correct"]}/{m["n"]}|{m["parse_failures"]}|{m["verifier_failures"]}|{m["mean_prompt_tokens"]:.1f}|')
 lines+=['','预算仅限制evidence块，系统指令和问题有额外token。v1在160预算隐藏一条冲突源时曾错误放行4个答案。这个漏洞没有被高通过率掩盖；下方v2新增全源冲突检查与原子证据组。原始v1轨迹原样保留，校验拦截仍不等于任务成功。','',
  '## 工程验收与适用边界','',
  '- SQLite源ID不可变、幂等写入；notes按namespace独立替换，保存来源hash和原文引用；关闭后重开逐项验证。','- 追加hash链检查审计记录完整性；不是签名、访问鉴权或防恶意数据库篡改保证。','- 生成温度0、最大200输出tokens；整理最大1024；单次Prompt上限8192。未使用隐藏重试或自动选最优结果。','- 严格JSON解析、引用可见性、当前版本、撤销、冲突、精确单位、整数和双证据校验。有限Setting语法不是通用NLI。','- 模型整理与来源重建分开记录；旧artifacts的llm_used=false保留，只有新真实调用为true。','',
  '## 可复核文件','',
  '- [summary.json](summary.json)：全条件汇总。','- [主实验逐条输出](run-primary/runs.jsonl) / [模型整理及回放审计](run-primary/consolidations.json) / [版本、权重hash和运行环境](run-primary/provenance.json)。','- [污染挑战](run-challenges/challenges.jsonl) / [预算消融](run-challenges/budgets.jsonl) / [挑战预声明协议](run-challenges/protocol.json)。','- [无模型强基线](deterministic-reference.json)。','',
  '## 不成立的宣传说法','',
  '不是Anthropic、Seed或Kimi旗舰复刻；没有原创论文、模型预训练、RL后训练、权重记忆、数日自主Agent运行、真人测试、线上业务收益或保密审计。合成规则不是实际电气规范。当前验收重点是可追溯来源、真实本地生成、受控消融与失败分析。']
 lines+=['','## v2：独立保存的探索性修复回归','', '已看过同模板问题的结果后改进，因此不是新的独立留出成绩。三项改动同时发生：全源冲突检查、同key证据原子分组、显式整数到字符串适配；收益不能单独归因到某项。原始数值输出与适配标识保留。','', '|预算tokens|通过/32|解析失败|校验失败|错误最终答案|整数适配次数|','|---:|---:|---:|---:|---:|---:|']
 for m in v2metrics:lines.append(f'|{m["budget"]}|{m["correct"]}/{m["n"]}|{m["parse_failures"]}|{m["verifier_failures"]}|{m["wrong_final_answers"]}|{m["normalized_integers"]}|')
 lines+=['','160预算仍无法完整容纳冲突/双源计算证据，只能拒答，8题未通过。400与1600预算在这批已见结构回归通过32/32；不称通用准确率或模型满分。','', '- [v2全部原始输出](run-v2/runs.jsonl) / [v2预声明协议](run-v2/protocol.json)。']
 (dest/'REPORT.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':build()
