"""Build public portfolio from owner-supplied resume; preserve research cards and visual language.
Business text originates only from profile/resume.json, never from internal sources.
No synthetic project screenshots or fabricated audit evidence.
"""
from pathlib import Path
import json,re,html
ROOT=Path(__file__).resolve().parents[1]
E=html.escape


def build():
    data=json.loads((ROOT/'profile/resume.json').read_text())
    old=(ROOT/'index.html').read_text()
    cards=re.findall(r'<article class="card" data-track="[^"]+">.*?</article>',old,re.S)
    research=[c for c in cards if 'projects/' in c and 'TEMPLATE /' not in c and not any(x in c for x in ['product-workflow','research-evaluation','infra-runtime','business-cases/'])]
    assert len(research)==13,len(research)
    style=re.search(r'<style>(.*?)</style>',old,re.S)[1]
    style+='''
.case-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin-top:26px}.case{background:#fff;border:1px solid var(--line);padding:28px;border-radius:8px}.case h3{font-size:25px;margin:10px 0}.case p{font-size:14px;color:var(--muted)}.case .role{font-size:13px;color:var(--green)}.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}.kpi{padding:15px 12px;background:var(--mint);border-radius:6px}.kpi strong{display:block;font-size:23px;line-height:1.3}.kpi span{font-size:11px;color:var(--muted)}.case-detail{padding:30px;border:1px solid var(--line);background:white;border-radius:8px;margin-top:20px;scroll-margin-top:20px}.case-detail h3{margin-top:0;font-size:28px}.modules{display:grid;grid-template-columns:1fr 1fr;gap:22px}.module h4{margin:0 0 8px;font-size:17px}.module p{margin:0;color:var(--muted);font-size:14px}.flow{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}.flow span{border:1px solid var(--line);padding:6px 10px;border-radius:5px;font-size:12px;color:var(--green)}.case-source{font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}.case-detail summary{cursor:pointer;font-size:14px;color:var(--green);margin:20px 0}details[open] summary{margin-bottom:20px}.skills{display:flex;gap:8px;flex-wrap:wrap}.skills span{font-size:12px;background:var(--mint);padding:5px 10px;border-radius:5px}.education-item{padding:20px 0;border-bottom:1px solid var(--line)}.education-item h3{font-size:18px;margin:0 0 5px}.education-item p{margin:4px 0}.source-banner{border-left:3px solid var(--green);padding:2px 16px;margin:24px 0;font-size:12px;color:var(--muted)}@media(max-width:780px){.case-grid,.modules{grid-template-columns:1fr}.kpis{grid-template-columns:1fr 1fr}.case,.case-detail{padding:22px}}
'''
    out=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         '<meta name="description" content="于跃｜Agent与AI产品作品集。AI审图、标准化评审、Skill与知识运营、AIGC内容实践，以及可复现研究实验。"><title>于跃｜Agent / AI 产品作品集</title><style>'+style+'</style></head><body>',
         '<header><a class="brand" href="#top">于跃 / AI Product Portfolio</a><nav aria-label="主导航"><a href="#projects">产品实践</a><a href="#experiments">研究实验</a><a href="#about">关于</a></nav></header><main class="wrap" id="top">',
         '<div class="hero"><div><div class="eyebrow">DOMAIN KNOWLEDGE · AGENT PRODUCT · DELIVERY</div><h1>把专业规则，<br>做成可用的 AI 产品。</h1><p>具备 AI 产品从 0—1 到上线试点的完整实践，擅长把高知识密度、强规则约束的业务流程拆解为可操作的产品模块。将专家经验沉淀为规则库、知识库与人工复核机制，让 AI 输出可追溯、可复算。</p><span class="badge">Agent / AI 产品 · 机电与电气工程背景</span><br><a class="button" href="#projects">查看产品实践</a> · <a href="#about">教育与能力</a></div>',
         '<aside class="note"><h2>产品定义 × 领域理解 × 落地判断</h2><ul><li>独立负责审核工作台、混合策略、权限和风险评分等功能设计。</li><li>推动产品上线 / 试点，关注真实使用数据与 Badcase。</li><li>用 Python、SQL 与 AI Coding 快速验证方案。</li></ul><p>四项实践分别标明业务使用、试点、团队公共资产与草稿交付；研究实验独立展示，不混作上线成果。</p></aside></div>',
         '<section id="projects"><div class="section-head"><h2>核心产品实践</h2><p>从规则拆解到上线 / 试点，再到公共能力沉淀。</p></div><div class="case-grid">']
    for i,c in enumerate(data['cases']):
        out.append(f'<article class="case"><div class="tag">0{i+1} / {E(c["category"])}</div><h3>{E(c["title"])}</h3><div class="role">{E(c["role"])}</div><span class="badge">{E(c["status"])}</span><p>{E(c["overview"])}</p><p><a href="#case-{c["id"]}" data-case="{c["id"]}">查看产品案例 →</a> · <a href="business-cases/{c["id"]}/README.md">案例文档</a></p></article>')
    out.append('</div><div class="source-banner">项目职责、上线 / 试点状态和业务指标依据本人提供并确认可公开的简历。未公开公司系统、客户材料或原始统计数据；页面不将简历指标称作本仓库独立审计结果。</div>')
    for c in data['cases']:
        out.append(f'<article class="case-detail" id="case-{c["id"]}"><div class="tag">PRODUCT CASE / {E(c["category"])}</div><h3>{E(c["title"])}</h3><div class="role">{E(c["role"])} · {E(c["status"])}</div><p>{E(c["problem"])}</p><div class="kpis">')
        for metric in c['metrics']:out.append(f'<div class="kpi"><strong>{E(metric["value"])}</strong><span>{E(metric["label"])}</span></div>')
        out.append('</div><details><summary>展开核心模块、产品决策与验证边界</summary><div class="modules">')
        for mod in c['modules']:out.append(f'<div class="module"><h4>{E(mod["title"])}</h4><p>{E(mod["text"])}</p></div>')
        out.append('</div><h4>产品流程 · 按简历职责整理</h4><div class="flow">')
        for step in c['flow']:out.append('<span>'+E(step)+'</span>')
        out.append('</div><h4>关键产品取舍</h4><ul>')
        for dec in c['decisions']:out.append('<li>'+E(dec)+'</li>')
        out.append('</ul><p class="case-source">'+E(c['evidence'])+'</p></details><p><a href="#projects">返回实践总览 ↑</a></p></article>')
    out.append('</section><section id="method"><div class="section-head"><h2>如何判断 AI 是否真正有效</h2><p>规则、模型与人工协作；让迭代有依据。</p></div><div class="steps">')
    for num,title,text in [('01','专业流程产品化','把图纸与标准拆成条目、适用范围、证据要求与责任边界，再组织为工作台、权限和状态流转。'),('02','判定与校验分层','规则与模型分级路由；要求理由和引用条款，证据不足或低置信时转人工复核，不让模型解释替代证据。'),('03','真实使用与 Badcase 迭代','关注命中率、误报率、人工打回率与结论采纳率；基于反馈持续迭代规则、Prompt、知识召回与评分量表。')]:
        out.append(f'<div class="step"><span class="num">{num}</span><h3>{title}</h3><p>{text}</p></div>')
    out.append('</div><p class="case-source">这些是我采用的产品验证视角；未在简历中提供的指标不补写结果，未明确统计口径的指标不外推为模型整体准确率。</p></section>')
    out.append('<section id="experiments"><div class="section-head"><h2>研究与工程实验</h2><p>14 项可复现实验，作为技术理解与验证能力的补充。</p></div><div class="note" style="margin-top:24px"><div class="tag">RESEARCH LAB / NOT BUSINESS DEPLOYMENT</div><h2>与真实产品实践分开展示</h2><p>以下实验由 AI 辅助搭建，代码、模型、日志、失败样本和贡献边界分别披露。本地模型 Demo 已可运行，真实大模型接口未调用；合成负载与仿真结果不等于生产业务效果。</p><p><a href="projects/reliability-lab/demo.html">FlowBench 可靠性实验台</a> · <a href="projects/reliability-lab/README.md">代码与复现</a> · <a href="projects/video-guard/demo.html">VideoGuard 深度研究</a> · <a href="docs/ai-evidence.md">实验真实性清单</a></p></div>')
    out.append('<div class="filters" role="group" aria-label="按实验方向筛选"><button type="button" data-filter="all" aria-pressed="true">全部实验</button><button type="button" data-filter="product" aria-pressed="false">检索应用</button><button type="button" data-filter="research" aria-pressed="false">算法研究</button><button type="button" data-filter="infra" aria-pressed="false">基础设施</button></div><div class="cards">')
    out.extend(research);out.append('</div></section>')
    out.append('<section id="about" class="split"><div><h2>关于我</h2><p>'+E(data['summary'])+'</p><div class="skills">')
    for skill in ['专业规则产品化','人机协同审核','Agent 工作流','权限与留痕','风险评分','Badcase 运营','Python','SQL','AI Coding']:out.append('<span>'+skill+'</span>')
    out.append('</div><p><a href="https://github.com/LlewynLune/ai-portfolio">GitHub 完整源码</a> · <a href="profile/README.md">个人介绍</a> · <a href="PUBLISHING.md">披露与证据边界</a></p></div><div><h2>教育经历</h2>')
    for edu in data['education']:
        out.append('<div class="education-item"><h3>'+E(edu['school'])+'</h3><p>'+E(edu['degree'])+' · '+E(edu['date'])+'</p>')
        if 'major' in edu:out.append('<p>'+E(edu['faculty']+' · '+edu['major'])+'</p><p>'+E(edu['lab'])+'</p><p>'+E(edu['student_leadership'])+'</p>')
        out.append('</div>')
    out.append('<p class="case-source">教育经历与项目信息由本人提供。硕士专业和入学日期未提供，不自动补写；导师与联系方式不公开展示。</p></div></section></main><footer class="wrap">真实产品实践依据本人简历 / 研究实验为 AI 辅助原型 / Python 实验仅本机运行 / 不公开内部系统、图纸或未授权素材</footer>')
    out.append('''<script>
const buttons=[...document.querySelectorAll('[data-filter]')],cards=[...document.querySelectorAll('[data-track]')];
buttons.forEach(button=>button.addEventListener('click',()=>{const filter=button.dataset.filter;buttons.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));cards.forEach(card=>{card.hidden=filter!=='all'&&card.dataset.track!==filter;})}));
function openCase(){let id=location.hash.slice(1);if(!id.startsWith('case-'))return;let target=document.getElementById(id);if(target){target.querySelector('details').open=true;}}
window.addEventListener('hashchange',openCase);openCase();
</script></body></html>''')
    (ROOT/'index.html').write_text('\n'.join(out))
    for c in data['cases']:
        folder=ROOT/'business-cases'/c['id'];folder.mkdir(parents=True,exist_ok=True)
        lines=['# '+c['title'],'',c['role']+'｜'+c['status'],'',c['overview'],'','## 场景与问题','',c['problem'],'','## 核心模块','']
        for mod in c['modules']:lines+=['### '+mod['title'],'',mod['text'],'']
        lines+=['## 产品流程','', ' → '.join(c['flow']),'','## 关键取舍','']+['- '+x for x in c['decisions']]
        lines+=['','## 结果与披露边界','',c['evidence'],'','本案例基于本人提供并确认可公开的履历。不是新生成的业务平台，不提供未经授权的内部源代码、截图、图纸或原始数据；不将学习实验作为真实项目演示。','', '[返回作品集](../../index.html#case-'+c['id']+')','']
        (folder/'README.md').write_text('\n'.join(lines))
    print('Built owner resume portfolio: 4 cases + 14 separate research projects')

if __name__=='__main__':build()
