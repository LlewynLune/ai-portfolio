"""Personal portfolio, one academic-homepage reference and owner-specific content.
All CSS and markup authored here. No borrowed identity/photo/honors or source code.
Owner business facts: resume.json; AI-assisted experiments: explicit contributions.
Deterministic rebuild; never rewrites frozen experiment evidence.
"""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1]
E=html.escape
STYLE='''
:root{--text:#494e52;--blue:#224b8d;--line:#f0f1f2;--tag:#001a77}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:78px}body{margin:0;background:#fff;color:var(--text);font-family:"Trebuchet MS",Helvetica,"PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.5}a{color:var(--blue);text-decoration:underline;text-underline-offset:2px}a:hover{color:#062b64}a:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid var(--blue);outline-offset:3px}.masthead{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line)}.nav-inner{max-width:1200px;margin:auto;padding:17px 18px;display:flex;gap:34px;align-items:center}.navlinks{display:flex;gap:31px;align-items:center}.navlinks a,.brand{text-decoration:none;color:#7a8288;font-weight:700;font-size:15px}.brand{color:var(--text)}.navlinks a.active{color:var(--blue)}.layout{max-width:1200px;padding:35px 18px 30px;margin:auto;display:grid;grid-template-columns:205px minmax(0,1fr);gap:40px}.identity{align-self:start;position:sticky;top:103px}.identity h1{font-size:21px;line-height:1.25;margin:0 0 8px;font-weight:700}.identity p{font-size:15px;line-height:1.5;margin:6px 0}.identity .sub{font-size:13px;color:#7a8288}.identity-links{display:flex;gap:14px;margin:17px 0;font-size:14px}.identity-note{margin-top:22px;font-size:12px;color:#7a8288;line-height:1.7}.content{min-width:0;max-width:860px}.section{margin:0 0 34px;scroll-margin-top:85px}.section h2{font-size:24px;line-height:1.4;margin:0 0 18px;padding-bottom:7px;border-bottom:1px solid var(--line);font-weight:700}.section h3{font-size:20px;margin:24px 0 12px;line-height:1.4}.section p{margin:0 0 13px}.bio p{line-height:1.65}.section-note{font-size:13px;color:#7a8288}.focus-list{margin:0;padding-left:22px;line-height:1.7}.focus-list li{margin-bottom:7px}.works,.experiments{margin:0;padding-left:22px;list-style:disc}.work-row,.experiment{margin:0 0 19px;padding:0;scroll-margin-top:83px}.entry-title{font-size:16px;line-height:1.6;font-weight:400;margin:0}.label{display:inline-block;background:var(--tag);color:#fff;font-family:Georgia,"Times New Roman",serif;font-size:11px;font-weight:700;line-height:1.1;padding:2px 4px;vertical-align:baseline;margin-right:5px;white-space:nowrap}.entry-role{font-size:15px;margin:3px 0!important;line-height:1.5}.entry-copy{font-size:15px;line-height:1.6;margin:4px 0 5px!important}.entry-limit{font-size:12px;line-height:1.5;color:#7a8288;margin:3px 0 5px!important}.entry-links{font-size:13px;display:flex;gap:11px;flex-wrap:wrap;margin:5px 0}.case-more{font-size:13px;margin:7px 0}.case-more summary{cursor:pointer;color:var(--blue)}.module{margin-top:13px}.module h4{margin:0 0 4px;font-size:14px}.module p{font-size:13px;line-height:1.7}.decisions{padding-left:20px;line-height:1.65}.case-source{font-size:12px;color:#7a8288;line-height:1.6}.filters{display:flex;gap:17px;flex-wrap:wrap;margin:15px 0 20px}.filters button{font:inherit;font-size:13px;color:#7a8288;border:0;background:none;padding:0;cursor:pointer;text-decoration:underline;text-underline-offset:3px}.filters button[aria-pressed=true]{color:var(--blue);font-weight:700}.research-group[hidden],.experiment[hidden]{display:none}.research-group h3{font-size:20px;margin:26px 0 13px}.research-group .entry-title a{font-weight:400}.education{list-style:disc;padding-left:22px;margin:0}.education li{margin-bottom:12px;line-height:1.7}.education .extra{font-size:13px;color:#7a8288}.footer{max-width:1200px;margin:auto;padding:0 18px 30px;font-size:12px;color:#7a8288}.footer p{margin-left:245px;border-top:1px solid var(--line);padding-top:14px;line-height:1.7}.skip{position:absolute;top:-100px;left:15px;z-index:20;background:#fff;padding:8px}.skip:focus{top:8px}
@media(max-width:1000px){.layout{grid-template-columns:180px minmax(0,1fr);gap:30px}.content{max-width:100%}.footer p{margin-left:210px}}
@media(max-width:760px){body{font-size:15px}.nav-inner{padding:16px 15px;gap:21px}.navlinks{gap:22px;flex-wrap:wrap}.navlinks a,.brand{font-size:14px}.layout{display:block;padding:22px 15px}.identity{position:static;display:flex;align-items:center;justify-content:space-between;gap:18px;margin-bottom:29px;padding-bottom:18px}.identity h1{font-size:19px}.identity p{font-size:14px}.identity-links{font-size:14px;margin:0;align-self:start;gap:12px}.identity-note{display:none}.section h2{font-size:21px}.section h3,.research-group h3{font-size:18px}.content{max-width:none}.entry-title,.entry-role,.entry-copy{font-size:15px}.footer{padding:0 15px 23px}.footer p{margin-left:0}.section{scroll-margin-top:79px}.label{font-size:10px}}
@media(max-width:420px){.brand{display:none}.navlinks{gap:25px}.identity-links{flex-direction:column;gap:6px}.identity{align-items:flex-start}.section h2{margin-bottom:13px}.works,.experiments,.education{padding-left:20px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''
SHORT={
'drawing-review':'负责审核工作台、规则＋模型分级路由、账号权限和数据看板，推动上线与迭代。11 条结构化规则、9 条模型审核 Prompt；通过 6 轮、300+ Badcase 复盘，人工复核打回率低于 1%。',
'standards-platform':'独立搭建技术标准应答与偏离评审平台，将表格与邮件评审线上化。设计条目规则、判定＋校验、人工复核、五级状态评分和风险看板；在试点中迭代，支持配置化复用。',
'skills-knowledge':'沉淀 6 个可复用 Skill，以及 10 章、约 446 条术语知识库，服务两项 AI 产品；统一输入输出与使用边界，采用技能说明常驻、详细知识按需调用和版本回归。',
'force-aigc':'独立完成创意构思、分镜脚本、Prompt 与文生视频草稿交付；对主体一致性、画面风格和镜头衔接进行多轮筛选与修正。'}
LABELS={'drawing-review':'上线产品','standards-platform':'试点产品','skills-knowledge':'公共资产','force-aigc':'AIGC 草稿'}
GROUPS=[
('multimodal','多模态可靠性与模型评估','Multimodal Reliability & Evaluation'),
('agents','Agent 工作流与知识检索','Agent Systems & Retrieval'),
('frontier','大模型算法机制','LLM Algorithm Mechanisms'),
('engineering','电子、通信与 AI 数据中心','AI for Electrical & Communication Engineering')]
# folder,name,title,description,boundary,filter,report,group
RESEARCH=[
('video-guard','VideoGuard-Lab','音画事件同步、校准拒估与因果漂移定位','由 RGB/PCM 事件估计延时，对照相关性、共享 MLP 与双塔 InfoNCE；扩展五种预测集合方法、独立重复校准、十类漂移真值及实际报警延迟。保留失败与 77 项测试、跨语言一致性检查。','合成事件数据；真实媒体入口强制人工复核，不声称自然视频准确率。','research','artifacts/REPORT.md','multimodal'),
('vision-cal','VisionCal','视觉模型置信校准与扰动鲁棒性','训练小型神经网络，研究温度缩放、图像噪声和平移；分开报告 NLL、ECE、覆盖率和错误率。','公开 8×8 图像实验，非通用视觉系统。','research','artifacts/REPORT.md','multimodal'),
('novelty-lab','NoveltyLab','新颖性检测与分布偏移','仅正常样本训练拟合，验证集选阈值；对照距离、Isolation Forest 和 One-Class SVM，分析迁移与漏检。','类别迁移实验，非工业故障实测。','research','artifacts/REPORT.md','multimodal'),
('textguard','TextGuard','可解释文本分类与留出评测','TF-IDF＋Logistic 实际训练，朴素贝叶斯对照、权重解释与浏览器导出推断；保留误判记录。','旧英文短信数据，不代表现代诈骗识别能力。','research','artifacts/REPORT.md','multimodal'),
('reliability-lab','FlowBench','可恢复 AI 工作流实验台','对照单次执行、有限重试、检查点与幂等恢复；构建 BM25 检索、受控故障、崩溃回放和原始事件链。','本地受控负载，不是生产集群或真实 LLM 任务成功率。','infra','results/advanced/REPORT.md','agents'),
('cite-rag','CiteRAG','引用优先检索、摘录与拒答','BM25、字符余弦与 RRF 融合；检查引用 ID、困难改写和无答案拒答，公开逐问题排序与证据。','自建小语料；摘录不是 LLM 生成答案。','product','artifacts/REPORT.md','agents'),
('tiny-attention','TinyAttention','从零训练因果注意力','实现多头注意力、causal mask、残差和层归一，实际 CPU 训练；对照无注意力消融与长度 OOD。','合成查找小模型，不是自然语言预训练。','research','artifacts/REPORT.md','frontier'),
('lora-lab','LoRA-Lab','低秩适配、合并与遗忘','冻结基座、rank1/4 与全量微调对照；验证权重合并一致性，分开观察新任务学习与旧任务保留。','共享 TinyAttention 基座，不外推大模型显存收益。','research','artifacts/REPORT.md','frontier'),
('dpo-lab','DPO-Lab','偏好优化与模型漂移','实现 DPO 损失与 frozen reference，比较 beta 和 SFT；将 pair win、chosen top1、KL 和旧任务保留分别报告。','规则单 token 偏好，不是真人对齐。','research','artifacts/REPORT.md','frontier'),
('moe-lab','SparseMoE','稀疏专家执行与负载平衡','实现 top1 专家分发、门控梯度和负载辅助损失；对照两种 dense 基线并评测偏斜 OOD。','微型机制，不是分布式 Transformer MoE。','research','artifacts/REPORT.md','frontier'),
('spec-decode','SpecDecode','精确推测解码与真实开销','训练 draft/target 双模型，greedy 块验证；核验逐 token 一致性，保留接受率、调用次数和三次 CPU 配对计时。','减少目标调用不等于更快；未验证随机采样或 GPU 加速。','infra','artifacts/REPORT.md','frontier'),
('circuit-id','CircuitID','物理与学习结合的 RC 电路辨识','32 点带噪 RC 阶跃；对照规则、物理拟合、Ridge 与 MLP，分析参数估计与分布迁移。','数学仿真，无硬件测量。','research','artifacts/REPORT.md','engineering'),
('channel-est','ChannelEst','学习型信道估计与先验迁移','理想频域导频估计、均衡和 QPSK；对照模型，报告 NMSE/BER、SNR 条件与先验迁移。','无线链路仿真，无设备或外场测试。','research','artifacts/REPORT.md','engineering'),
('power-scope','PowerScope','AI 数据中心功率预测','构建下一步负荷预测、计划特征消融、时间留出与冷却漂移测试；公开预测和失败记录。','合成时序、离线只读，不控制电气设备。','infra','artifacts/REPORT.md','engineering')]


def build():
    d=json.loads((ROOT/'profile/resume.json').read_text());out=[]
    out.append('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>于跃 | AI Product Portfolio</title><meta name="description" content="于跃：Agent与AI产品实践，机电工程背景，14项AI辅助算法与工程实验。"><style>'+STYLE+'</style></head><body>')
    out.append('<a class="skip" href="#about">跳至正文</a><header class="masthead"><div class="nav-inner"><a class="brand" href="#top">Homepage</a><nav class="navlinks" aria-label="主导航"><a href="#about">About Me</a><a href="#projects">Products</a><a href="#experiments">Projects</a><a href="#education">Education</a></nav></div></header><div class="layout" id="top"><aside class="identity"><div><h1>于跃</h1><p>Agent / AI Product</p><p class="sub">领域型 AI 产品实践<br>机电与电气工程背景</p><div class="identity-note">新加坡南洋理工大学<br>硕士在读 · 预计 2028 年毕业<br><br>澳门大学 · 机电工程</div></div><div class="identity-links"><a href="https://github.com/LlewynLune">GitHub</a><a href="profile/README.md">Profile</a></div></aside><main class="content">')
    out.append('<section class="section bio" id="about"><h2>自我介绍</h2><p>我目前在新加坡南洋理工大学攻读硕士，预计 2028 年毕业。本科就读于澳门大学科技学院机电工程专业，具有机电与电气工程背景，能够阅读图纸和专业规范。</p><p>我的产品方向专注于<strong>专业知识密集、强规则约束场景中的 Agent 与 AI 产品</strong>。具备从 0—1 产品设计到上线、试点和持续迭代的实践，负责过审核工作台、规则与模型分级路由、账号权限、风险评分与数据看板等核心模块。</p><p>在产品实践中，我通过专家知识库、规则库、引用条款和人工复核机制，让 AI 结论可追溯、可确认、可复算；关注命中率、误报率、人工打回率和结论采纳率，基于真实使用数据与 Badcase 持续迭代。</p><p>此外，我使用 Python、SQL 与 AI Coding 验证方案，并在 AI 辅助下搭建了<strong>14 项研究与工程实验</strong>，覆盖多模态可靠性、Agent 工作流、知识检索、大模型算法机制，以及电子、通信和 AI 数据中心场景。项目公开 Demo、源码、实验报告和失败记录；AI 辅助实现与本人独立复核的边界明确区分。</p></section>')
    out.append('<section class="section" id="focus"><h2>产品与技术方向</h2><ul class="focus-list"><li><strong>领域型 Agent 产品：</strong>专业规则结构化、人机协同审核、偏离评审、风险评分与决策可复算。</li><li><strong>可靠性与知识运营：</strong>知识检索、证据追溯、低置信复核、Badcase 迭代、公共 Skill 和术语资产。</li><li><strong>算法理解与工程验证：</strong>多模态校准、注意力、LoRA、DPO、MoE、推测解码与跨学科仿真。</li></ul></section>')
    out.append('<section class="section" id="projects"><h2>产品实践</h2><p class="section-note">四项真实实践，职责与指标依据本人可公开履历；不提供内部代码、图纸或原始业务数据。</p><ul class="works">')
    for c in d['cases']:
        out.append('<li class="work-row" id="case-'+c['id']+'"><div class="entry-title"><span class="label">'+LABELS[c['id']]+'</span><a href="business-cases/'+c['id']+'/README.md">'+E(c['title'])+'</a></div><p class="entry-role"><strong>于跃</strong> · '+E(c['role'])+'</p><p class="entry-copy">'+E(SHORT[c['id']])+'</p><p class="entry-limit">'+E(c['status'])+'</p><div class="entry-links"><a href="business-cases/'+c['id']+'/README.md">[Case Study]</a><a href="#case-'+c['id']+'" data-case="'+c['id']+'">[Details]</a></div><details class="case-more"><summary>模块设计与关键取舍</summary>')
        for mod in c['modules']:out.append('<div class="module"><h4>'+E(mod['title'])+'</h4><p>'+E(mod['text'])+'</p></div>')
        out.append('<ul class="decisions">'+''.join('<li>'+E(t)+'</li>' for t in c['decisions'])+'</ul><p class="case-source">'+E(c['evidence'])+'</p></details></li>')
    out.append('</ul></section><section class="section" id="experiments"><h2>研究与工程项目</h2><p class="section-note">14 项由 AI 辅助搭建的研究原型，与业务产品分开展示。本地模型 Demo 已可运行，真实大模型接口未调用；可运行不等于生产上线或论文成果。</p><div class="filters" role="group" aria-label="按项目方向筛选"><button data-filter="all" aria-pressed="true">全部</button><button data-filter="product" aria-pressed="false">检索应用</button><button data-filter="research" aria-pressed="false">算法研究</button><button data-filter="infra" aria-pressed="false">基础设施</button></div>')
    for gid,zh,en in GROUPS:
        out.append('<div class="research-group" id="group-'+gid+'"><h3>'+E(zh)+' · '+en+'</h3><ul class="experiments">')
        for folder,name,title,desc,limit,track,report,group in RESEARCH:
            if group!=gid:continue
            out.append('<li class="experiment" data-track="'+track+'"><div class="entry-title"><span class="label">AI-assisted</span><a href="projects/'+folder+'/demo.html">'+name+': '+E(title)+'</a></div><p class="entry-role"><strong>于跃的个人项目仓库</strong> · AI 辅助研究原型</p><p class="entry-copy">'+E(desc)+'</p><p class="entry-limit">'+E(limit)+'</p><div class="entry-links"><a href="projects/'+folder+'/demo.html">[Demo]</a><a href="projects/'+folder+'/README.md">[Code]</a><a href="projects/'+folder+'/'+report+'">[Report]</a></div></li>')
        out.append('</ul></div>')
    out.append('<p class="section-note">LoRA 与 DPO 共享 TinyAttention 小型基座；不将对照模型或实验模块拆为独立项目，不声称全部代码为本人独立研发。<a href="docs/ai-evidence.md">实验真实性</a> · <a href="docs/frontier-evidence.md">算法机制与失败结果</a></p></section><section class="section" id="education"><h2>教育背景</h2><ul class="education">')
    for edu in d['education']:
        out.append('<li><strong>'+E(edu['school'])+'</strong> · '+E(edu['degree'])+' · '+E(edu['date']))
        if 'major' in edu:out.append('<br>'+E(edu['faculty']+' / '+edu['major'])+'<br><span class="extra">'+E(edu['lab'])+'；'+E(edu['student_leadership'])+'</span>')
        out.append('</li>')
    out.append('</ul></section></main></div><footer class="footer"><p>真实产品实践依据本人简历 · 研究实验为 AI 辅助原型 · Python 实验仅本机运行<br><a href="https://github.com/LlewynLune/ai-portfolio">GitHub 完整仓库</a> · <a href="PUBLISHING.md">披露与贡献边界</a></p></footer>')
    out.append('''<script>
const buttons=[...document.querySelectorAll('[data-filter]')],experiments=[...document.querySelectorAll('[data-track]')];
buttons.forEach(b=>b.addEventListener('click',()=>{buttons.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));experiments.forEach(x=>x.hidden=b.dataset.filter!=='all'&&x.dataset.track!==b.dataset.filter);document.querySelectorAll('.research-group').forEach(g=>g.hidden=![...g.querySelectorAll('[data-track]')].some(x=>!x.hidden))}));
function openCase(){const id=location.hash.slice(1);if(id.startsWith('case-')){const item=document.getElementById(id);if(item)item.querySelector('details').open=true}}
window.addEventListener('hashchange',openCase);document.querySelectorAll('[data-case]').forEach(a=>a.addEventListener('click',()=>document.getElementById('case-'+a.dataset.case).querySelector('details').open=true));openCase();
</script></body></html>''')
    (ROOT/'index.html').write_text('\n'.join(out))
    print('Built single-reference profile: four business products + 14 AI-assisted projects in four thematic groups')
if __name__=='__main__':build()
