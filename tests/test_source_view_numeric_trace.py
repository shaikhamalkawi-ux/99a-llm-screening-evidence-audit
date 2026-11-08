import sys,unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_source_view_numeric_trace import audit

class TestSourceViewNumericalCertificates(unittest.TestCase):
    def test_two_original_works(self):self.assertEqual(audit()['certificate_rows'],2)
    def test_leads_preprint_disclosed(self):self.assertEqual(audit()['leads_earlier_preprint_saving_pct'],'22.6')
    def test_leads_final_preserved(self):self.assertEqual(audit()['leads_final_reported_saving_pct'],'20.8')
    def test_leads_printed_means_ratio_distinct(self):
        a=audit()
        self.assertEqual(a['leads_ratio_of_final_printed_means_pct_to_1dp'],'22.6')
        self.assertNotEqual(a['leads_ratio_of_final_printed_means_pct_to_1dp'],a['leads_final_reported_saving_pct'])
    def test_huotala_printed_difference(self):self.assertEqual(audit()['huotala_difference_of_printed_means_s'],'9.69')
    def test_no_silent_source_correction(self):self.assertEqual(audit()['huotala_narrative_difference_s'],'9.39')

if __name__=='__main__':unittest.main()
