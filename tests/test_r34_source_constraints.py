import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_r34_source_constraints import check
class R34SourceConstraintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.a=check()
    def test_integrity(self):self.assertTrue(self.a['ok'])
    def test_zhang_two_denominators(self):
        z=self.a['zhang'];self.assertEqual((z['percent_of_table_n_1dp'],z['percent_of_methods_n_1dp']),('6.4','6.5'))
        self.assertTrue(z['source_denominator_unresolved'])
    def test_insuk_do_not_call_author_error(self):self.assertTrue(self.a['insuk']['no_author_error_certified'])
    def test_cao_ceiling_is_counterfactual(self):
        c=self.a['cao'];self.assertEqual(c['counterfactual_coverage_ceiling_if_all_unavailable_excluded_percent'],'59.16')
        self.assertEqual(c['assumed_ten_thousand_abstract_human_hours'],'83.33')
        self.assertTrue(c['no_observed_net_person_time'])
    def test_janoudi_only_include_decisions_corrected(self):
        j=self.a['janoudi'];self.assertEqual(j['baseline_errors'],170)
        self.assertEqual([r['remaining_false_negatives'] for r in j['simulated_cases']],[3,3])
        self.assertEqual([r['corrected_errors_if_perfect'] for r in j['simulated_cases']],[102,135])
        self.assertFalse(j['human_routing_executed'])
    def test_li_integer_feasible_set_not_actual_model_output(self):
        l=self.a['li'];self.assertEqual(l['conditionally_feasible_matrices'],7)
        self.assertEqual((l['feasible_tp'],l['feasible_fn']),(87,26))
        self.assertEqual(l['feasible_predicted_include_counts'],[253,259])
        self.assertTrue(l['not_the_actual_reported_model_confusion_matrix'])
    def test_r34_does_not_promote_source_inclusion(self):self.assertTrue(self.a['study_inclusion_denominator_unchanged'])
if __name__=='__main__':unittest.main()

class R34SourceFingerprintAndRightsTests(unittest.TestCase):
    def test_five_hashes_match_prior_admission_overlays(self):
        import csv
        data=Path(__file__).resolve().parents[1]/'data'
        def rows(name):
            with (data/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
        declared=rows('R34_OriginalPDF_SourceFingerprints_5.csv')
        assert len(declared)==5 and len({x['doi'] for x in declared})==5
        refs={x['doi']:x['original_sha256'] for x in rows('R28_new_final_publisher_reports_3.csv')}
        refs.update({x['doi']:x['main_sha256'] for x in rows('R29_janoudi_final_publisher_and_supplement.csv')})
        refs.update({x['doi']:x['publisher_pdf_sha256'] for x in rows('R30_li_final_publisher_article_1.csv')})
        for row in declared:self.assertEqual(row['sha256'],refs[row['doi']])
    def test_no_article_pdf_in_public_root(self):
        public=Path(__file__).resolve().parents[1]
        self.assertFalse(any(p.suffix.lower()=='.pdf' for p in public.rglob('*') if p.is_file()))
