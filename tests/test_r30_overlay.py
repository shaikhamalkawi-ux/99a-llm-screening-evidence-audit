import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_r30_overlay import audit
class TestR30SourceClosure(unittest.TestCase):
    def test_additive_source_admission(self):self.assertTrue(audit()['ok'])
    def test_full_reports_54(self):self.assertEqual(audit()['full_reports_access_checked'],54)
    def test_zero_journal_text_holds(self):self.assertEqual(audit()['final_publisher_holds'],0)
    def test_candidate_count_unchanged(self):self.assertEqual(audit()['candidate_ids'],60)
    def test_interpretive_core_unchanged(self):self.assertEqual(audit()['interpretive_core'],21)
    def test_human_savings_unmeasured(self):self.assertFalse(audit()['measured_net_human_saving'])
if __name__=='__main__':unittest.main()
