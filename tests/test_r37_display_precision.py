"""R37 exact display-metric compatibility checks and adversarial controls."""
import unittest,sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_r37_display_precision import audit,band,in_band,janoudi_case

class R37DisplayCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=audit()
    def test_source_lock(self):self.assertTrue(self.data['source_baseline_unchanged'])
    def test_original_dois(self):self.assertEqual(self.data['janoudi_source_doi'],'10.1016/j.jval.2025.09.008')
    def test_half_open_814(self):self.assertEqual(band('81.4',1,True),(F(1627,2000),F(1629,2000)))
    def test_half_open_899(self):self.assertEqual(band('89.9',1,True),(F(1797,2000),F(1799,2000)))
    def test_814_one_state(self):self.assertEqual(self.data['janoudi_policy_display_constraints'][0]['compatible_integer_count_states'],1)
    def test_899_one_state(self):self.assertEqual(self.data['janoudi_policy_display_constraints'][1]['compatible_integer_count_states'],1)
    def test_policy145_unique_corner(self):self.assertEqual(self.data['janoudi_policy_display_constraints'][0]['only_compatible_state'],{'x':102,'y':0})
    def test_policy221_unique_corner(self):self.assertEqual(self.data['janoudi_policy_display_constraints'][1]['only_compatible_state'],{'x':135,'y':0})
    def test_next_highest_below_814_bin(self):self.assertLess(F(self.data['janoudi_policy_display_constraints'][0]['highest_other_fraction']),F(1627,2000))
    def test_next_highest_below_899_bin(self):self.assertLess(F(self.data['janoudi_policy_display_constraints'][1]['highest_other_fraction']),F(1797,2000))
    def test_one_wrong_tp_not_same_rounded_814(self):self.assertFalse(in_band(F(283,348),'81.4',1,True))
    def test_one_wrong_tp_not_same_rounded_899(self):self.assertFalse(in_band(F(283,315),'89.9',1,True))
    def test_li_seven_matrices(self):self.assertEqual(self.data['li_display_constraints']['same_cohort_rounded_candidates_not_observations'],7)
    def test_li_all_have_26_fn(self):self.assertEqual({a['fn'] for a in self.data['li_display_constraints']['conditional_matrices']},{26})
    def test_li_pure_negatives_conserved(self):self.assertTrue(all(c['tn']+c['fp']==6218 for c in self.data['li_display_constraints']['conditional_matrices']))
    def test_li_npv_1_nonnezero_fn(self):self.assertTrue(all(in_band(F(c['tn'],c['tn']+c['fn']),'1.00',2) and c['fn']>0 for c in self.data['li_display_constraints']['conditional_matrices']))
    def test_rounding_upper_bounded(self):self.assertEqual(band('1.00',2),(F(199,200),F(1)))
    def test_rounding_non_observed(self):self.assertIn('NOT_NEW_EMPIRICAL',self.data['audit_kind'])

if __name__=='__main__':unittest.main()
