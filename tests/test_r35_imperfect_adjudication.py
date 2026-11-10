"""Unit and adverse-case tests for a deterministic, source-conditional envelope."""
import unittest
import sys
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_r35_imperfect_adjudication import audit,state

class R35HumanOverrideEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.a=audit()
    def test_same_original_reference(self):self.assertEqual(self.a['baseline']['n'],3796)
    def test_source_policy_includes_and_correctable_fp(self):
        self.assertEqual([(p['flagged_predicted_includes'],p['source_perfect_correction_available_fp']) for p in self.a['policies']],[(145,102),(221,135)])
    def test_correct_tp_risk(self):self.assertEqual([p['source_flagged_originally_correct_tp_at_risk'] for p in self.a['policies']],[43,86])
    def test_all_states_exhaustive(self):self.assertEqual(self.a['lattice_states_enumerated'],16364)
    def test_one_error_reduces_recall_but_can_increase_precision(self):
        b=state(284,3,167,3342,0,0); s=state(284,3,167,3342,102,1)
        self.assertLess(s['recall'],b['recall']);self.assertGreater(s['precision'],b['precision'])
        self.assertEqual((s['tp'],s['fn'],s['fp'],s['tn']),(283,4,65,3444))
    def test_source_perfect_correction_matches_source(self):
        self.assertEqual([state(284,3,167,3342,p['source_perfect_correction_available_fp'],0)['fp'] for p in self.a['policies']],[65,32])
    def test_thresholds_80(self):self.assertEqual([p['fp_corrected_needed_for_precision_80pct_if_no_new_error'] for p in self.a['policies']],[96,96])
    def test_85_not_attainable_smaller_policy(self):self.assertEqual([p['fp_corrected_needed_for_precision_85pct_if_no_new_error'] for p in self.a['policies']],[None,117])
    def test_90_not_attainable_under_either_policy(self):self.assertTrue(all(p['fp_corrected_needed_for_precision_90pct_if_no_new_error'] is None for p in self.a['policies']))
    def test_recall_98_loss_allowance(self):self.assertEqual([p['max_wrong_overrides_to_keep_recall_at_least_98pct'] for p in self.a['policies']],[2,2])
    def test_not_a_human_observation(self):
        self.assertTrue(all(r['source_kind'].startswith('MATHEMATICAL_COUNTERFACTUAL') for r in self.a['scenarios']))
        self.assertEqual(len(self.a['scenarios']),8)
    def test_no_change_if_reviewer_keeps_every_AI_decision(self):
        self.assertEqual(state(284,3,167,3342,0,0)['accuracy'],Fraction(3626,3796))

if __name__=='__main__':unittest.main()
