"""Public, standard-library-only source-conditional B0/B1 routing audit."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_r40_policy_identity import cert

class R40PolicyReadback(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.result=cert(ROOT/'data'/'r40'/'heldout_per_review.csv')
 def test_source(self):self.assertEqual(self.result['source_csv_sha256'],'4590955b6cca5375c97af17e4350d4f6fa84ff5e811286c4934af48cf06861d7')
 def test_count_rows(self):self.assertEqual((self.result['all_derived_rows'],self.result['matched_policy_rows']),(1740,1680))
 def test_pairwise(self):self.assertEqual(self.result['matched_review_budget_mask_pairs'],840)
 def test_saturation(self):self.assertEqual(self.result['budget_ge_95_structurally_no_auto_exclusion_rows'],480)
 def test_budget(self):self.assertEqual(self.result['scenario_pairs_over_nominal_human_budget'],184)
 def test_splits(self):self.assertEqual((self.result['distinct_test_review_units'],self.result['distinct_external_review_units']),(8,22))
 def test_b0_b1_crossing(self):
  a=self.result['unmasked_observed_routing']
  self.assertEqual([a['test_50'][k]['final_positives_auto_excluded'] for k in ['B0','B1']],[67,49])
  self.assertEqual([a['external_50'][k]['final_positives_auto_excluded'] for k in ['B0','B1']],[74,81])
 def test_b2_hold(self):self.assertIn('No fuzzy B2 calibration',self.result['claims_denied'])
if __name__=='__main__':unittest.main()
