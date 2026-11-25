"""Restyle existing inference pages as an academic demonstration, no model/JS changes.
Single measured design source: Video-MME project page; metadata belongs to this repo.
"""
from pathlib import Path
import html,re
from academic_project_style import CSS as BASE_CSS,hero
ROOT=Path(__file__).resolve().parents[1]
CSS='\n/* ===== Portfolio presentation system: academic project layout ===== */\n'+BASE_CSS+r'''
body main,body main.shell{max-width:1008px;margin:auto;padding:0 24px 48px;min-width:0}body .grid,body .layout,body .split,body .two{display:block;min-width:0}body .grid>*,body .layout>*,body .split>*,body .two>*{min-width:0}
body .card,body .panel{border:0;border-radius:0;box-shadow:none;padding:34px 0;margin:0;background:#fff;min-width:0}body .card+.card,body .content>.panel,body .split>.panel+section{border-top:1px solid #eee}body .panel .panel{border-top:1px solid #eee;margin-top:24px}
body h2{font-size:28px;line-height:1.25;color:#363636;font-weight:600;text-align:center;margin:0 0 24px}body h3{font-size:21px;color:#363636;font-weight:600;margin-top:26px}body p{color:#4a4a4a;font-size:16px;line-height:1.7}body .label,body .eyebrow{font-size:12px;letter-spacing:0;color:#777}
body>header:not(.publication-header){display:none}body main>h1,body main>.label,body main>.badge,body main>p:first-of-type,body main>header,body .intro,body main>div[style*="padding-top:28px"]{display:none}
body main>.grid{margin-top:0!important}body .badge{font-size:12px;color:#777;border:0;border-radius:0;background:none;padding:0;white-space:normal}
body button,body button.primary,body button.secondary{padding:8px 17px;border:1px solid #363636;border-radius:999px;background:#363636;color:white;font-size:14px;line-height:1.5;min-height:38px;margin:8px 6px 8px 0;width:auto}body button:disabled{opacity:.4;cursor:not-allowed}body button:hover:not(:disabled){background:#222}body select,body input:not([type=range]):not([type=checkbox]):not([type=file]),body textarea{font:14px/1.6 Arial,"PingFang SC",sans-serif;border:1px solid #ccc;border-radius:3px;padding:8px 10px;background:#fff;color:#4a4a4a;max-width:100%;min-width:0}body textarea{width:100%;min-height:105px}body .controls{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 24px;align-items:end}body .controls h2,body .controls p,body .controls hr,body .controls label[for=report],body .controls input[type=file]{grid-column:1/-1}body .controls label{font-size:14px;color:#4a4a4a;margin:10px 0 6px;display:block}
body .metrics{display:flex;flex-wrap:wrap;justify-content:center;gap:25px;margin:22px 0;border-top:1px solid #777;border-bottom:1px solid #777;padding:16px 0}body .metric{background:#fff;border:0;border-radius:0;padding:8px;min-width:140px;text-align:center;color:#363636;font-size:32px}body .metric b{font-size:28px;display:block;font-variant-numeric:tabular-nums}body .metric span{font-size:12px;color:#666;display:block}
body .warning,body .warn,body .status{background:none;border:0;border-radius:0;color:#777;padding:10px 0;font-size:13px;line-height:1.8}body .warning{border-left:2px solid #bbb;padding-left:14px;margin:20px 0}.presentation-guide{color:#777;font-size:13px}
body .scroll{overflow:auto;border:0;border-radius:0;max-width:100%;max-height:440px}body table{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums}body th,body td{padding:10px 12px;border-bottom:1px solid #ddd;background:#fff;white-space:nowrap;line-height:1.6}body th{border-top:2px solid #555;border-bottom:1px solid #aaa;font-weight:600;color:#363636}body tbody tr:nth-child(even){background:#fff}body tr:hover td{background:#fafafa}body pre{background:#fafafa;border:0;border-radius:0;padding:16px;white-space:pre-wrap;overflow-wrap:anywhere;max-height:320px;overflow:auto;font:12px/1.7 ui-monospace,SFMono-Regular,Consolas,monospace}
body canvas{width:100%;max-width:100%;height:auto;border:0;border-radius:0}body .tabs{justify-content:center;flex-wrap:wrap;border-bottom:1px solid #ddd;padding-bottom:14px;margin:15px 0 24px;gap:8px}body .tabs button{background:#fff;color:#555;border:0;border-radius:0;padding:7px 13px;margin:0;font-size:14px}body .tabs button[aria-pressed=true]{background:#fff;color:#209cee;border-bottom:2px solid #209cee}
body .tiny,body .small,body footer,body .footer{font-size:13px;line-height:1.75;color:#777}body .toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.demo-navigation{display:none}.publication-header h1{display:block!important}.publication-header h2{font-size:32px;font-weight:400}.publication-header p{margin-top:0}.publication-header .publication-note{font-size:12px}.publication-header{display:block!important;border:0;padding:48px 24px 50px;gap:0}.publication-header .publication-links{display:flex;justify-content:center;flex-wrap:wrap;width:auto}.publication-header a.resource{color:#fff}.publication-header .publication-title{font-size:48px;line-height:1.125;font-weight:600;margin:0 0 24px}.project-top{display:flex}.project-top a{color:#777}
@media(max-width:600px){body main,body main.shell{padding:0 20px 30px}body .controls{grid-template-columns:1fr}body .card,body .panel{padding:28px 0}body .metrics{gap:10px}body .metric{min-width:125px;padding:6px}body h2{font-size:25px}.publication-header .publication-title{font-size:38px}.publication-header .publication-subtitle{font-size:25px}.publication-header{padding:32px 20px 34px}}
'''
START='<!-- presentation-shell:start -->';END='<!-- presentation-shell:end -->'
def polish(page,project):
 if START in page:page=page.split(START,1)[0]+page.split(END,1)[1]
 page=re.sub(r'\n*/\* ===== Portfolio presentation system:.*?/\* ===== End presentation system ===== \*/\n*','',page,flags=re.S)
 page=re.sub(r'href="(?!https?://)([^"#]+\.md)"',lambda m:'href="https://github.com/LlewynLune/ai-portfolio/blob/main/projects/'+project+'/'+m[1]+'"',page)
 page=page.replace('</style>',CSS+'\n/* ===== End presentation system ===== */\n</style>',1)
 # New title shell precedes original main; model controls and all script identifiers are unchanged.
 page=page.replace('<h2>改变观察，而非手填评分</h2>','<h2>Interactive Demo</h2>').replace('这次实验告诉你什么</h2>','Workflow Analysis</h2>').replace('实际参数推断</h2>','Model Inference</h2>').replace('真实参数推断</h2>','Model Inference</h2>').replace('冻结评测与方法边界</h2>','Evaluation Protocol</h2>').replace('冻结训练与失败记录</h2>','Evaluation Results</h2>')
 shell=START+hero(project,'demo')+END+'<nav class="demo-navigation" aria-label="项目导航" hidden></nav>'
 page=re.sub(r'<nav class="demo-navigation"[^>]*>.*?</nav>','',page,flags=re.S)
 page=page.replace('<body>','<body>'+shell,1)
 return page
if __name__=='__main__':
 for p in sorted((ROOT/'projects').glob('*/demo.html')):p.write_text(polish(p.read_text(),p.parent.name));print('Academic demo',p.parent.name)
