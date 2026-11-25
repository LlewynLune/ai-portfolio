"""Work-experience presentation using measured public academic CV geometry.
All employment attribution is owner-confirmed in resume.json; no inferred title/dates/team.
"""
from pathlib import Path
import html,json
ROOT=Path(__file__).resolve().parents[1]
E=html.escape
CSS=r'''
.work-experience{font-family:Arial,"PingFang SC",sans-serif;background:#fff}.employment-row{display:flex;gap:0;align-items:flex-start;margin:28px 0 22px}.employment-logo{width:140px;flex:0 0 140px;min-height:140px;display:flex;align-items:center;justify-content:center;padding:8px 13px 8px 0}.employment-logo img{width:140px;height:auto;border:0;box-shadow:none;border-radius:0;padding:0}.employment-meta{font-size:18px;line-height:1.42857143;padding:5px 0 0 0;min-width:0}.employment-role{font-weight:700;margin:0}.employment-company{margin:3px 0}.employment-company a{color:#337ab7}.employment-scope{font-size:16px;color:#555;margin:3px 0}.employment-subline{font-size:14px;color:#777;margin:6px 0}.experience-projects{margin-left:140px;max-width:840px}.experience-project{border:0;border-top:1px solid #eee;margin:0;padding:24px 0;font-size:15px;line-height:1.7}.experience-project h3{font-size:18px;font-weight:700;color:#333;line-height:1.5;margin:0 0 6px}.experience-project .role-line{font-size:14px;color:#666;margin:0 0 12px}.experience-project ul{padding-left:19px;margin:10px 0 14px}.experience-project li{margin:6px 0;line-height:1.8}.experience-project .work-links{font-size:13px;display:flex;gap:18px;flex-wrap:wrap}.experience-project details{margin-top:12px;font-size:13px}.experience-project summary{color:#337ab7;cursor:pointer}.experience-project .module h4{font-size:14px;color:#333}.experience-project .module p{font-size:13px;line-height:1.8}.experience-project .case-source{font-size:12px;color:#777;line-height:1.8;margin:12px 0 0}.employment-disclosure{font-size:12px;color:#777;line-height:1.8;margin:18px 0}.experience-project .case-more{border:0;border-radius:0;background:none;padding:0}
@media(max-width:767px){.employment-logo{width:120px;flex-basis:120px;min-height:120px;padding-right:15px}.employment-meta{font-size:17px;padding-top:12px}.employment-scope{font-size:14px}.experience-projects{margin-left:0;max-width:none}.experience-project{padding:22px 0}.experience-project h3{font-size:17px}.experience-project ul{font-size:14px}.employment-row{margin-top:16px}.employment-subline{font-size:12px}}
@media(max-width:420px){.employment-logo{width:100px;flex-basis:100px;min-height:100px}.employment-meta{font-size:16px}.employment-scope{font-size:13px}}
'''
BULLETS={
'drawing-review':[
('产品设计与上线','完成审核工作台、任务流转、人工介入、问题清单、报告导出及数据看板设计，推动业务使用。'),
('审核策略','梳理并结构化 11 条规则，设计 9 条模型审核 Prompt，按条目类型与风险分级路由，结合专家知识和人工复核。'),
('反馈闭环','基于 6 轮、300+ Badcase 复盘迭代规则、Prompt 与知识召回；人工复核打回率低于 1%。')],
'standards-platform':[
('0—1 搭建','将技术标准应答和偏离评审从表格、邮件流转转为线上工作台，推动平台在试点项目中使用。'),
('智能判定','设计“判定＋校验”两层机制；给出等级、理由与引用条款，证据不足或低置信时转人工复核。'),
('风险与复用','贯通五级状态评分、维度加权和风险看板，通过配置化规则与统一接口支持多项目复用。')],
'skills-knowledge':[
('能力沉淀','封装 6 个可复用 Skill，统一场景、输入输出、使用边界与调用方式。'),
('公共知识','建设 10 章、约 446 条术语知识库，服务 AI 审图与标准化评审两项产品。'),
('调用与维护','采用“技能说明常驻、详细内容按需调用”，随反馈补充能力，并在版本更新时同步回归。')],
'force-aigc':[
('创意与制作','独立完成主题拆解、创意构思、分镜脚本、镜头语言和提示词设计。'),
('质量控制','对主体一致性、风格和镜头衔接进行多轮筛选与修正，交付文生视频草稿；未标注正式投放或大会播放。')]
}
def render(d):
 emp=d['employment'];out=[]
 out.append('<section class="section work-experience" id="projects"><div class="container"><h2>Work Experience <small>字节跳动工作经历</small></h2>')
 out.append('<div class="employment-row"><a class="employment-logo" href="https://www.bytedance.com/en/"><img src="assets/portfolio/bytedance-logo.svg" alt="ByteDance 字节跳动官网标识" width="146" height="38"></a><div class="employment-meta"><div class="employment-role">'+E(emp['type'])+'</div><div class="employment-company"><a href="https://www.bytedance.com/en/"><strong>ByteDance · 字节跳动</strong></a></div><div class="employment-scope">'+E(emp['scope'])+'</div><div class="employment-subline">审核工作台 / 混合审核策略 / 标准评审 / 知识与 Skill</div></div></div>')
 out.append('<div class="experience-projects">')
 for c in d['cases']:
  out.append('<article class="experience-project work-row" id="case-'+c['id']+'"><h3>'+E(c['title'])+'</h3><p class="role-line">'+E(c['role'])+' · '+E(c['status'])+'</p><ul>'+''.join('<li><strong>'+E(t)+'：</strong>'+E(v)+'</li>' for t,v in BULLETS[c['id']])+'</ul><div class="work-links"><a href="business-cases/'+c['id']+'/case.html">Case Study</a><a href="#case-'+c['id']+'" data-case="'+c['id']+'">Details</a></div><details class="case-more"><summary>职责、模块与关键取舍</summary>')
  for m in c['modules']:out.append('<div class="module"><h4>'+E(m['title'])+'</h4><p>'+E(m['text'])+'</p></div>')
  out.append('<ul>'+''.join('<li>'+E(v)+'</li>' for v in c['decisions'])+'</ul><p class="case-source">'+E(c['evidence'])+'</p></details></article>')
 out.append('</div><p class="employment-disclosure">真实产品实践依据本人简历；本人已确认四项均属于字节跳动工作经历。职责、指标和阶段沿用可公开履历，不公开公司代码、图纸、客户材料或内部系统截图。该页面为个人作品集，不代表公司官方发布或背书。</p></div></section>')
 return ''.join(out)
