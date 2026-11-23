import asyncio
import hashlib
import json
from pathlib import Path
import sys
import unittest

LAB=Path(__file__).resolve().parents[1]/'projects/reliability-lab'
sys.path.insert(0,str(LAB))
from reliability_lab.config import Config,SLOW_DELAY_MS
from reliability_lab.engine import run_experiment
from reliability_lab.retrieval import rank,quality_report,RetrievalWorker,DOCUMENTS
from reliability_lab.store import Store
from reliability_lab.advanced import crash_probe

class RetrievalTests(unittest.TestCase):
    def test_known_query(self):
        self.assertEqual(rank('idempotency duplicate acknowledgement')[0]['id'],'idempotency')
    def test_labels_and_ranking_bounds(self):
        ids={d['id'] for d in DOCUMENTS}
        r=quality_report()
        for q in r['questions']: self.assertTrue(set(q['relevant'])<=ids)
        for m in r['metrics']:
            self.assertTrue(0<=m['recall3']<=1 and 0<=m['mrr']<=1)
    def test_challenge_is_not_hidden(self):
        metrics=[m for m in quality_report()['metrics'] if m['split']=='challenge']
        self.assertEqual(len(metrics),2)
        self.assertTrue(any(m['mrr']<1 for m in metrics))
    def test_unknown_method(self):
        with self.assertRaises(ValueError):rank('some query','other')
    def test_fixed_slow_delay(self): self.assertEqual(SLOW_DELAY_MS,140)

class IntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_actual_retrieval_output(self):
        cfg=Config(count=4,profile='clean',base_ms=1);store=Store()
        try:
            r=await run_experiment(cfg,store=store,worker=RetrievalWorker(cfg,store,'experiment',True))
            self.assertEqual(r['summary']['succeeded'],4)
            self.assertTrue(all(t['output']['citations'] for t in r['tasks']))
            self.assertTrue(r['workload'].startswith('authored_local_bm25'))
        finally:store.close()
    async def test_worker_switch_refuses_cached_outputs(self):
        cfg=Config(count=1,profile='clean',base_ms=1);store=Store()
        try:
            await run_experiment(cfg,store=store)
            with self.assertRaises(ValueError):
                await run_experiment(cfg,store=store,worker=RetrievalWorker(cfg,store,'experiment',True))
        finally:store.close()

class CrashTests(unittest.TestCase):
    def test_checkpoint_survives_abrupt_child_exit(self):
        p=crash_probe('after_checkpoint')
        self.assertEqual(p['child_exit_code'],73)
        self.assertEqual(p['integrity_check'],'ok')
        self.assertEqual(p['recovered']['summary']['succeeded'],4)
        self.assertGreaterEqual(p['recovered']['summary']['checkpoint_hits'],3)
    def test_commit_without_checkpoint_replays_without_idempotence(self):
        p=crash_probe('after_commit','retry')
        self.assertEqual(p['recovered']['summary']['duplicate_effects'],1)
    def test_commit_without_checkpoint_is_idempotent(self):
        p=crash_probe('after_commit','resilient')
        self.assertEqual(p['recovered']['summary']['duplicate_effects'],0)
        self.assertEqual(p['recovered']['summary']['succeeded'],4)

class AdvancedEvidenceTests(unittest.TestCase):
    def test_advanced_integrity_and_code(self):
        folder=LAB/'results/advanced'
        for name,digest in json.loads((folder/'checksums.json').read_text()).items():
            self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),digest,name)
        report=json.loads((folder/'advanced.json').read_text())
        for name,digest in report['code_sha256'].items():
            self.assertEqual(hashlib.sha256((LAB/'reliability_lab'/name).read_bytes()).hexdigest(),digest,name)
    def test_sweep_pairs_have_same_faults(self):
        data=json.loads((LAB/'results/advanced/sweep.json').read_text())
        for seed in (42,43,44):
            runs=[r for r in data['runs'] if r['config']['seed']==seed]
            self.assertEqual(len(runs),9)
            self.assertEqual(len({r['manifest_hash'] for r in runs}),1)
            for r in runs:
                self.assertEqual(r['summary']['succeeded'],sum(t['status']=='succeeded' for t in r['tasks']))

if __name__=='__main__':unittest.main()
