"""Source-dependent independent evidence checks, not predictive model performance tests."""
import os, sys, json, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from r38_source_decision_reanalysis import parse_source,analyze,metrics,SOURCE_SHA256

PATH=Path(os.environ['R38_SOURCE_FILE']) if 'R38_SOURCE_FILE' in os.environ else None
class EvidenceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if PATH is None:
            raise unittest.SkipTest('R38_SOURCE_FILE not provided; source data are not publicly redistributed')
        cls.labels,cls.source=parse_source(PATH)
        cls.a=analyze(PATH)
    def test_admitted(self):self.assertEqual(self.a['status'],'ADMITTED_PRIMARY_RECORD_LEVEL_REANALYSIS')
    def test_sha(self):self.assertEqual(self.source['file_sha256'],SOURCE_SHA256)
    def test_n(self):self.assertEqual(self.source['rows'],1003)
    def test_positives(self):self.assertEqual(self.a['reference_positives'],25)
    def test_negatives(self):self.assertEqual(self.a['reference_negatives'],978)
    def test_a1(self):self.assertEqual(tuple(self.a['reviewer_matrices']['A1'][x] for x in ('tp','fp','fn','tn')),(25,1,0,977))
    def test_a2(self):self.assertEqual(tuple(self.a['reviewer_matrices']['A2'][x] for x in ('tp','fp','fn','tn')),(22,7,3,971))
    def test_b1(self):self.assertEqual(tuple(self.a['reviewer_matrices']['B1'][x] for x in ('tp','fp','fn','tn')),(25,1,0,977))
    def test_b2(self):self.assertEqual(tuple(self.a['reviewer_matrices']['B2'][x] for x in ('tp','fp','fn','tn')),(23,3,2,975))
    def test_each_matrix_sums(self):self.assertTrue(all(sum(m[k] for k in ('tp','fp','fn','tn'))==1003 for m in self.a['reviewer_matrices'].values()))
    def test_all_assisted_retain_25(self):self.assertEqual([self.a['reviewer_matrices'][x]['fn'] for x in ('A1','B1')],[0,0])
    def test_error_union15(self):self.assertEqual(self.a['error_overlap']['distinct_records_with_at_least_one_error'],15)
    def test_error_events17(self):self.assertEqual(self.a['error_overlap']['sum_of_reviewer_error_events'],17)
    def test_assisted_fp_disjoint(self):self.assertEqual(self.a['error_overlap']['assisted_pair_fp_overlap'],0)
    def test_unassisted_fn_disjoint(self):self.assertEqual(self.a['error_overlap']['unassisted_pair_fn_overlap'],0)
    def test_A1_A2_disagreements(self):self.assertEqual(next(x['decision_disagreements'] for x in self.a['reviewer_pair_disagreements'] if x['reviewer_a']=='A1' and x['reviewer_b']=='A2'),11)
    def test_B1_B2_disagreements(self):self.assertEqual(next(x['decision_disagreements'] for x in self.a['reviewer_pair_disagreements'] if x['reviewer_a']=='B1' and x['reviewer_b']=='B2'),4)
    def test_virtual_assisted_intersection(self):self.assertEqual([(x['tp'],x['fp'],x['fn']) for x in self.a['counterfactual_consensus_policies'] if x['first']=='A1' and x['rule']=='AND'],[(25,0,0)])
    def test_virtual_unassisted_union(self):self.assertEqual([(x['tp'],x['fp'],x['fn']) for x in self.a['counterfactual_consensus_policies'] if x['first']=='A2' and x['rule']=='OR'],[(25,9,0)])
    def test_a1_to_a2_override(self):self.assertEqual([(x['tp'],x['fp'],x['fn']) for x in self.a['counterfactual_include_only_override_policies'] if x['first_stage']=='A1' and x['hypothetical_checker']=='A2'],[(22,0,3)])
    def test_a1_to_b2_override(self):self.assertEqual([(x['tp'],x['fp'],x['fn']) for x in self.a['counterfactual_include_only_override_policies'] if x['first_stage']=='A1' and x['hypothetical_checker']=='B2'],[(23,0,2)])
    def test_one_stage_vs_replay_precision(self):
        base=self.a['reviewer_matrices']['A1']['precision']
        assert base<1
        v=[x for x in self.a['counterfactual_include_only_override_policies'] if x['first_stage']=='A1']
        self.assertTrue(all(x['precision']>base and x['recall']<1 for x in v))
    def test_only_virtual_not_observed(self):self.assertTrue(all(x['kind'].startswith('COUNTERFACTUAL') for x in self.a['counterfactual_include_only_override_policies']))
    def test_source_rights(self):self.assertEqual(self.a['original_dataset_license'],'CC BY-NC 4.0')
    def test_time_bounded(self):self.assertEqual(self.a['published_reviewer_times_minutes_not_per_record']['A1'],116)
    def test_no_sequential_measurement(self):self.assertTrue(any('not actually observed' in x for x in self.a['limitations']))

if __name__=='__main__':unittest.main(verbosity=2)
