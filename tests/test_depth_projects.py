"""Depth correctness, frozen-export parity, scope, hash, API and report tests.
All new numerical tests use NumPy, not torch/pickle. No training dependency.
"""
import unittest,sys,json,hashlib,importlib.util,threading,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'projects'))
try:
    import numpy as np
    from depth_support import Attention,affine,softmax,generate_lookup,metrics
except ImportError:np=None

def module(folder):
    spec=importlib.util.spec_from_file_location('depth_'+folder.replace('-','_'),ROOT/'projects'/folder/'depth.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
@unittest.skipIf(np is None,'NumPy required')
class DepthTests(unittest.TestCase):
    def test_14_evidence_reports_and_source_hashes(self):
        reports=list(ROOT.glob('projects/*/artifacts/depth/results.json'));self.assertEqual(len(reports),14)
        for p in reports:
            r=json.loads(p.read_text());self.assertGreater(len(r['records']),0);self.assertGreater(len(r['metrics']),0)
            for path,digest in r['source_hashes'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
            self.assertTrue((p.parents[2]/'depth.py').exists());self.assertTrue((p.parents[2]/'depth-demo.html').exists())
    def test_new_lookup_excludes_prior_ids(self):
        x,y=generate_lookup(20,44);new,yy=generate_lookup(20,44,exclude=[json.dumps(v.tolist()) for v in x]);self.assertFalse(set(map(tuple,x))&set(map(tuple,new)))
    def test_attention_export_matches_frozen_examples(self):
        for name in ['tiny-attention','lora-lab','dpo-lab']:
            model=json.loads((ROOT/'projects'/name/'artifacts/model.json').read_text());e=json.loads((ROOT/'projects'/name/'artifacts/results.json').read_text())['examples'];a=Attention(model)
            for r in e[:4]:self.assertLess(np.max(abs(softmax(a.forward(r['tokens'])[0,-1])-r['probabilities'])),2e-5,name)
    def test_causal_prefix_and_cache(self):
        m=json.loads((ROOT/'projects/spec-decode/artifacts/model.json').read_text())['target'];a=Attention(m);tokens=[1,3,5,2,4,6];full=a.forward(tokens)[0];cache=None
        for i,t in enumerate(tokens):
            self.assertLess(np.max(abs(full[i]-a.forward(tokens[:i+1])[0,-1])),1e-10)
            z,cache=a.step(t,cache);self.assertLess(np.max(abs(z-full[i])),1e-10)
        self.assertEqual(len(cache['k']),6)
    def test_invalid_model_inputs_rejected(self):
        m=json.loads((ROOT/'projects/tiny-attention/artifacts/model.json').read_text());a=Attention(m)
        for tokens in [[],[19],[1.5],list(range(17))]:
            with self.assertRaises(ValueError):a.forward(tokens)
    def test_lora_delta_merge(self):
        base=json.loads((ROOT/'projects/tiny-attention/artifacts/model.json').read_text());adapt=json.loads((ROOT/'projects/lora-lab/artifacts/model.json').read_text());lo=module('lora-lab');x,y=generate_lookup(20,1450);self.assertLess(np.max(abs(Attention(lo.interpolate(base,adapt,1)).forward(x)-Attention(adapt).forward(x))),3e-5)
    def test_textguard_invariance_and_parity(self):
        a=module('textguard');m=json.loads((ROOT/'projects/textguard/artifacts/model.json').read_text());e=json.loads((ROOT/'projects/textguard/artifacts/results.json').read_text())['examples']
        for r in e:
            p,n=a.infer(r['text'],m);self.assertAlmostEqual(p,r['probability'],places=10);self.assertAlmostEqual(p,a.infer(r['text'].upper()+'!!!',m)[0],places=10)
        self.assertEqual(a.infer('你好明天开会',m)[1],0)
        with self.assertRaises(ValueError):a.infer('a'*2001,m)
    def test_citerag_dedup_and_no_fabricated_citation(self):
        m=module('cite-rag');docs=m.base.DOCS;flood=docs+[dict(d,id=d['id']+'-duplicate'+str(i)) for d in docs for i in range(3)];a=m.search('retry checkpoint',docs,True);b=m.search('retry checkpoint',flood,True)
        self.assertEqual([x['id'] for x in a],[x['id'] for x in b]);self.assertEqual(len(b),len(docs));self.assertTrue(all('fingerprint' in r for r in b))
        self.assertEqual(m.search('retry',[],True),[])
    def test_moe_capacity_enforced(self):
        a=module('moe-lab');m=json.loads((ROOT/'projects/moe-lab/artifacts/model.json').read_text());x=np.zeros((32,2));out,routes,admitted,counts,p=a.dispatch(x,m,.5)
        self.assertTrue((counts<=4).all());self.assertEqual(sum(counts),sum(admitted));self.assertTrue((out[~admitted]==0).all());self.assertTrue((routes[~admitted]==-1).all())
    def test_moe_matches_frozen_example(self):
        a=module('moe-lab');m=json.loads((ROOT/'projects/moe-lab/artifacts/model.json').read_text());e=json.loads((ROOT/'projects/moe-lab/artifacts/results.json').read_text())['examples']
        for r in e:
            o,route,_,_,p=a.dispatch([r['input']],m);self.assertAlmostEqual(float(o[0]),r['output'][0],places=5);self.assertEqual(int(route[0]),r['route'])
    def test_specdecode_exact_cached_and_speculated(self):
        a=module('spec-decode');m=json.loads((ROOT/'projects/spec-decode/artifacts/model.json').read_text());target=Attention(m['target']);draft=Attention(m['draft'])
        for p in [[0,1,2,3],[7,0,6,2],[2,4,0,6]]:
            baseline,_=a.greedy(target,p);cached,_=a.greedy(target,p,cached=True);self.assertEqual(baseline,cached)
            for k in [1,2,4]:out,stats=a.speculative(target,draft,p,k=k);self.assertEqual(out,baseline)
    def test_rc_nuisance_fit(self):
        a=module('circuit-id');tau=2.5;v=.8*(1-np.exp(-a.TIME/tau))+.15;t,params,res=a.fit_curve(v,True);self.assertAlmostEqual(t,tau,places=4);self.assertAlmostEqual(params[0],.8,places=4);self.assertAlmostEqual(params[1],.15,places=4)
    def test_missing_pilots_refuse_underdetermined(self):
        a=module('channel-est');H,z=a.synth(20,3);valid=np.array([1,1,0,0,0,0,0,0],bool)
        with self.assertRaises(ValueError):a.missing_ls(z,valid)
        self.assertEqual(a.missing_ls(z,np.ones(8,bool)).shape,H.shape)
    def test_latency_matching_no_early_or_double_credit(self):
        a=module('video-guard');alarms=[dict(estimated_frame=60,alarm_frame=75),dict(estimated_frame=60,alarm_frame=76)]
        self.assertEqual(a.latency_match([60],alarms,16,20),dict(tp=1,fp=1,fn=0));self.assertEqual(a.latency_match([60],alarms,16,10),dict(tp=0,fp=2,fn=1));self.assertEqual(a.latency_match([60],[dict(estimated_frame=60,alarm_frame=59)],16,20)['tp'],0)
    def test_affine_export_finite_dimension(self):
        m=json.loads((ROOT/'projects/circuit-id/artifacts/model.json').read_text());e=json.loads((ROOT/'projects/circuit-id/artifacts/results.json').read_text())['examples'][0];self.assertAlmostEqual(np.exp(affine(e['input'],m).item()),e['output'][0],places=8)
        with self.assertRaises(ValueError):affine([float('nan')]*32,m)
    def test_report_no_fake_zero_nll(self):
        self.assertNotIn('nll',metrics([dict(correct=True,loss=0)]))
    def test_local_api_validation_and_pagination(self):
        spec=importlib.util.spec_from_file_location('depth_api',ROOT/'scripts/depth_server.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
        result=a.query('textguard',limit=3);self.assertEqual(len(result['rows']),3)
        with self.assertRaises(ValueError):a.query('../outside')
        with self.assertRaises(ValueError):a.query('textguard',limit=201)
    def test_local_http_readonly(self):
        spec=importlib.util.spec_from_file_location('depth_http',ROOT/'scripts/depth_server.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);server=a.ThreadingHTTPServer(('127.0.0.1',0),a.Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url='http://127.0.0.1:'+str(server.server_port)
        try:
            with urllib.request.urlopen(url+'/health') as r:self.assertEqual(json.load(r)['status'],'ok')
            with urllib.request.urlopen(url+'/api/evidence?project=vision-cal&limit=2') as r:self.assertEqual(len(json.load(r)['rows']),2)
            try:
                urllib.request.urlopen(urllib.request.Request(url+'/api/evidence',data=b'{}'))
            except urllib.error.HTTPError as error:
                self.assertEqual(error.code,405);error.close()
            else:self.fail('POST must be rejected')
        finally:server.shutdown();server.server_close()
if __name__=='__main__':unittest.main()
