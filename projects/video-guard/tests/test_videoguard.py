import unittest, json, sys, hashlib, shutil, subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from videoguard.data import make_clip,shift,content_hash,LAGS
from videoguard.features import extract,lag_features,baseline,signal_quality
from videoguard.model import loss_grad,forward,predict,softmax
from videoguard.calibration import metrics,conformal_sets,bootstrap_difference
from videoguard.media import assess,decode

class SignalTests(unittest.TestCase):
    def test_fixture_repeatability(self):
        a=make_clip(88);b=make_clip(88);self.assertEqual(content_hash(a),content_hash(b))
    def test_fixture_independence(self):
        self.assertNotEqual(content_hash(make_clip(88)),content_hash(make_clip(89)))
    def test_shift_not_circular(self):
        self.assertEqual(shift(np.array([1,2,3]),1).tolist(),[0,1,2])
        self.assertEqual(shift(np.array([1,2,3]),-1).tolist(),[2,3,0])
    def test_shift_too_large(self):self.assertFalse(shift(np.ones(3),4).any())
    def test_negative_and_positive_delay_sign(self):
        for lag in [-5,-2,0,3,5]:
            c=make_clip(98,lag);s=extract(c.frames,c.audio,20,8000)
            self.assertEqual(baseline(s),lag)
    def test_features_label_blind(self):
        c=make_clip(98);s=extract(c.frames,c.audio,20,8000);a=lag_features(s)
        c.delay=123;c.events[:]=0;c.seed=0
        self.assertTrue(np.array_equal(a,lag_features(extract(c.frames,c.audio,20,8000))))
    def test_features_finite(self):
        for condition in ['id','silent','noise','periodic','distractor','drift','missing','long']:
            c=make_clip(91,condition=condition);x=lag_features(extract(c.frames,c.audio,20,8000))
            self.assertEqual(x.shape,(13,12));self.assertTrue(np.isfinite(x).all())
    def test_silent_not_scorable(self):
        c=make_clip(99,condition='silent');self.assertFalse(signal_quality(extract(c.frames,c.audio,20,8000))['scorable'])
    def test_short_audio_rejected(self):
        c=make_clip(77)
        with self.assertRaises(ValueError):extract(c.frames,c.audio[:20],20,8000)
    def test_nan_rejected(self):
        c=make_clip(77);c.audio[0]=np.nan
        with self.assertRaises(ValueError):extract(c.frames,c.audio,20,8000)
    def test_invalid_condition(self):
        with self.assertRaises(ValueError):make_clip(3,condition='bad')
    def test_media_nonfile_rejected(self):
        with self.assertRaises(ValueError):decode('https://example.com/clip.mp4')

class GradientTests(unittest.TestCase):
    def test_finite_difference_all_trainable_types(self):
        rng=np.random.default_rng(5);X=rng.normal(size=(3,13,12));y=np.array([1,3,9])
        p={'mean':np.zeros(12),'scale':np.ones(12),'w1':rng.normal(0,.1,(12,4)),
           'b1':np.zeros(4),'w2':rng.normal(0,.1,(4,1)),'b2':np.zeros(1)}
        _,g=loss_grad(X,y,p)
        for k,index in [('w1',(3,2)),('w2',(1,0)),('b1',(2,)),('b2',(0,))]:
            original=p[k][index];eps=1e-5
            p[k][index]=original+eps;plus=loss_grad(X,y,p)[0]
            p[k][index]=original-eps;minus=loss_grad(X,y,p)[0]
            p[k][index]=original
            self.assertAlmostEqual((plus-minus)/(2*eps),g[k][index],places=6)
    def test_dual_tower_finite_difference(self):
        from videoguard.contrastive import loss_grad as cg
        rng=np.random.default_rng(42);V=rng.normal(size=(2,3,24));A=rng.normal(size=(2,13,3,24));y=np.array([1,9]);p={}
        for prefix in ['v','a']:
            p.update({prefix+'w1':rng.normal(0,.1,(24,4)),prefix+'b1':np.zeros(4),prefix+'w2':rng.normal(0,.1,(4,3)),prefix+'b2':np.zeros(3)})
        _,g=cg(V,A,y,p)
        for k,index in [('vw1',(3,2)),('aw1',(4,1)),('vw2',(1,0)),('aw2',(2,1)),('vb1',(2,)),('ab2',(1,))]:
            original=p[k][index];eps=1e-6;p[k][index]=original+eps;plus=cg(V,A,y,p)[0];p[k][index]=original-eps;minus=cg(V,A,y,p)[0];p[k][index]=original
            self.assertAlmostEqual((plus-minus)/(2*eps),g[k][index],places=5)
    def test_probability_normalization(self):
        self.assertTrue(np.allclose(softmax(np.arange(26).reshape(2,13)).sum(1),1))
    def test_temperature_preserves_argmax(self):
        z=np.arange(26).reshape(2,13);self.assertTrue(np.array_equal(softmax(z).argmax(1),softmax(z/3).argmax(1)))
    def test_perfect_metrics(self):
        r=metrics(np.eye(3),np.arange(3));self.assertEqual(r['accuracy'],1);self.assertEqual(r['ece_10_equal_width'],0)
    def test_conformal_sets_keep_ties(self):
        p=np.ones((2,13))/13;self.assertEqual(int(conformal_sets(p,1-1/13).sum()),26)
    def test_paired_bootstrap_identical(self):
        r=bootstrap_difference([1,0,1],[1,0,1]);self.assertEqual(r['ci_95_percentile'],[0,0])

class FrozenEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=json.loads((ROOT/'artifacts/model.json').read_text())
        cls.results=json.loads((ROOT/'artifacts/results.json').read_text())
    def test_model_hash(self):
        self.assertEqual(hashlib.sha256((ROOT/'artifacts/model.json').read_bytes()).hexdigest(),self.results['model_sha256'])
    def test_disjoint_manifest(self):
        groups=json.loads((ROOT/'artifacts/split-manifest.json').read_text())
        seeds=[];hashes=[]
        for rows in groups.values():
            seeds.extend(r['seed'] for r in rows);hashes.extend(r['media_sha256'] for r in rows)
        self.assertEqual(len(set(seeds)),len(seeds));self.assertEqual(len(set(hashes)),len(hashes))
    def test_three_training_seeds(self):self.assertEqual([r['optimizer_seed'] for r in self.results['runs']],[7,19,31])
    def test_no_cherry_picked_ood(self):self.assertEqual(len(self.results['conditions']),8)
    def test_frozen_inference_parity(self):
        for e in json.loads((ROOT/'artifacts/examples.json').read_text()):
            p=predict(np.array(e['features'])[None],self.model['parameters'],self.model['temperature'])[0]
            self.assertTrue(np.allclose(p,e['probabilities'],atol=1e-10))
    def test_test_rows_recompute_accuracy(self):
        rows=json.loads((ROOT/'artifacts/test-predictions.json').read_text())
        acc=np.mean([r['true_delay']==r['pred_delay'] for r in rows])
        self.assertAlmostEqual(acc,self.results['conditions']['id']['accuracy'],places=12)
    def test_silent_forces_review(self):
        c=make_clip(884,condition='silent');r=assess(extract(c.frames,c.audio,20,8000),self.model)
        self.assertEqual(r['decision'],'review')
    def test_documents(self):
        for file in ['README.md','METHOD.md','MODEL_CARD.md','CONTRIBUTIONS.md','RESEARCH.md','demo.html']:
            self.assertTrue((ROOT/file).is_file(),file)
    def test_code_checksums(self):
        for name,h in json.loads((ROOT/'artifacts/code-checksums.json').read_text()).items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),h,name)
    def test_json_import_safety_and_invalid_input(self):
        from build_demo import ENGINE
        report=json.loads((ROOT/'artifacts/local-report-example.json').read_text())
        code=ENGINE+'const R='+json.dumps(report)+';let s=validateReport(R);let safe=importSafety({accept:true},true);if(safe.accept||safe.decision!=="review")throw Error("unsafe");let failed=false;try{validateReport({signals:{visual:[1]}})}catch(e){failed=true}if(!failed)throw Error("invalid accepted");console.log("ok");'
        subprocess.run(['node','--input-type=commonjs'],input=code,text=True,check=True,capture_output=True)
    def test_full_js_parity(self):
        subprocess.run([sys.executable,str(ROOT/'check_js_parity.py')],check=True,capture_output=True)
    def test_dual_tower_three_seeds(self):
        r=json.loads((ROOT/'artifacts/contrastive-results.json').read_text());self.assertEqual([x['seed'] for x in r['seeds']],[43,57,71])
    def test_artifact_checksums(self):
        for name,h in json.loads((ROOT/'artifacts/checksums.json').read_text()).items():
            self.assertEqual(hashlib.sha256((ROOT/'artifacts'/name).read_bytes()).hexdigest(),h,name)

if __name__=='__main__':unittest.main()
