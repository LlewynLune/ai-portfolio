"""Integrate per-project study links without changing homepage visual or frozen evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build():
 idx=json.loads((ROOT/'docs/investigations-index.json').read_text());lines=['# 每个项目深入到具体研究问题','', '本轮14研究工程项目全部完成一项专项调查，4业务案例深化产品取舍与建议验收。不是新项目数量或统一准确率。', '', '|项目|本轮研究问题|完整条件|阅读入口|','|---|---|---:|---|']
 for d in idx:
  folder=d['project'];p=ROOT/'projects'/folder
  lines.append(f'|{folder}|{d["question"]}|{d["metric_conditions"]}|[深研页](../projects/{folder}/deep-study.html) / [实测报告](../projects/{folder}/artifacts/investigation/REPORT.md) / [讨论](../projects/{folder}/artifacts/investigation/DISCUSSION.md)|')
  readme=p/'README.md';text=readme.read_text();marker='<!-- investigation-link -->'
  if marker not in text:
   addition='\n\n'+marker+'\n## 本轮专项深入研究\n\n'+d['question']+'\n\n[Deep Investigation](https://llewynlune.github.io/ai-portfolio/projects/'+folder+'/deep-study.html) · [全部实测条件](artifacts/investigation/REPORT.md) · [结果讨论与未完成项](artifacts/investigation/DISCUSSION.md) · [原始证据](artifacts/investigation/results.json)\n\n'+d['observations'][0]+'\n\n原模型、旧Depth和CiteRAG记忆证据保持冻结。新调查按各自协议区分训练、推断、合成仿真和历史再分析，不能以记录数证明泛化。\n'
   readme.write_text(text+addition)
 lines+=['', '## 关键深化而非数据规模','', '- DPO：3种子×SFT与两beta，9次真实NumPy输出头训练；基座冻结。梯度独立有限差分测试，训练/验证/测试由新合成前缀划分。','- SpecDecode：16上下文每个1000抽样，解析接受＋修正分布恒等式验证；另64四token轨迹。不宣称多token并行或加速。','- FlowBench：18次真实子进程退出，加36受控异步期限负载运行；不是生产事故或LLM实验。','- CiteRAG：8新namespace48题，两策略96问答＋1预热。旧521调用单独保留；累计618真实本地调用仍来自有限已知设置语法。','', '## 4业务案例','', '业务深化说明已有产品取舍、建议指标定义、建议验收和原始证据缺口，不新增未经提供的实现或历史指标。']
 for c in json.loads((ROOT/'profile/resume.json').read_text())['cases']:lines.append('- ['+c['title']+'](../business-cases/'+c['id']+'/case.html) / [产品分析](../business-cases/'+c['id']+'/PRODUCT_ANALYSIS.md)。')
 lines+=['', '## 验证与复现','', '在独立仓库副本运行 scripts/run_investigations.py，模型只在CiteRAG需要。原输出目录已存在时拒绝覆盖；不要删除历史证据替换为更好结果。核心依赖requirements-depth.txt，本地LLM依赖requirements-local-llm.txt。', '', '新专项测试 tests/test_investigations.py 检查：冻结hash、独立DPO梯度、隐藏状态导出、采样恒等式、容量、真实崩溃、prequential无当前真值泄漏、流式前缀与新题隔离。测试通过不代表模型泛化或履历真实性。', '', '## 仍未做的工作','', '各项目的Next Uncompleted Work已逐项明确。没有自然视频/真实设备/真人偏好/多日Agent/生产收益；不自动训练更大模型或宣称SOTA。']
 (ROOT/'docs/individual-investigations.md').write_text('\n'.join(lines)+'\n')
 print('linked',len(idx),'project READMEs')
if __name__=='__main__':build()
