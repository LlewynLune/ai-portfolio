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
    def test_no_fabricated_results(self):
        for name in checker.REQUIRED:
            if name in {'projects/product-workflow/README.md', 'projects/research-evaluation/README.md', 'projects/infra-runtime/README.md'}:
                self.assertIn('待补', (ROOT / name).read_text(encoding='utf-8'))
    def test_site_declares_limitations(self):
        text = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn('没有可运行模型 Demo', text)
        self.assertIn('尚未连接 GitHub', text)
    def test_evidence_trace_runs(self):
        result = subprocess.run(
            [sys.executable, 'examples/evidence-trace/evidence_trace.py',
             'examples/evidence-trace/sample-events.jsonl'],
            cwd=ROOT, check=True, text=True, capture_output=True)
        self.assertIn('Status path: waiting_for_review -> checked -> reviewed', result.stdout)
        self.assertIn('human=2', result.stdout)

if __name__ == '__main__':
    unittest.main()
