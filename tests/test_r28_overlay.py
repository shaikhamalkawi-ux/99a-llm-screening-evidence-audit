import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_r28_overlay import audit
class TestR28Overlay(unittest.TestCase):
 def test_valid(self):self.assertTrue(audit()['ok'])
 def test_closed_three(self):self.assertEqual(audit()['newly_accessed'],3)
 def test_remaining_two(self):self.assertEqual(len(audit()['unobtained']),2)
 def test_preserves_original_60(self):self.assertEqual(audit()['frozen_candidates'],60)
if __name__=='__main__':unittest.main()
