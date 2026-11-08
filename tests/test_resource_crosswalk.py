import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_resource_crosswalk import verify

class TestFrozenSourceClaimCrosswalk(unittest.TestCase):
 def test_audit_passes(self):self.assertTrue(verify()['ok'])
 def test_49_sources(self):self.assertEqual(verify()['source_notes_coded'],49)
 def test_first_assisted_timed_case(self):self.assertEqual(verify()['resource_note_categories']['OBSERVED_ASSISTED_VS_UNASSISTED_TASK'],1)
 def test_distinct_simplification(self):self.assertEqual(verify()['resource_note_categories']['OBSERVED_ABSTRACT_REPRESENTATION_TASK'],1)
 def test_not_all_saving_are_person_time(self):self.assertEqual(verify()['resource_note_categories']['OBSERVED_HUMAN_VS_MACHINE_RUNTIME'],3)
 def test_remaining_scope_is_source_note(self):self.assertEqual(verify()['resource_note_categories']['NO_ASSISTED_HUMAN_CONTRAST_DOCUMENTED_IN_R20_SOURCE_NOTE'],41)

if __name__=='__main__':unittest.main()
