"""Build a self-contained, understated scientific evidence viewer, not live LLM UI."""
import sys,json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from academic_project_style import CSS,icon
E=html.escape
P=ROOT/'projects/cite-rag';A=P/'artifacts/memory'
def table(rows,fields):
 return '<div class="table-scroll"><table class="paper-table"><thead><tr>'+''.join('<th>'+E(k)+'</th>' for k in fields)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(f'{r[k]:.3f}' if isinstance(r[k],float) else str(r.get(k,'—')))+'</td>' for k in fields)+'</tr>' for r in rows)+'</tbody></table></div>'
def build():
 s=json.loads((A/'summary.json').read_text());d=json.loads((P/'data/memory/episodes.json').read_text());rows=[]
 for phase,path in [('Primary','run-primary/runs.jsonl'),('Memory challenge','run-challenges/challenges.jsonl'),('Budget ablation','run-challenges/budgets.jsonl'),('V2 regression','run-v2/runs.jsonl')]:
  for line in (A/path).read_text().splitlines():
   r=json.loads(line);r['phase']=phase;rows.append(r)
 hero='<nav class="project-top"><a href="../../index.html#experiments">← Yu Yue / Portfolio</a><a href="memory-demo.html">Evidence Viewer</a></nav><header class="publication-header"><h1 class="publication-title">CiteRAG</h1><h2 class="publication-subtitle">Source-backed Agent Memory</h2><div class="publication-authors"><a href="../../index.html#about">Yu Yue（于跃）</a></div><p class="publication-affiliation">Versioned Evidence · Context Budgets · Local LLM</p><p class="publication-note">AI 辅助实现 · 本地可复现实验 · 非论文发表或生产项目</p><div class="publication-links">'+''.join('<a class="resource" href="'+url+'">'+icon(k)+name+'</a>' for k,name,url in [('code','Code','https://github.com/LlewynLune/ai-portfolio/tree/main/projects/cite-rag/memory_agent'),('report','Report','artifacts/memory/REPORT.md'),('data','Evidence','memory-demo.html'),('report','Protocol','MEMORY_METHOD.md'),('demo','Run locally','LOCAL_LLM.md')])+'</div></header>'
 def sec(id,title,body,narrow=False):return '<section id="'+id+'" class="project-section'+(' narrow' if narrow else '')+'"><h2>'+title+'</h2>'+body+'</section>'
 body=sec('introduction','Introduction','<p class="abstract">模型能写下一条记忆，不意味着这条记忆仍然正确。CiteRAG 从引用优先检索深化到来源支持的跨任务记忆：记录修订与撤销，回放原文检查笔记，在有限上下文中保留冲突证据，并让真实本地大模型输出可验证的结构化结论。</p><p>本作品关注产品与工程判断，而非堆叠功能：独立校验、传统强基线、预算消融、失败留痕与可复现运行。所有数据都是自建虚构软件设置，不使用公司材料。</p>',True)
 body+=sec('overview','Overview','<div class="method-steps">'+''.join('<div><small>0'+str(i+1)+'</small>'+t+'</div>' for i,t in enumerate(['版本化来源','模型记忆整理','原文回放校验','生成与独立验证']))+'</div><p>来源事件 → 不可变ID与namespace → 模型notes → 原文支持 / 修订 / 撤销 / 冲突检查 → token预算下证据装入 → 本地模型生成 → 输出契约与全源校验 → 答案或拒答。</p><p class="caption">来源回放重建是确定性抽取，不冒充LLM自主学习。当前SQLite验证持久化和隔离，不等于多租户鉴权或恶意攻击防护。</p>')
 body+=sec('method','Method','<p>主实验在推断前冻结78条源记录和48个问题，16开发、32留出；比较原始上下文、来源检索、模型笔记与来源回放四策略。每次生成记录Prompt hash、模型版本、真实token、GPU峰值、原始文本与校验结果。</p><p>后续污染挑战和预算实验分别保存。小预算暴露v1冲突漏洞后，v2加入全源冲突检查、证据原子分组和整数类型适配；它是探索性修复回归，不是新的独立留出。</p>',True)
 body+=sec('results','Experimental Results','<p>主实验留出结果如下，状态、字符串值和引用集合必须同时正确。原始失败不回填修复后结果。</p>'+table([r for r in s['primary'] if r['split']=='evaluation'],['mode','n','correct','accuracy','parse_failures','mean_prompt_tokens','mean_seconds'])+'<p class="caption">平均生成秒不含加载或整理开销。原始模型记忆与回放同分；确定性Setting解析器通过32/32，说明该有限规则任务不需要LLM。本作品不宣称模型优于规则。</p><h3>Memory corruption challenge</h3>'+table(s['challenges'],['mode','n','correct','verifier_failures','wrong_final_answers'])+'<p class="caption">旧版本、跨namespace、错值和缺失笔记，16配对。回放拥有完整源记录，未校验notes没有，因此不是等信息量的模型智能对照。</p><h3>Context budget ablation</h3>'+table(s['budgets'],['budget','mode','n','correct','parse_failures','wrong_final_answers'])+'<p class="caption">更多上下文不保证更好。v1的160预算隐藏一条冲突源时错误放行4个答案，已保留并修复。</p><h3>V2 exploratory regression</h3>'+table(s['v2_exploratory'],['budget','n','correct','parse_failures','wrong_final_answers','normalized_integers'])+'<p class="caption">三项改动同时发生，不能单独归因。400/1600预算通过32/32仅限已见结构回归；160预算仍有8题证据不足，只能拒答。</p>')
 body+=sec('demo','Interactive Demo','<p>证据浏览器可筛选全部真实生成，查看原文、模型输出、引用、失败原因、v1/v2差异与上下文预算。网页不运行完整大模型；自定义真实生成请用本地CLI。</p><p class="section-links"><a class="resource" href="memory-demo.html">'+icon('data')+'Open Evidence Viewer</a></p><p class="section-links"><a href="demo.html">早期检索 Demo</a> · <a href="depth-demo.html">历史去重研究</a> · <a href="LOCAL_LLM.md">本地模型运行</a></p>',True)
 condition=sorted({r['condition'] for r in json.loads((P/'artifacts/depth/results.json').read_text())['metrics']})[0]
 body+=sec('limitations','Limitations &amp; Reproducibility','<p>一次4bit本地模型运行、共享模板自建数据。521实际模型调用含512问答、6次整理和3次预热；重复策略、挑战和回归不是521个独立样本。没有自然语言NLI、权重记忆、RL、多日自主任务、真人评测、真实电气规范或线上收益。</p><p>实验由AI辅助实现，不包装为本人既往独立研发、论文或公司项目。内部检索只作选题参考，公开代码、Prompt和数据不含内部内容。</p><details><summary>历史证据保持冻结</summary><p>早期检索与内容去重报告仍保留：'+E(condition)+'。旧报告llm_used=false没有改写，新真实LLM结果单独存放。</p></details>',True)
 footer='<footer class="project-footer">Yu Yue / Personal AI Research &amp; Engineering<br><a href="MEMORY_METHOD.md">Method &amp; public sources</a> · <a href="artifacts/memory/REPORT.md">Full report</a></footer>'
 def shell(title,content):
  import re
  page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><style>'+CSS+EXTRA+'</style></head><body>'+hero+'<main>'+content+'</main>'+footer+'</body></html>'
  # Pages does not guarantee direct Markdown rendering; open documentation in GitHub.
  return re.sub(r'href="([^"/:]+(?:/[^"/:]+)*\.md)"',lambda m:'href="https://github.com/LlewynLune/ai-portfolio/blob/main/projects/cite-rag/'+m[1]+'"',page)
 body='<div class="section-links"><a class="resource" href="deep-study.html">New Namespace Investigation</a></div>'+body
 (P/'project.html').write_text(shell('CiteRAG | Source-backed Agent Memory',body))
 controls='<section class="project-section" id="inspector"><h2>Evidence Viewer</h2><p>真实本地推断证据回放，非在线模型聊天。选择记录检查完整过程；未进行页面内生成。</p><div class="controls"><label>实验阶段<select id="phase"></select></label><label>策略<select id="mode"></select></label><label>结果<select id="result"><option value="all">全部</option><option value="fail">仅失败</option><option value="pass">仅通过</option></select></label><label>问题／条件<select id="record"></select></label></div><p id="count" class="caption" aria-live="polite"></p><div id="evidence"></div><p><button id="export">导出当前真实记录 JSON</button></p></section>'
 payload=json.dumps({'rows':rows,'sources':d['sources']},ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')
 js='''<script>const DATA='''+payload+''';
 const $=id=>document.getElementById(id),uniq=x=>[...new Set(x)],esc=x=>String(x??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));let filtered=[],selected=null;
 function opts(el,values){el.innerHTML=values.map(v=>'<option>'+esc(v)+'</option>').join('')}
 opts($('phase'),uniq(DATA.rows.map(r=>r.phase)));
 function modes(){opts($('mode'),['全部',...uniq(DATA.rows.filter(r=>r.phase===$('phase').value).map(r=>r.mode))]);filter()}
 function filter(){filtered=DATA.rows.filter(r=>r.phase===$('phase').value&&($('mode').value==='全部'||r.mode===$('mode').value)&&($('result').value==='all'||r.score.correct===($('result').value==='pass')));$('record').innerHTML=filtered.map((r,i)=>'<option value="'+i+'">'+esc(r.id+' / '+r.mode+' / '+(r.budget??r.kind??'1600'))+'</option>').join('');$('count').textContent=filtered.length+'条真实记录；同问题多策略不是独立样本。';render()}
 function render(){selected=filtered[Number($('record').value)];if(!selected){$('evidence').textContent='没有匹配记录。';return}const r=selected;
 let t='<h3>'+esc(r.id)+'</h3><p><b>'+esc(r.score.correct?'严格通过':'未通过')+'</b> · '+esc(r.phase)+' · '+esc(r.mode)+' · 校验：'+esc(r.verifier_reason)+'</p>';
 t+='<p class="caption">Prompt '+r.call.prompt_tokens+' tokens · 输出 '+r.call.completion_tokens+' tokens · '+r.call.elapsed_seconds.toFixed(3)+' 秒 · 本地GPU峰值 '+(r.call.peak_gpu_memory_bytes/1e9).toFixed(3)+' GB。计时不含加载/整理。</p>';
 t+='<h3>原始模型输出</h3><pre>'+esc(r.call.text)+'</pre><h3>最终结构与适配</h3><pre>'+esc(JSON.stringify({parsed:r.parsed,parse_error:r.parse_error,normalized_integer:r.normalized_integer??false,final:r.final},null,2))+'</pre><h3>实际模型上下文</h3>';
 (r.context||[]).forEach(x=>{t+='<details><summary>'+esc(x.id??x.key)+' · '+esc(x.value??x.state??'source')+'</summary><pre>'+esc(JSON.stringify(x,null,2))+'</pre></details>'});
 const ids=uniq((r.context||[]).flatMap(x=>x.source_ids??[x.id]).filter(Boolean));t+='<h3>引用来源原文</h3>';
 DATA.sources.filter(x=>ids.includes(x.id)).forEach(x=>{t+='<p><b>'+esc(x.id)+'</b> · '+esc(x.namespace)+' / Revision '+x.revision+' / '+esc(x.state)+'</p><blockquote>'+esc(x.text)+'</blockquote>'});
 if(r.audit)t+='<details><summary>记忆回放审计</summary><pre>'+esc(JSON.stringify(r.audit,null,2))+'</pre></details>';t+='<details><summary>完整证据与哈希</summary><pre>'+esc(JSON.stringify(r,null,2))+'</pre></details>';$('evidence').innerHTML=t}
 $('phase').onchange=modes;$('mode').onchange=filter;$('result').onchange=filter;$('record').onchange=render;
 $('export').onclick=()=>{if(!selected)return;const u=URL.createObjectURL(new Blob([JSON.stringify(selected,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=u;a.download=selected.id+'-'+selected.mode+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};modes();</script>'''
 (P/'memory-demo.html').write_text(shell('CiteRAG | Real LLM Evidence Viewer',controls+js))
 print('built project and evidence viewer',len(rows),'real query records')
EXTRA='''pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#fafafa;border:1px solid #ddd;padding:16px;font:13px/1.65 ui-monospace,monospace;max-height:520px;overflow:auto}blockquote{margin:16px 0;padding:12px 20px;border-left:3px solid #999;line-height:1.7;background:#fafafa}details{border-top:1px solid #ddd;padding:14px 0}summary{cursor:pointer}.controls{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:24px 0}label{font-size:14px;color:#666}select{display:block;width:100%;padding:9px;margin-top:8px;border:1px solid #bbb;background:white;border-radius:0}button{background:#363636;color:white;border:0;padding:10px 20px}#evidence{margin-top:32px}@media(max-width:600px){.controls{grid-template-columns:1fr}.publication-title{font-size:38px}pre{font-size:12px}}'''
if __name__=='__main__':build()
