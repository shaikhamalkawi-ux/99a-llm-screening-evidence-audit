"""Metadata tests, not human-workflow validation."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_r29_overlay import audit


class TestR29SourceAndSupplement(unittest.TestCase):
    def test_source_admission(self):
        self.assertTrue(audit()['ok'])
    def test_candidate_frozen(self):
        self.assertEqual(audit()['candidate_total'],60)
    def test_current_fulltexts(self):
        self.assertEqual(audit()['full_sources_checked'],53)
    def test_one_remaining(self):
        self.assertEqual(audit()['remaining_final_text_holds'],['LIT-003'])
    def test_source_confusion_matrix(self):
        self.assertEqual(audit()['observed_counts'],{'TP':284,'FN':3,'FP':167,'TN':3342})
    def test_decision_count_not_person_time(self):
        self.assertTrue(audit()['simulation_not_human_time'])
        self.assertEqual(audit()['hypothetical_review_records'],[145,221])


if __name__ == '__main__':
    unittest.main()
