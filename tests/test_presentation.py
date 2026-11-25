"""Presentation contract tests, no claim that layout tests prove project quality."""
import unittest,sys,re,json,hashlib
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from demo_presentation import polish
class P(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id' in a:self.ids.append(a['id'])
  if t=='a' and 'href' in a:self.links.append(a['href'])
class PresentationTests(unittest.TestCase):
 def test_14_demo_shells_and_idempotence(self):
  paths=list(ROOT.glob('projects/*/demo.html'));self.assertEqual(len(paths),14)
  for p in paths:
   text=p.read_text();self.assertEqual(text.count('class="demo-navigation"'),1);self.assertEqual(polish(text,p.parent.name),polish(polish(text,p.parent.name),p.parent.name));self.assertIn('depth-demo.html',text)
 def test_academic_project_pages_and_source_tables(self):
  from academic_project_style import PROJECTS
  pages=list(ROOT.glob('projects/*/project.html'));self.assertEqual(len(pages),14)
  for p in pages:
   text=p.read_text();parser=P();parser.feed(text);self.assertEqual(len(parser.ids),len(set(parser.ids)))
   for section in ['Introduction','Overview','Method','Experimental Results','Interactive Demo','Limitations &amp; Reproducibility']:
    self.assertIn(section,text)
   data=json.loads((p.parent/'artifacts/depth/results.json').read_text());condition=sorted({r['condition'] for r in data['metrics']})[0];self.assertIn(condition,text);self.assertIn('非论文发表或生产项目',text);self.assertIn('publication-subtitle',text)
   for link in parser.links:
    if '://' not in link and not link.startswith('#'):self.assertTrue((p.parent/link.split('#',1)[0]).is_file(),link)
 def test_14_depth_records_unchanged(self):
  paths=list(ROOT.glob('projects/*/depth-demo.html'));self.assertEqual(len(paths),14)
  for p in paths:
   text=p.read_text();start=text.index('const DATA=')+len('const DATA=');end=text.index(',META=',start);embedded=json.loads(text[start:end]);original=json.loads((p.parent/'artifacts/depth/results.json').read_text());self.assertEqual(embedded,original)
   for marker in ['id="aggregate-note"','id="record-facts"','id="diag-note"','id="reset"','Enter','max-width:500px']:
    self.assertIn(marker,text)
 def test_depth_ids_unique_and_internal_anchors(self):
  for p in ROOT.glob('projects/*/depth-demo.html'):
   parser=P();parser.feed(p.read_text());self.assertEqual(len(parser.ids),len(set(parser.ids)))
   for link in parser.links:
    if link.startswith('#'):self.assertIn(link[1:],parser.ids)
    elif '://' not in link:self.assertTrue((p.parent/link.split('#',1)[0]).is_file(),link)
 def test_readme_demo_links_open_pages(self):
  text=(ROOT/'README.md').read_text();self.assertIn('两项代表性工程实验',text)
  demo_links=re.findall(r'\]\(([^)]+(?:demo\.html|depth-demo\.html))\)',text);self.assertGreaterEqual(len(demo_links),14)
  self.assertTrue(all(x.startswith('https://llewynlune.github.io/ai-portfolio/') for x in demo_links))
 def test_home_keeps_style_and_eager_evidence(self):
  text=(ROOT/'index.html').read_text();self.assertIn('stars.jpg',text);self.assertIn('class="featured-path"',text);self.assertEqual(text.count('loading="eager"'),14)
if __name__=='__main__':unittest.main()
