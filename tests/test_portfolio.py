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
    def test_bytedance_employment_owner_confirmed(self):
        import json
        data=json.loads((ROOT/'profile/resume.json').read_text());emp=data['employment']
        self.assertEqual(emp['company_en'],'ByteDance');self.assertEqual(emp['type'],'工作经历');self.assertEqual(set(emp['case_ids']),{c['id'] for c in data['cases']})
        text=(ROOT/'index.html').read_text();self.assertIn('ByteDance · 字节跳动',text);self.assertNotIn('TopSeed',text);self.assertNotIn('Research Intern',text)
        for c in data['cases']:
            case=(ROOT/'business-cases'/c['id']/'case.html').read_text();self.assertIn(c['title'],case);self.assertIn('工作经历',case);self.assertIn('本人提供并确认可公开的履历',case)
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
        self.assertIn('profile-info', text)
        self.assertIn('Work Experience', text)
        self.assertIn('Selected Research & Engineering', text)
        self.assertIn('background:#3d3d3d',text)
        self.assertIn('assets/portfolio/stars.jpg',text)
        self.assertIn('assets/portfolio/avatar.webp',text)
        self.assertNotIn('姓名标识 · 非个人照片',text)
        self.assertNotIn('Trebuchet MS',text)
        self.assertEqual(text.count('work-row"'), 4)
        self.assertEqual(text.count('data-track="'), 14)
        self.assertEqual(text.count('class="research-group"'),4)
        self.assertEqual(text.count('AI-assisted</span>'),14)
        self.assertEqual(text.count('<style>'),1)
        self.assertEqual(text.count('冻结实验报告重绘 · 点击放大'),14)
        self.assertIn('ntu-logo.png',text)
        self.assertIn('um-logo.png',text)
        self.assertNotIn('class="edu-symbol"',text)
        self.assertIn('image-dialog',text)
        self.assertIn('bytedance-logo.svg',text)
        self.assertEqual(text.count('class="experience-project work-row"'),4)
        self.assertNotIn('Product Case</span>',text)
        for item in ['stars.jpg','identity.svg','drawing-review.svg','standards-platform.svg','skills-knowledge.svg','force-aigc.svg']:
            self.assertTrue((ROOT/'assets/portfolio'/item).is_file())
        self.assertEqual(len(list((ROOT/'assets/portfolio').glob('*.webp'))),15)
        ids=[]
        class IdParser(HTMLParser):
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if 'id' in a: ids.append(a['id'])
                if tag=='img' and a.get('src'):
                    self_test.assertTrue((ROOT/a['src']).is_file(),a['src'])
        self_test=self
        IdParser().feed(text)
        self.assertEqual(len(ids),len(set(ids)))
        spec=importlib.util.spec_from_file_location('resume_builder',ROOT/'scripts/build_resume_portfolio.py')
        builder=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        builder.build()
        self.assertEqual(text,(ROOT/'index.html').read_text())
    def test_evidence_figures_match_frozen_reports(self):
        import json,hashlib,statistics
        records=json.loads((ROOT/'assets/portfolio/evidence-figures.json').read_text())
        self.assertEqual(len(records),14)
        for r in records:
            self.assertEqual(hashlib.sha256((ROOT/r['source']).read_bytes()).hexdigest(),r['sha256'])
            self.assertTrue((ROOT/'assets/portfolio'/(r['project']+'-evidence.svg')).is_file())
            for i,g in enumerate(r['groups']):
                for j,m in enumerate(r['models']):
                    hits=[x for x in r['rows'] if x[r['model_column']]==m and (r['group_column'] is None or x[r['group_column']]==g)]
                    self.assertAlmostEqual(statistics.mean(float(x[r['metric']]) for x in hits),r['values'][i][j])
    def test_evidence_trace_runs(self):
        result = subprocess.run(
            [sys.executable, 'examples/evidence-trace/evidence_trace.py',
             'examples/evidence-trace/sample-events.jsonl'],
            cwd=ROOT, check=True, text=True, capture_output=True)
        self.assertIn('Status path: waiting_for_review -> checked -> reviewed', result.stdout)
        self.assertIn('human=2', result.stdout)

if __name__ == '__main__':
    unittest.main()
