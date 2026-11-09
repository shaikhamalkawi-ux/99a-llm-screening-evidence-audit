import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_r33_atlas import audit
class TestR33ExpandedEvidenceMap(unittest.TestCase):
 def setUp(self):self.a=audit()
 def test_valid(self):self.assertTrue(self.a['ok'])
 def test_full_source_notes(self):self.assertEqual(self.a['source_note_atlas'],54)
 def test_discoveries(self):self.assertEqual(self.a['new_discovery_records'],11)
 def test_search_log(self):self.assertEqual(self.a['logged_searches'],12)
 def test_comparators(self):self.assertEqual(self.a['prior_art_comparators'],8)
 def test_no_presumed_zero_labor(self):self.assertEqual(self.a['admission_boundary'],'not systematic or final eligibility')
 def test_frozen_note_unknowns(self):self.assertEqual(self.a['r20_note_categories']['NO_ASSISTED_HUMAN_CONTRAST_DOCUMENTED_IN_R20_SOURCE_NOTE'],41)
 def test_matched_human_timing_note(self):self.assertEqual(self.a['r20_note_categories']['OBSERVED_ASSISTED_VS_UNASSISTED_TASK'],1)
if __name__=='__main__':unittest.main()
