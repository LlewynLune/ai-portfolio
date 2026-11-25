"""Readable original-writing archive and small personal-background section.
No rewriting of author's original article, no third-party image republication.
"""
from pathlib import Path
import html,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'profile/writing';E=html.escape
ARTICLE='https://mp.weixin.qq.com/s/F12ydRzh1u-T2M8EuSPWJg'
PODCAST='https://www.xiaoyuzhoufm.com/podcast/615ffb31ef56f237f8e18917'
CSS='''*{box-sizing:border-box}body{margin:0;font:17px/1.95 Arial,"PingFang SC","Microsoft YaHei",sans-serif;color:#333;background:#fff}main{max-width:800px;margin:auto;padding:42px 24px 80px}nav{max-width:800px;margin:auto;padding:24px;font-size:13px}a{color:#337ab7;text-decoration:none}a:hover{text-decoration:underline}h1{font-size:35px;line-height:1.4;margin:30px 0}h2{font-size:25px;line-height:1.5;margin-top:55px}h3{font-size:21px;line-height:1.6;margin-top:28px}p{margin:20px 0;white-space:pre-wrap}blockquote{border-left:3px solid #bbb;margin:30px 0;padding-left:20px;font-size:14px;color:#666}hr{border:0;border-top:1px solid #ddd;margin:35px 0}.meta{font-size:13px;color:#777}footer{max-width:800px;margin:auto;padding:30px 24px;border-top:1px solid #eee;font-size:13px;color:#777}@media(max-width:500px){h1{font-size:28px}body{font-size:16px}main{padding:24px 20px 60px}}'''

def inline(text):
 text=E(text)
 import re
 text=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<a href="\2">\1</a>',text)
 text=re.sub(r'\*\*(.*?)\*\*',r'<strong>\1</strong>',text)
 return text

def build():
 file=P/'verification-layer.md';text=file.read_text();parts=[]
 for block in text.split('\n\n'):
  if not block.strip():continue
  if block.startswith('# '):parts.append('<h1>'+inline(block[2:])+'</h1>')
  elif block.startswith('## '):
   for line in block.splitlines():
    if line.startswith('### '):parts.append('<h3>'+inline(line[4:])+'</h3>')
    elif line.startswith('## '):parts.append('<h2>'+inline(line[3:])+'</h2>')
  elif block.startswith('### '):parts.append('<h3>'+inline(block[4:])+'</h3>')
  elif block.startswith('> '):parts.append('<blockquote>'+inline(block[2:])+'</blockquote>')
  elif block=='---':parts.append('<hr>')
  else:parts.append('<p>'+inline(block)+'</p>')
 page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>于跃｜谁来给 AI 验收？</title><style>'+CSS+'</style></head><body><nav><a href="../../index.html#more">← Portfolio / More about me</a> · <a href="'+ARTICLE+'">公众号原文</a></nav><main>'+''.join(parts)+'</main><footer>作者：于跃 · 公众号「愤怒的墨镜」<br>正文原文归档，非工程项目。第三方图片请在原文查看。</footer></body></html>'
 (P/'verification-layer.html').write_text(page)
 metadata={'author':'于跃','ownership':'公众号与播客均由本人确认创立；文章本人确认撰写','section':'More about me / 补充信息，非主要项目','article':{'title':'Continual Learning 时代最缺的一层 AI Infra——“谁来给 AI 验收？”','account':'愤怒的墨镜','source':ARTICLE,'published':'2026-09-03','archive':'verification-layer.md','sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'archive_scope':'公开可读取正文全文文字；图注保留，第三方原图未重新分发；未改原稿数字或观点'},'podcast':{'title':'小青年广场','source':PODCAST,'description':'独立书店、音乐与文学'}}
 (P/'sources.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2));print('Built full author text archive',len(text),'characters')
if __name__=='__main__':build()
