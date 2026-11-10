import unittest
import sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_r36_joint_certificates import audit, derived, ceiling, floor_fraction

class R36ExactCertificates(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.a=audit()
    def test_policy_size_145(self):self.assertEqual(self.a['policy_145']['policy_tagged_states'],4532)
    def test_policy_size_221(self):self.assertEqual(self.a['policy_221']['policy_tagged_states'],11832)
    def test_total_policy_tagged(self):self.assertEqual(self.a['policy_tagged_states_total'],16364)
    def test_distinct_matrices_union(self):self.assertEqual(self.a['distinct_untagged_confusion_matrices'],11832)
    def test_difference_increment(self):self.assertEqual(self.a['nested_extra_flags'],{'false_includes':33,'true_includes':43})
    def test_joint_80_98_small(self):self.assertEqual(self.a['policy_145']['feasible_target_certificates'][0]['feasible_policy_tagged_states_not_probabilities'],19)
    def test_joint_80_98_large(self):self.assertEqual(self.a['policy_221']['feasible_target_certificates'][0]['feasible_policy_tagged_states_not_probabilities'],118)
    def test_joint_85_98_large(self):self.assertEqual(self.a['policy_221']['feasible_target_certificates'][1]['feasible_policy_tagged_states_not_probabilities'],55)
    def test_85_unattainable_small(self):self.assertFalse(self.a['policy_145']['feasible_target_certificates'][1]['feasible'])
    def test_90_unattainable_both(self):self.assertFalse(self.a['policy_145']['feasible_target_certificates'][2]['feasible'] or self.a['policy_221']['feasible_target_certificates'][2]['feasible'])
    def test_integer_rounding_boundary(self):self.assertEqual(ceiling(F(385,4)),97);self.assertEqual(floor_fraction(F(-1,2)),-1)
    def test_correct_80_precision_at_y1(self):self.assertEqual(self.a['policy_145']['feasible_target_certificates'][0]['min_corrections_by_permitted_y'][1]['min_fp_corrections'],97)
    def test_fully_wrong_large_policy(self):self.assertEqual(self.a['policy_221']['all_fp_and_all_tp_reversed']['precision_pct'],'86.0870')
    def test_fully_wrong_large_recall(self):self.assertEqual(self.a['policy_221']['all_fp_and_all_tp_reversed']['recall_pct'],'68.9895')
    def test_policy_extension_reversal(self):self.assertEqual(self.a['nested_policy_counterexample']['precision_pct'],'88.2784')
    def test_counterfactual_only(self):self.assertTrue(self.a['source_only_post_hoc_counterfactual_not_human_measurement'])
    def test_adversarial_y_grid(self):
        for C,T in [(0,0),(2,1),(3,4),(43,7)]:
            r=derived(C,T)
            self.assertEqual(r['policy_tagged_states'],(C+1)*(T+1))
if __name__=='__main__':unittest.main()
