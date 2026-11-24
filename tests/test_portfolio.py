import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('checker', ROOT / 'scripts/check_portfolio.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class PortfolioTest(unittest.TestCase):
    def test_structure_and_links(self):
        self.assertEqual(checker.check(ROOT), [])
    def test_resume_cases_and_evidence_boundaries(self):
        import json
        data=json.loads((ROOT/'profile/resume.json').read_text())
        self.assertEqual(len(data['cases']),4)
        self.assertEqual(data['education'][0]['degree'],'硕士在读')
        self.assertTrue(data['publication']['projects_and_metrics_owner_confirmed_public'])
        for case in data['cases']:
            text=(ROOT/'business-cases'/case['id']/'README.md').read_text()
            self.assertIn('本人提供并确认可公开的履历',text)
            self.assertIn(case['title'],text)
    def test_form_references_and_placeholders_removed(self):
        text=(ROOT/'index.html').read_text()
        for marker in ['形式参考','TopSeed','Wanjun','liziniu','TEMPLATE /','待填 ·']:
            self.assertNotIn(marker,text)
    def test_site_declares_limitations(self):
        text = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn('本地模型 Demo 已可运行', text)
        self.assertIn('真实大模型接口未调用', text)
        self.assertIn('https://github.com/LlewynLune/ai-portfolio', text)
        self.assertIn('Python 实验仅本机运行', text)
    def test_redesign_content_and_reproducible_build(self):
        import importlib.util
        from html.parser import HTMLParser
        text=(ROOT/'index.html').read_text()
        self.assertIn('class="identity"', text)
        self.assertIn('自我介绍', text)
        self.assertIn('产品实践', text)
        self.assertIn('研究与工程项目', text)
        self.assertIn('"Trebuchet MS"',text)
        self.assertNotIn('class="hero"', text)
        self.assertNotIn('class="kpis"', text)
        self.assertNotIn('work-figure',text)
        self.assertEqual(text.count('class="work-row"'), 4)
        self.assertEqual(text.count('data-track="'), 14)
        self.assertEqual(text.count('class="research-group"'),4)
        self.assertEqual(text.count('AI-assisted</span>'),14)
        self.assertEqual(text.count('<style>'),1)
        self.assertEqual(text.count('[Demo]'),14)
        self.assertEqual(text.count('[Report]'),14)
        ids=[]
        class IdParser(HTMLParser):
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if 'id' in a: ids.append(a['id'])
        IdParser().feed(text)
        self.assertEqual(len(ids),len(set(ids)))
        spec=importlib.util.spec_from_file_location('resume_builder',ROOT/'scripts/build_resume_portfolio.py')
        builder=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        builder.build()
        self.assertEqual(text,(ROOT/'index.html').read_text())
    def test_evidence_trace_runs(self):
        result = subprocess.run(
            [sys.executable, 'examples/evidence-trace/evidence_trace.py',
             'examples/evidence-trace/sample-events.jsonl'],
            cwd=ROOT, check=True, text=True, capture_output=True)
        self.assertIn('Status path: waiting_for_review -> checked -> reviewed', result.stdout)
        self.assertIn('human=2', result.stdout)

if __name__ == '__main__':
    unittest.main()
