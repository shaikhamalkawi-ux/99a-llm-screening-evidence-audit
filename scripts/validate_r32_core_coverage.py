#!/usr/bin/env python3
"""Check retrospectively coded R31 21-work core; no final eligibility adjudication.

The six strata are authored, post hoc descriptive labels of source notes, not
independent evidence claims, exhaustive selection criteria, or sampling weights.
"""
from pathlib import Path
from collections import Counter
import csv,json
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
EXPECTED_COUNTS={
 'OBSERVED_ASSISTED_TASK':3,
 'OBSERVED_UNASSISTED_HUMAN':1,
 'ASSUMPTION_MODELED_LABOR':2,
 'DECISION_ROUTING':5,
 'MACHINE_RUNTIME_OR_ELAPSED':4,
 'CLASSIFICATION_REFERENCE_OR_DISAGREEMENT':6,
}
CORE_IDS={'LIT-002','LIT-004','LIT-008','LIT-009','LIT-012','LIT-013','LIT-015','LIT-017',
          'LIT-020','LIT-024','LIT-028','LIT-031','LIT-039','LIT-040','LIT-043','LIT-047',
          'LIT-049','LIT-052','LIT-075','TM-25','LD-25'}

def load(file):
 with (DATA/file).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def audit():
 core=load('R32_purposive_core_coverage_21.csv')
 prior=load('R32_prior_art_boundary_6.csv')
 access=load('candidate_source_gates_60.csv')
 assert len(core)==21 and {r['source_id'] for r in core}==CORE_IDS
 assert len({r['bib_key'] for r in core})==21
 assert Counter(r['post_hoc_primary_illustrative_stratum'] for r in core)==EXPECTED_COUNTS
 registry={r['candidate_id'] for r in access}
 assert len(registry)==60
 assert {r['source_id'] for r in core if r['in_frozen_60_access_register']=='NO'}=={'TM-25','LD-25'}
 assert all((r['source_id'] in registry)==(r['in_frozen_60_access_register']=='YES') for r in core)
 assert {r['source_id'] for r in core if r['publication_state_from_R31']=='PREPRINT'}=={'LIT-009','LIT-012','LIT-052'}
 assert all(r['reported_resource_or_reference_focus'].strip() and r['why_case_is_illustrative'].strip() and
            'Retrospective' in r['coding_boundary'] for r in core)
 assert len(prior)==6 and len({r['doi'] for r in prior})==6
 assert all(r['source_url']=='https://doi.org/'+r['doi'] and r['prior_contribution'].strip() and
            r['project_limit'].strip() for r in prior)
 assert {r['first_author'] for r in prior}=={'Nunnery','Lai','Madeyski','Laignelot','Fleurence','Baser'}
 return {'ok':True,'selected_core':len(core),'inside_frozen_60':19,'outside_frozen_60':2,
         'preprints_in_core':3,'primary_illustrative_strata':EXPECTED_COUNTS,
         'new_prior_art_source_rows':len(prior),
         'boundary':'retrospective source-note mapping; not exhaustive eligibility or literature prevalence'}

if __name__=='__main__':print(json.dumps(audit(),indent=2,sort_keys=True))
