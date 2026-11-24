import unittest,json,hashlib,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from videoguard.drift_data import make_drift
from videoguard.data import content_hash
from videoguard.features import extract
from videoguard.drift import detect,match_events,lag_trajectory,summarize

class DriftMechanismTests(unittest.TestCase):
    def row(self,end,lag,conf=1):return {'start':end-32,'end':end,'center':end-16,'energy':.1,'mlp_lag':lag,'mlp_confidence':conf}
    def test_generator_deterministic(self):self.assertEqual(content_hash(make_drift(77).clip),content_hash(make_drift(77).clip))
    def test_change_labels_match_delay_track(self):
        for g in ['stable','step','negative','ramp','multiple','quiet_gap','silent']:
            f=make_drift(88,g);self.assertEqual((np.flatnonzero(np.diff(f.delay_track)!=0)+1).tolist(),f.change_frames)
    def test_stable_no_truth(self):self.assertEqual(make_drift(88,'stable').change_frames,[])
    def test_multiple_truth(self):self.assertEqual(make_drift(88,'multiple').change_frames,[50,105])
    def test_quiet_gap_not_faked_observable(self):
        f=make_drift(88,'quiet_gap');c=f.change_frames[0];self.assertFalse(f.source_events[c-22:c+25].any())
    def test_confirmation_alarm_after_estimate(self):
        rows=[self.row(32,0),self.row(36,0),self.row(40,3),self.row(44,3)]
        a=detect(rows,confidence=.9,min_jump=2,patience=2)
        self.assertEqual(len(a),1);self.assertEqual(a[0]['alarm_frame'],44);self.assertEqual(a[0]['estimated_frame'],24)
    def test_low_evidence_clears_candidate(self):
        rows=[self.row(32,0),self.row(36,0),self.row(40,3),self.row(44,3,.1),self.row(48,0)]
        self.assertEqual(detect(rows,patience=2),[])
    def test_stable_traj_no_alarm(self):self.assertEqual(detect([self.row(e,0) for e in range(32,160,4)]),[])
    def test_duplicate_alarm_false_positive(self):
        a=[{'estimated_frame':50,'alarm_frame':66},{'estimated_frame':50,'alarm_frame':70}];s=match_events([50],a)
        self.assertEqual((s['tp'],s['fp'],s['fn']),(1,1,0))
    def test_early_alarm_not_credited(self):
        s=match_events([50],[{'estimated_frame':50,'alarm_frame':49}]);self.assertEqual(s['tp'],0)
    def test_tolerance_edge(self):
        self.assertEqual(match_events([50],[{'estimated_frame':66,'alarm_frame':70}],16)['tp'],1)
        self.assertEqual(match_events([50],[{'estimated_frame':67,'alarm_frame':70}],16)['tp'],0)
    def test_maximum_one_to_one_matching(self):
        a=[{'estimated_frame':45,'alarm_frame':100},{'estimated_frame':60,'alarm_frame':100}]
        self.assertEqual(match_events([50,70],a,20)['tp'],2)
    def test_causal_prefix_invariance(self):
        model=json.loads((ROOT/'artifacts/model.json').read_text());f=make_drift(991);s=extract(f.clip.frames,f.clip.audio,20,8000)
        a=lag_trajectory(s,model);short={k:v[:80] for k,v in s.items()};b=lag_trajectory(short,model)
        self.assertEqual([r for r in a if r['end']<=80],b)
    def test_detector_truth_blind(self):
        rows=[self.row(e,0 if e<60 else 3) for e in range(32,100,4)];a=detect(rows)
        self.assertEqual(a,detect(rows));self.assertTrue(all('truth' not in str(x) for x in a))

class DriftEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=ROOT/'artifacts/drift-localization';cls.r=json.loads((cls.d/'results.json').read_text())
    def test_frozen_model(self):self.assertEqual(hashlib.sha256((ROOT/'artifacts/model.json').read_bytes()).hexdigest(),self.r['model_sha256'])
    def test_all_ten_groups(self):self.assertEqual(len(self.r['groups']),10)
    def test_all_three_methods(self):self.assertEqual(self.r['methods'],['raw','onset','mlp'])
    def test_metrics_recompute(self):
        for group in self.r['groups']:
            rows=json.loads((self.d/f'{group}-records.json').read_text())
            for m,cfg in self.r['configs'].items():
                a=summarize(rows,m,cfg);b=self.r['groups'][group][m]
                for k in ['tp','fp','fn','f1','recall']:self.assertAlmostEqual(a[k],b[k],places=12)
    def test_no_validation_test_overlap(self):
        seen=set()
        files=['validation-records.json']+[f'{g}-records.json' for g in self.r['groups']]+[f'repeat-{i}.json' for i in range(3)]
        for f in files:
            for r in json.loads((self.d/f).read_text()):self.assertNotIn(r['seed'],seen);seen.add(r['seed'])
    def test_sweep_retained(self):self.assertEqual(set(self.r['tolerance_sweep']),{'200','400','800','1200'})
    def test_three_independent_repeats(self):self.assertEqual(len(self.r['repeats']),3)
    def test_hashes(self):
        for name,h in json.loads((self.d/'checksums.json').read_text()).items():self.assertEqual(hashlib.sha256((self.d/name).read_bytes()).hexdigest(),h)
if __name__=='__main__':unittest.main()
