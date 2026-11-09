"""Arithmetical checks on printed source counts, not source study replication."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_insuk_2025 import audit
class TestInsukPublisherSource(unittest.TestCase):
 def setUp(self): self.a=audit()
 def test_pass(self): self.assertTrue(self.a['ok'])
 def test_three_rows(self): self.assertEqual(len(self.a['results']),3)
 def test_body_and_table_heading_differ(self): self.assertTrue(all(x['source_total_body_table1']==1648 and x['source_total_table3_heading']==1684 for x in self.a['results']))
 def test_junior_counts(self): self.assertEqual([(x['TP'],x['FN'],x['FP'],x['TN']) for x in self.a['results'] if x['screener']=='Junior reviewers'],[(21,12,55,1560)])
 def test_gpt_counts(self): self.assertEqual([(x['TP'],x['FN'],x['FP'],x['TN']) for x in self.a['results'] if x['screener']=='ChatGPT'],[(27,6,136,1479)])
 def test_claude_counts(self): self.assertEqual([(x['TP'],x['FN'],x['FP'],x['TN']) for x in self.a['results'] if x['screener']=='Claude'],[(27,6,85,1530)])
 def test_fpr_reported_distinct(self): self.assertTrue(all(abs(x['reconstructed_fpr']-float(x['published_fpr']))>.001 for x in self.a['results']))
if __name__=='__main__':unittest.main()
