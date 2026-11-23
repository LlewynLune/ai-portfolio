import asyncio
import importlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

LAB=Path(__file__).resolve().parents[1]/"projects/reliability-lab"
sys.path.insert(0,str(LAB))
from reliability_lab.config import Config, manifest
from reliability_lab.engine import run_experiment, compare, quantile, RetryableError
from reliability_lab.store import Store

class ConfigTests(unittest.TestCase):
    def test_invalid_config(self):
        for args in ({"count":True},{"concurrency":0},{"seed":-1},{"base_ms":float('nan')},
                     {"profile":"other"},{"attempts":20},{"timeout_ms":float('inf')}):
            with self.subTest(args=args), self.assertRaises(ValueError): Config(**args)
    def test_fault_manifest_determinism(self):
        self.assertEqual(manifest(Config()),manifest(Config()))
        self.assertNotEqual(manifest(Config()),manifest(Config(seed=43)))
    def test_quantiles(self):
        self.assertIsNone(quantile([],.95))
        self.assertEqual(quantile([10],.95),10)
        self.assertEqual(quantile([0,10],.5),5)

class StoreTests(unittest.TestCase):
    def test_idempotence_and_conflict(self):
        s=Store()
        try:
            self.assertTrue(s.commit('x',1,{'v':1},True))
            self.assertFalse(s.commit('x',1,{'v':1},True))
            with self.assertRaises(ValueError): s.commit('x',1,{'v':2},True)
            self.assertEqual(s.stats('x')['duplicate_effects'],0)
        finally: s.close()
    def test_checkpoint_persistence(self):
        with tempfile.TemporaryDirectory() as temp:
            db=Path(temp)/'state.sqlite3'
            s=Store(db); s.bind('scope','a'); s.save('scope',1,'stage',{'v':1}); s.close()
            s=Store(db)
            try:
                self.assertEqual(s.get('scope',1,'stage'),{'v':1})
                with self.assertRaises(ValueError): s.bind('scope','b')
            finally: s.close()

class EngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_clean_success_and_concurrency(self):
        cfg=Config(count=8,profile='clean',base_ms=1)
        r=await run_experiment(cfg)
        self.assertEqual(r['summary']['succeeded'],8)
        self.assertLessEqual(r['summary']['peak_active'],4)
        self.assertEqual(r['summary']['attempts'],40)
    async def test_pair_same_manifest(self):
        pair=await compare(Config(count=6,profile='mixed',base_ms=1))
        self.assertEqual(len({r['manifest_hash'] for r in pair['results']}),1)
    async def test_transient_recovery(self):
        pair=await compare(Config(count=16,profile='transient',base_ms=1))
        b,r,_=pair['results']
        self.assertGreater(r['summary']['succeeded'],b['summary']['succeeded'])
        self.assertEqual(r['summary']['succeeded'],16)
    async def test_permanent_never_retried(self):
        r=await run_experiment(Config(count=16,profile='permanent',base_ms=1))
        self.assertGreater(r['summary']['status_counts'].get('permanent_failed',0),0)
        self.assertEqual(r['summary']['retries'],0)
    async def test_ack_loss_idempotency(self):
        pair=await compare(Config(count=16,profile='ack_loss',base_ms=1))
        b,r,s=pair['results']
        self.assertGreater(r['summary']['duplicate_effects'],0)
        self.assertEqual(s['summary']['duplicate_effects'],0)
        self.assertEqual(s['summary']['succeeded'],16)
        self.assertLess(b['summary']['succeeded'],16)
    async def test_resume_and_warm_run(self):
        s=Store(); cfg=Config(count=4,profile='clean',base_ms=1)
        try:
            paused=await run_experiment(cfg,store=s,pause_after='analyze')
            resumed=await run_experiment(cfg,store=s)
            warm=await run_experiment(cfg,store=s)
            self.assertEqual(paused['summary']['status_counts'],{'paused':4})
            self.assertEqual(resumed['summary']['checkpoint_hits'],12)
            self.assertEqual(resumed['summary']['attempts'],8)
            self.assertEqual(warm['summary']['checkpoint_hits'],20)
            self.assertEqual(warm['summary']['attempts'],0)
        finally: s.close()
    async def test_attempt_timeout_not_budget_timeout(self):
        class Slow:
            async def execute(self,*args): await asyncio.sleep(1)
        r=await run_experiment(Config(count=1,timeout_ms=5,budget_ms=200),policy='baseline',worker=Slow())
        self.assertEqual(r['tasks'][0]['status'],'retry_exhausted')
        self.assertEqual(r['summary']['attempt_timeouts'],1)
    async def test_budget_cancels_worker(self):
        class Slow:
            active=0
            async def execute(self,*args):
                self.active+=1
                try: await asyncio.sleep(1)
                finally: self.active-=1
        w=Slow()
        r=await run_experiment(Config(count=4,concurrency=2,timeout_ms=1000,budget_ms=20),worker=w)
        self.assertEqual(r['summary']['status_counts'],{'budget_exhausted':4})
        self.assertEqual(w.active,0)
        self.assertTrue(all(r['queue_ms']>0 for r in r['tasks'] if r['attempts']==0))
    async def test_output_contract_rejection(self):
        class Invalid:
            async def execute(self,*args): return {'valid':False}
        r=await run_experiment(Config(count=1),worker=Invalid())
        self.assertEqual(r['tasks'][0]['status'],'permanent_failed')
        self.assertEqual(r['summary']['retries'],0)
    async def test_invalid_policy(self):
        with self.assertRaises(ValueError): await run_experiment(Config(),policy='unknown')
    async def test_unknown_worker_errors_not_swallowed_as_success(self):
        class Broken:
            async def execute(self,*args): raise RuntimeError('bad implementation')
        r=await run_experiment(Config(count=1),worker=Broken())
        self.assertEqual(r['tasks'][0]['status'],'internal_failed')

class CliTests(unittest.TestCase):
    def test_process_restart_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            db=str(Path(temp)/'state.sqlite3')
            common=[sys.executable,'-m','reliability_lab','run','--count','2','--profile','clean','--database',db]
            subprocess.run(common+['--pause-after','analyze'],cwd=LAB,check=True,capture_output=True)
            result=subprocess.run(common,cwd=LAB,check=True,capture_output=True,text=True)
            import json
            summary=json.loads(result.stdout)
            self.assertEqual(summary['checkpoint_hits'],6)
            self.assertEqual(summary['attempts'],4)

if __name__ == '__main__': unittest.main()
