"""Presentation-only shell for existing demos; does not touch embedded models or JS engines."""
from pathlib import Path
import html
ROOT=Path(__file__).resolve().parents[1]
CSS=r'''
/* ===== Portfolio presentation system: generated, no model changes ===== */
:root{--paper:#f5f7fa;--bg:#f5f7fa;--ink:#243347;--muted:#607187;--green:#285f79;--line:#dce4ed;--border:#dce4ed;--gold:#865e25;--accent:#285f79}
body{background:#f5f7fa;color:#243347;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:15px;line-height:1.7;-webkit-font-smoothing:antialiased}
body main,body main.shell{max-width:1200px;padding:32px 28px;margin:auto;min-width:0}
body h1{font-size:clamp(26px,3.3vw,38px);font-weight:700;letter-spacing:-.035em;line-height:1.35;margin:20px 0 16px;overflow-wrap:break-word}
body h2{font-size:20px;line-height:1.5;font-weight:650;letter-spacing:-.015em;margin-top:0}
body h3{font-size:16px;line-height:1.5;margin-top:24px}body p{line-height:1.8}body a{color:#285f79;text-underline-offset:4px}body a:hover{color:#143f57}
body .card,body .panel{background:#fff;border:1px solid #dce4ed;border-radius:12px;padding:24px;box-shadow:0 2px 6px rgba(35,52,72,.025);min-width:0}
body .grid,body .two,body .split,body .content,body .layout{min-width:0;gap:24px}body .grid>*{min-width:0}body .metric{font-variant-numeric:tabular-nums}body .metric b{font-size:28px;line-height:1.4}
body .badge{font-size:12px;border:1px solid #d9e5eb;background:#edf4f7;color:#285f79;border-radius:6px;line-height:1.6;padding:5px 10px;white-space:normal}
body .label,body .eyebrow{font-size:11px;color:#607187;letter-spacing:.13em;line-height:1.8}
body .warning,body .warn{background:#faf6ee;border-left:3px solid #c69950;border-radius:0 6px 6px 0;padding:12px 14px;color:#725a36;font-size:12px;line-height:1.8}
body .status{border-radius:8px;font-size:14px;line-height:1.8}body textarea{min-height:116px;resize:vertical;line-height:1.6;background:#fafbfc;font-size:14px}
body select,body input:not([type=range]):not([type=checkbox]):not([type=file]),body textarea{border:1px solid #cbd7e3;border-radius:7px;color:#243347;padding:9px 11px;font:inherit;max-width:100%;min-width:0}
body button{font-size:13px;line-height:1.5;border-radius:7px;padding:10px 15px;transition:background .15s,border-color .15s;min-height:40px}
body button:hover:not(:disabled){filter:brightness(.94)}body button:disabled{opacity:.45;cursor:not-allowed}
body a:focus-visible,body button:focus-visible,body select:focus-visible,body textarea:focus-visible,body input:focus-visible,body summary:focus-visible{outline:3px solid #8bbbd0;outline-offset:3px}
body table{font-size:12px;border-collapse:separate;border-spacing:0;width:100%;font-variant-numeric:tabular-nums}
body th{background:#f4f7fa;color:#4e627a;font-weight:600;position:sticky;top:0;z-index:1}body th,body td{padding:11px 12px;border-bottom:1px solid #e8edf3;white-space:nowrap;vertical-align:top;line-height:1.65}
body tbody tr:nth-child(even){background:#fafbfd}body tbody tr:hover{background:#f0f6fa}
body .scroll{max-width:100%;overflow:auto;border:1px solid #e4eaf1;border-radius:8px;scrollbar-width:thin;scrollbar-color:#b9c8d6 #f3f6fa}
body pre{background:#f6f8fb;border:1px solid #e1e8f0;border-radius:7px;padding:16px;max-height:340px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.75 ui-monospace,SFMono-Regular,Consolas,monospace}
body .tabs{gap:8px;flex-wrap:wrap}body .tabs button{background:#fff;border:1px solid #dce4ed}body .tabs button[aria-pressed=true]{background:#285f79;color:white;border-color:#285f79}
body canvas{max-width:100%;height:auto}body .tiny,body .small,body .footer,body footer{font-size:12px;line-height:1.8;color:#607187}
.demo-navigation{display:flex;gap:8px 20px;align-items:center;flex-wrap:wrap;padding:0 0 18px;margin:0 0 22px;border-bottom:1px solid #dce4ed;font-size:13px}
.demo-navigation a{text-decoration:none}.demo-navigation a:hover{text-decoration:underline}.demo-navigation .mode-label{margin-left:auto;color:#718195;font-size:11px;letter-spacing:.06em}
.presentation-guide{font-size:12px;background:#edf4f7;color:#416378;border-radius:7px;padding:10px 14px;margin:18px 0 0;line-height:1.8}
body .toolbar{gap:10px}body .intro{gap:24px}body .controls{align-content:start}
@media(min-width:1000px){body .grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
@media(max-width:820px){body main,body main.shell{padding:22px 18px}body .grid,body .layout,body .two,body .split{grid-template-columns:minmax(0,1fr)}body .card,body .panel{padding:20px}body .grid .controls{order:0}body .metric b{font-size:24px}}
@media(max-width:500px){body main,body main.shell{padding:18px 14px}body .card,body .panel{padding:16px}body .metrics{gap:9px}body .metric{padding:12px}body .metric b{font-size:22px}.demo-navigation{gap:9px 15px}.demo-navigation .mode-label{width:100%;margin:0}body .tabs{gap:6px}body .tabs button{padding:9px 10px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
'''
START='<!-- presentation-shell:start -->';END='<!-- presentation-shell:end -->'
def polish(page,project):
    if START in page:
        before,rest=page.split(START,1);_,after=rest.split(END,1);page=before+after
    import re
    page=re.sub(r'\n*/\* ===== Portfolio presentation system:.*?/\* ===== End presentation system ===== \*/\n*','',page,flags=re.S)
    # Markdown links should render on GitHub rather than download raw on Pages.
    import re
    page=re.sub(r'href="(?!https?://)([^"#]+\.md)"',lambda m:'href="https://github.com/LlewynLune/ai-portfolio/blob/main/projects/'+project+'/'+m[1]+'"',page)
    page=page.replace('</style>',CSS+'\n/* ===== End presentation system ===== */\n</style>',1)
    nav=f'{START}<nav class="demo-navigation" aria-label="项目导航"><a href="../../index.html#experiments">← 作品集</a><a href="https://github.com/LlewynLune/ai-portfolio/tree/main/projects/{html.escape(project)}">代码与文档 ↗</a><a href="depth-demo.html">深化分析</a><span class="mode-label">MODEL DEMO · AI 辅助研究原型</span></nav>{END}'
    # Insert after the existing main's opening tag without moving any original element.
    import re
    page=re.sub(r'(<main\b[^>]*>)',lambda m:m[0]+nav,page,count=1)
    return page
if __name__=='__main__':
    for path in sorted((ROOT/'projects').glob('*/demo.html')):
        path.write_text(polish(path.read_text(),path.parent.name));print('Polished',path.parent.name)