def build_cases():
 d=json.loads((ROOT/'profile/resume.json').read_text())
 base='''*{box-sizing:border-box}body{margin:0;color:#333;background:#fff;font:16px/1.7 Arial,PingFang SC,Microsoft YaHei,sans-serif}a{color:#337ab7;text-decoration:none}a:hover{text-decoration:underline}main{max-width:970px;margin:auto;padding:28px 24px}nav{font-size:13px;margin-bottom:30px}h1{font-size:30px;line-height:1.3;font-weight:600;margin:22px 0 12px}h2{font-size:23px;font-weight:500;margin:40px 0 18px;padding-bottom:14px;border-bottom:1px solid #eee}h3{font-size:17px;margin:23px 0 6px}p{line-height:1.8}.employer{display:flex;align-items:center;gap:28px;border-bottom:1px solid #eee;padding:0 0 22px}.employer img{width:146px;height:auto}.employer strong{display:block;font-size:20px}.employer span{font-size:14px;color:#777}.role{color:#666;font-size:14px}.statement{font-size:13px;color:#777;line-height:1.8}.facts{padding-left:20px}.facts li{margin:10px 0}.figure{margin:20px 0}.figure img{display:block;width:100%;max-width:640px;margin:auto}figcaption{text-align:center;font-size:12px;color:#777;margin-top:10px}summary{cursor:pointer;color:#337ab7;font-size:13px}footer{border-top:1px solid #eee;margin-top:35px;padding-top:20px;font-size:12px;color:#777}@media(max-width:600px){main{padding:20px}h1{font-size:26px}.employer{gap:18px}.employer img{width:110px}.employer strong{font-size:18px}}'''
 for c in d['cases']:
  page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(c['title'])+' | 字节跳动工作经历</title><style>'+base+'</style></head><body><main><nav><a href="../../index.html#projects">← Work Experience</a> · <a href="https://github.com/LlewynLune/ai-portfolio/blob/main/business-cases/'+c['id']+'/README.md">案例文档</a></nav><div class="employer"><img src="../../assets/portfolio/bytedance-logo.svg" alt="ByteDance 字节跳动官方标识"><div><strong>ByteDance · 字节跳动</strong><span>工作经历 / 领域 AI 产品实践</span></div></div><h1>'+E(c['title'])+'</h1><p class="role">'+E(c['role'])+' · '+E(c['status'])+'</p><p>'+E(c['overview'])+'</p><h2>项目成果</h2><ul class="facts">'+''.join('<li><strong>'+E(t)+'：</strong>'+E(v)+'</li>' for t,v in BULLETS[c['id']])+'</ul><h2>场景与产品职责</h2><p>'+E(c['problem'])+'</p>'+''.join('<h3>'+E(m['title'])+'</h3><p>'+E(m['text'])+'</p>' for m in c['modules'])+'<h2>关键取舍</h2><ul>'+''.join('<li>'+E(v)+'</li>' for v in c['decisions'])+'</ul><details><summary>产品流程示意（非系统截图）</summary><figure class="figure"><img src="../../assets/portfolio/'+c['id']+'.svg" alt="'+E(c['title'])+'产品流程示意，非系统截图"><figcaption>仅根据可公开履历整理的说明图，不是内部实现或原系统画面。</figcaption></figure></details><h2>证据与公开边界</h2><p class="statement">'+E(c['evidence'])+'</p><p class="statement">公司归属和工作经历性质经本人确认。正式职位、团队和日期未提供，不补写。所有职责与指标为本人提供并确认可公开的履历；本页不公开内部代码、图纸、客户数据、真实系统截图或原始统计。</p><footer>于跃个人作品集 · 公司工作经历依据本人确认<br>公司标识仅用于经历识别，商标权归字节跳动，不构成官方背书。</footer></main></body></html>'
  from build_case_analysis import render as render_analysis
  page=page.replace('<h2>证据与公开边界</h2>',render_analysis(c)+'<h2>证据与公开边界</h2>')
  (ROOT/'business-cases'/c['id']/'case.html').write_text(page);print('Business case',c['id'])
if __name__=='__main__':build_cases()
