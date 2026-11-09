import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_r32_core_coverage import audit
class R32CoreCoverageTests(unittest.TestCase):
 def setUp(self):self.result=audit()
 def test_valid(self):self.assertTrue(self.result['ok'])
 def test_selected_exact(self):self.assertEqual(self.result['selected_core'],21)
 def test_frozen_membership(self):self.assertEqual(self.result['inside_frozen_60'],19)
 def test_outside_registry(self):self.assertEqual(self.result['outside_frozen_60'],2)
 def test_preprints(self):self.assertEqual(self.result['preprints_in_core'],3)
 def test_assisted_cases(self):self.assertEqual(self.result['primary_illustrative_strata']['OBSERVED_ASSISTED_TASK'],3)
 def test_total_strata(self):self.assertEqual(sum(self.result['primary_illustrative_strata'].values()),21)
 def test_prior_work(self):self.assertEqual(self.result['new_prior_art_source_rows'],6)
if __name__=='__main__':unittest.main()
