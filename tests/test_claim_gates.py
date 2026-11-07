import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from claim_gates import Evidence,evaluate

class TestClaimGates(unittest.TestCase):
 def test_e01_machine_not_labor(self):self.assertEqual(evaluate('E01',Evidence()),'TASK_TIME_ONLY_OR_UNIDENTIFIED')
 def test_e01_no_overhead(self):self.assertEqual(evaluate('E01',Evidence(matched_human_time=True)),'TASK_TIME_ONLY_OR_UNIDENTIFIED')
 def test_e01_observed_complete(self):self.assertEqual(evaluate('E01',Evidence(matched_human_time=True,full_human_overhead_observed=True)),'OBSERVED_NET_PERSON_TIME_COMPONENT')
 def test_e02_only_assumed(self):self.assertEqual(evaluate('E02',Evidence(modeled_rates_disclosed=True)),'MODELED_SCENARIO_WITH_ASSUMPTIONS')
 def test_e02_missing_rate(self):self.assertEqual(evaluate('E02',Evidence()),'MODELED_CLAIM_HOLD')
 def test_e03(self):self.assertEqual(evaluate('E03',Evidence(decision_counts_observed=True)),'DECISION_WORKLOAD_ONLY')
 def test_e04_simulated(self):self.assertEqual(evaluate('E04',Evidence(policy_simulated_only=True)),'SIMULATED_ROUTING_ONLY')
 def test_e04_executed(self):self.assertEqual(evaluate('E04',Evidence(human_oversight_executed_and_timed=True)),'EXECUTED_HUMAN_OVERSIGHT_TIMED')
 def test_e05_unverified_pool(self):self.assertEqual(evaluate('E05',Evidence()),'VERIFIED_SUBSET_ONLY')
 def test_e05_complete(self):self.assertEqual(evaluate('E05',Evidence(complete_eligibility_reference=True)),'FULL_REFERENCE_RETENTION')
 def test_e06_shared_data(self):self.assertEqual(evaluate('E06',Evidence()),'CLUSTER_LINKED_OR_HOLD')
 def test_e06_disjoint(self):self.assertEqual(evaluate('E06',Evidence(cohort_independence_verified=True)),'COHORT_INDEPENDENCE_SUPPORTED')
 def test_e07_not_prisma(self):self.assertEqual(evaluate('E07',Evidence(comprehensive_search_logged=True)),'CRITICAL_REVIEW_ONLY')
 def test_e07_both_gates(self):self.assertEqual(evaluate('E07',Evidence(comprehensive_search_logged=True,independent_human_adjudication=True)),'SYSTEMATIC_REVIEW_MINIMUM_PROCESS_GATES')
 def test_error(self):
  with self.assertRaises(ValueError):evaluate('BAD',Evidence())
if __name__=='__main__':unittest.main()
