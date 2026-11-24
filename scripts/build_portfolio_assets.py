"""Generate name placeholder and owner-described product schematics.
Diagrams are explanatory, not screenshots, architecture verification or original internal assets.
"""
from pathlib import Path
import html
ROOT=Path(__file__).resolve().parents[1]/'assets/portfolio'
ROOT.mkdir(parents=True,exist_ok=True)
E=html.escape
BASE='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 373"><rect width="640" height="373" fill="#fbfcfe"/><style>text{font-family:Arial,PingFang SC,Microsoft YaHei,sans-serif;fill:#32445b}.title{font-size:23px;font-weight:bold}.small{font-size:13px;fill:#7d8ba0}.node{fill:#eef3f9;stroke:#c0ccda;stroke-width:1.5}.arrow{fill:none;stroke:#7893b4;stroke-width:2}</style>'
def box(x,y,w,h,t):return f'<rect class="node" x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/><text x="{x+w/2}" y="{y+h/2+6}" font-size="18" text-anchor="middle">{E(t)}</text>'
def line(x,y,a,b):return f'<path class="arrow" d="M{x},{y} L{a},{b}"/><circle cx="{a}" cy="{b}" r="3" fill="#7893b4"/>'
items={
'drawing-review':('Hybrid Review', ['图纸任务','分级路由','规则审核','模型审核','人工复核','报告与留痕']),
'standards-platform':('Evidence-based Assessment',['条目规则','证据材料','判定','校验','人工复核','评分与看板']),
'skills-knowledge':('Reusable Knowledge Assets',['高频场景','Skill 边界','6 个 Skill','约 446 术语','按需调用','版本回归']),
'force-aigc':('AIGC Creative Workflow',['大会主题','创意分镜','镜头 Prompt','视频草稿','质量筛选','草稿交付'])}
for key,(title,labels) in items.items():
    s=BASE+f'<text class="title" x="32" y="42">{title}</text><text class="small" x="32" y="68">PRODUCT MODULES · EXPLANATORY SCHEMATIC</text>'
    for i,t in enumerate(labels):
        x=32+(i%3)*204;y=108+(i//3)*124;s+=box(x,y,168,59,t)
    for a,b in [(0,1),(1,2),(2,5),(5,4),(4,3)]:
        x1=32+(a%3)*204+84;y1=108+(a//3)*124+29
        x2=32+(b%3)*204+84;y2=108+(b//3)*124+29
        if a//3==b//3:s+=line(x1+(84 if b>a else -84),y1,x2+(-84 if b>a else 84),y2)
        else:s+=line(x1,y1+29,x2,y2-29)
    s+='<text class="small" x="32" y="344">模块流程示意 · 非真实系统截图 · 不含内部素材</text></svg>'
    (ROOT/(key+'.svg')).write_text(s)
identity='''<svg xmlns="http://www.w3.org/2000/svg" width="644" height="483" viewBox="0 0 644 483"><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#283c59"/><stop offset="1" stop-color="#5b789b"/></linearGradient></defs><rect width="644" height="483" fill="url(#g)"/><path d="M0 400 200 240 400 430 644 130" fill="none" stroke="#b1bfd0" stroke-width="2" opacity=".2"/><text x="322" y="260" text-anchor="middle" fill="#e4eaf3" font-family="PingFang SC,Microsoft YaHei,sans-serif" font-size="112" font-weight="600">于跃</text><text x="322" y="323" text-anchor="middle" fill="#c0ccde" font-family="Arial,sans-serif" font-size="23" letter-spacing="4">AGENT · AI PRODUCT</text></svg>'''
(ROOT/'identity.svg').write_text(identity)
print('Generated 4 explanatory schematics and name monogram')
