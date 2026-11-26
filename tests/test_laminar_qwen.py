"""CPU verification of logged Qwen experiments; not a full GPU-training test."""
import unittest,sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'projects/laminar-lab';sys.path.insert(0,str(P))
from laminar_lab.qwen_audit import verify
class QwenTests(unittest.TestCase):
    def test_samples_reward_and_evaluation(self):
        d=verify(P/'artifacts');self.assertEqual(len(d['runs']),12);self.assertEqual(sum(r['action_draws'] for r in d['runs']),9216);self.assertEqual(d['dataset_exact_or_swapped_overlap'],0)
    def test_final_adapters_were_reloaded(self):
        d=json.loads((P/'artifacts/qwen-reload.json').read_text());self.assertEqual(len(d['results']),6)
        for r in d['results']:self.assertEqual(r['probes'],128);self.assertEqual(r['decisions_matching'],128);self.assertLessEqual(r['max_abs_probability_error'],1e-5)
    def test_original_runner_preserved(self):
        d=json.loads((P/'artifacts/qwen-policy/summary.json').read_text());self.assertEqual(d['source_sha256'],hashlib.sha256((P/'artifacts/qwen-policy/runner-original.py').read_bytes()).hexdigest())
    def test_live_and_qwen_scopes_separate(self):
        text=(P/'QWEN_STUDY.md').read_text();self.assertIn('contextual bandit',text);self.assertIn('没有',text);self.assertIn('32/64',text)
if __name__=='__main__':unittest.main()
