"""Build actual project landing pages in one measured academic layout.
Tables are derived from frozen depth outputs, not invented metrics.
"""
from pathlib import Path
import json,html
from academic_project_style import PROJECTS,CSS,hero
ROOT=Path(__file__).resolve().parents[1]
E=html.escape
def fmt(v):
 if isinstance(v,float):return f'{v:.4f}' if abs(v)>=.0001 else f'{v:.3e}'
 return str(v)
def build():
 for folder,(name,en,zh,abstract,steps,protocol,report) in PROJECTS.items():
  p=ROOT/'projects'/folder;d=json.loads((p/'artifacts/depth/results.json').read_text())
  # One complete representative condition only; selected by sorted condition, never best score.
  condition=sorted({r['condition'] for r in d['metrics']})[0];rows=[r for r in d['metrics'] if r['condition']==condition]
  keys=['model','condition','n']+[k for k in ['accuracy','mae','rmse','mean_elapsed_ms','mean_nmse','admission_coverage','nll'] if any(k in r for r in rows)]
  heads={'model':'Model / Policy','condition':'Condition','n':'Records','accuracy':'Success / Correctness','mae':'MAE','rmse':'RMSE','mean_elapsed_ms':'Mean latency (ms)','mean_nmse':'NMSE','admission_coverage':'Admission coverage','nll':'NLL'}
  table='<div class="table-scroll"><table class="paper-table"><thead><tr>'+''.join('<th>'+heads[k]+'</th>' for k in keys)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(fmt(r.get(k,'—')))+'</td>' for k in keys)+'</tr>' for r in rows)+'</tbody></table></div>'
  page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(name)+' | '+E(en)+'</title><meta name="description" content="'+E(zh)+'"><style>'+CSS+'</style></head><body>'+hero(folder)+'''<main>
<section class="project-section narrow" id="introduction"><h2>Introduction</h2><p class="abstract">'''+E(abstract)+'''</p></section>
<section class="project-section" id="overview"><h2>Overview</h2><figure class="figure"><a href="../../assets/portfolio/'''+folder+'''-evidence.svg"><img src="../../assets/portfolio/'''+folder+'''-evidence.svg" width="800" height="480" alt="'''+E(name)+'''冻结实验报告重绘"></a><figcaption>原始冻结报告的代表性结果；不是论文作者结果或系统截图。点击查看完整矢量图。</figcaption></figure></section>
<section class="project-section narrow" id="method"><h2>Method</h2><div class="method-steps">'''+''.join('<div><small>0'+str(i+1)+'</small>'+E(t)+'</div>' for i,t in enumerate(steps))+'''</div><p>'''+E(protocol)+'''</p><p class="caption">方法与模型代码、训练协议、适用边界分别保留在项目文档中。此处为公开说明，不代替完整复现步骤。</p><p class="section-links"><a href="https://github.com/LlewynLune/ai-portfolio/tree/main/projects/'''+folder+'''">Implementation &amp; Protocol →</a></p></section>
<section class="project-section" id="results"><h2>Experimental Results</h2><p>深化批次的一个完整条件对照如下。条件按名称顺序取首项，不按最好分数挑选；全部条件、失败与逐条记录在 Depth Study 中可复查。</p>'''+table+'''<p class="caption">Condition: '''+E(condition)+'''。表格数值直接读取 artifacts/depth/results.json；记录包含相关扰动、重复计时或历史再分析，不等于独立样本规模。不同项目的 Success / Correctness 定义不同，不能横向当作统一准确率。完整实验协议：'''+E(d['protocol'])+'''</p><p class="section-links"><a class="resource" href="depth-demo.html">'''+__import__('academic_project_style').icon('report')+'''Full Results / Depth Study</a></p></section>
<section class="project-section narrow" id="demo"><h2>Interactive Demo</h2><p>浏览器执行已导出的模型参数或显示真实本地运行记录。自定义输入没有预设真值，不重训、不调用远程大模型，也不操作设备。</p><p class="section-links"><a class="resource" href="demo.html">'''+__import__('academic_project_style').icon('demo')+'''Open Demo</a></p></section>
<section class="project-section narrow" id="limitations"><h2>Limitations &amp; Reproducibility</h2><p>'''+E(protocol)+''' 实验为 AI 辅助实现，本人独立理解、修改和复核贡献如实记录。模型名称、机制复现和静态发布不代表原创论文或生产能力。</p><p><a href="https://github.com/LlewynLune/ai-portfolio/blob/main/projects/'''+folder+'''/README.md">README / Reproduction</a> · <a href="https://github.com/LlewynLune/ai-portfolio/blob/main/projects/'''+folder+'''/artifacts/depth/results.json">Frozen evidence</a></p></section></main><footer class="project-footer">Yu Yue / Personal AI Research &amp; Engineering<br>个人实验 · AI 辅助实现 · 合成 / 仿真 / 公开数据 / 历史再分析性质按项目说明<br><a href="../../index.html#experiments">Portfolio</a><a href="https://github.com/LlewynLune/ai-portfolio">Repository</a></footer></body></html>'''
  page=page.replace('<main>','<main><div class="section-links"><a class="resource" href="deep-study.html">Deep Investigation / 本轮专项研究</a></div>',1)
  (p/'project.html').write_text(page);print('Academic project',folder)
 # Preserve the single project's new real-model evidence landing page after generic build.
 from build_memory_demo import build as build_memory
 build_memory()
if __name__=='__main__':build()
