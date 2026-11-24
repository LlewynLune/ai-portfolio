import unittest,json,hashlib,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from videoguard.prediction_sets import quantile,fit_threshold,predict_sets,set_metrics,binomial_upper,risk_curve,aps_scores

class SetMethodTests(unittest.TestCase):
    def test_small_calibration_requires_infinite_threshold(self):
        self.assertEqual(quantile([.2,.4],alpha=.01),float('inf'))
    def test_quantile_finite_sample_rank(self):
        self.assertEqual(quantile(np.arange(9),alpha=.2),7)
    def test_invalid_probabilities(self):
        for p in [np.array([[1.,1.]]),np.array([[np.nan,0.]]),np.array([[-.1,1.1]])]:
            with self.assertRaises(ValueError):predict_sets(p,.5)
    def test_log_lac_order_equivalence(self):
        p=np.array([[.7,.2,.1],[.1,.6,.3],[.3,.1,.6],[.6,.3,.1]])
        y=np.array([0,1,2,0]);q=fit_threshold(p,y,'lac',.3);lq=fit_threshold(p,y,'log_lac',.3)
        self.assertTrue(np.array_equal(predict_sets(p,q,'lac'),predict_sets(p,lq,'log_lac')))
    def test_top1_is_superset_not_new_calibration(self):
        p=np.array([[.8,.15,.05],[.2,.3,.5]])
        a=predict_sets(p,.01,'lac');b=predict_sets(p,.01,'lac_top1')
        self.assertTrue(np.all(b>=a));self.assertTrue(np.all(b.sum(1)>=1))
    def test_crossing_keeps_first_above_threshold(self):
        p=np.array([[.6,.3,.1]])
        self.assertEqual(predict_sets(p,.7,'aps_crossing').tolist(),[[True,True,False]])
    def test_crossing_nonempty(self):
        p=np.array([[.6,.3,.1]])
        self.assertEqual(int(predict_sets(p,0,'aps_crossing').sum()),1)
    def test_randomized_requires_uniforms(self):
        with self.assertRaises(ValueError):fit_threshold(np.array([[.5,.5]]),np.array([0]),'aps_randomized')
    def test_randomized_exact_example(self):
        p=np.array([[.6,.3,.1]]);s=aps_scores(p,np.array([.5]))[0]
        self.assertTrue(np.allclose(s,[[.3,.75,.95]]))
    def test_uniform_repeatability(self):
        p=np.array([[.6,.3,.1],[.2,.5,.3]]);u=np.array([.3,.7]);a=predict_sets(p,.5,'aps_randomized',u)
        self.assertTrue(np.array_equal(a,predict_sets(p,.5,'aps_randomized',u)))
    def test_zero_error_exact_bound(self):
        self.assertAlmostEqual(binomial_upper(0,100),1-.05**.01,places=12)
        self.assertGreater(binomial_upper(0,3),.6)
    def test_no_observations_not_zero_risk(self):self.assertEqual(binomial_upper(0,0),1)
    def test_bound_increases_with_errors(self):
        self.assertLess(binomial_upper(2,100),binomial_upper(10,100))
    def test_bound_binomial_root(self):
        from videoguard.prediction_sets import log_binomial_cdf
        q=binomial_upper(3,30);self.assertAlmostEqual(np.exp(log_binomial_cdf(3,30,q)),.05,places=9)
    def test_risk_empty_and_multiple_testing(self):
        p=np.array([[.8,.2],[.7,.3]]);rows=risk_curve(p,np.array([0,1]),thresholds=[0,.9])
        self.assertIsNone(rows[1]['error_rate']);self.assertEqual(rows[1]['upper95'],1)
        self.assertGreaterEqual(rows[0]['simultaneous_upper95'],rows[0]['upper95'])

class DepthEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=ROOT/'artifacts/calibration-depth'
        cls.r=json.loads((cls.out/'results.json').read_text());cls.pools=json.loads((cls.out/'probability-pools.json').read_text())
    def test_model_still_frozen(self):
        self.assertEqual(hashlib.sha256((ROOT/'artifacts/model.json').read_bytes()).hexdigest(),self.r['model_sha256'])
    def test_methods_not_selected_after_test(self):
        self.assertEqual(self.r['methods'],['lac','log_lac','aps_randomized','aps_crossing','lac_top1'])
    def test_primary_threshold_recompute(self):
        c=self.pools['fresh_calibration'];p=np.array(c['probabilities']);y=np.array(c['labels']);u=np.array(c['uniforms'])
        for method,q in self.r['fresh_thresholds'].items():
            self.assertAlmostEqual(q,fit_threshold(p,y,method,u=u if method=='aps_randomized' else None),places=10)
    def test_primary_metric_recompute(self):
        for name,r in self.r['conditions'].items():
            pool=self.pools[name];p=np.array(pool['probabilities']);y=np.array(pool['labels']);u=np.array(pool['uniforms'])
            for method,q in self.r['fresh_thresholds'].items():
                s=predict_sets(p,q,method,u=u if method=='aps_randomized' else None);m=set_metrics(s,y,p)
                self.assertAlmostEqual(m['coverage'],r['sets'][method]['coverage'],places=10)
                self.assertAlmostEqual(m['mean_size'],r['sets'][method]['mean_size'],places=10)
    def test_24_independent_repeats_and_seeds(self):
        self.assertEqual(len(self.r['repeats']),24);seeds=[]
        for i in range(24):
            data=json.loads((self.out/f'repeat-{i:02d}.json').read_text())
            for split in ['calibration','test']:seeds.extend(r['seed'] for r in data[split]['records'])
        self.assertEqual(len(seeds),len(set(seeds)))
    def test_new_holdout_seed_separation(self):
        seeds=[r['seed'] for p in self.pools.values() for r in p['records']]
        self.assertEqual(len(seeds),len(set(seeds)))
    def test_legacy_failure_retained(self):
        old=json.loads((ROOT/'artifacts/results.json').read_text())
        self.assertEqual(old['conditions']['id']['prediction_set_coverage'],.835)
    def test_depth_hashes(self):
        for name,h in json.loads((self.out/'checksums.json').read_text()).items():
            self.assertEqual(hashlib.sha256((self.out/name).read_bytes()).hexdigest(),h)

if __name__=='__main__':unittest.main()
