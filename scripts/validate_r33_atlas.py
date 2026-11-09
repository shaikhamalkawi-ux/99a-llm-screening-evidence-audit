#!/usr/bin/env python3
"""R33 finite source-ledger consistency; NOT full-paper extraction or eligibility adjudication."""
from pathlib import Path
from collections import Counter
import csv,json
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data'
def read(f):
 with (DATA/f).open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
def audit():
 base=read('candidate_source_gates_60.csv')
 old=read('source_claim_timing_crosswalk_49.csv')
 a=read('R33_All54_SourceNote_EvidenceAtlas.csv')
 new=read('R33_Additional_2026_Discovery_Register.csv')
 search=read('R33_Reproducible_Web_Search_Log.csv')
 prior=read('R33_Closest_Synthesis_Contrast.csv')
 summary=json.loads((DATA/'R33_Analysis_Summary.json').read_text())
 assert len(base)==len({r['candidate_id'] for r in base})==60
 assert len(old)==len({r['candidate_id'] for r in old})==49
 assert len(a)==len({r['candidate_id'] for r in a})==54
 assert len(new)==len({r['source_id'] for r in new})==11
 assert len(search)==len({r['search_id'] for r in search})==12
 assert len(prior)==len({r['doi'] for r in prior})==8
 oids={r['candidate_id'] for r in old}
 a_ids={r['candidate_id'] for r in a}
 assert oids<=a_ids
 assert a_ids-oids=={'LIT-003','LIT-021','LIT-025','LIT-068','LIT-076'}
 assert Counter(r['provisional_role'] for r in a)=={'EMPIRICAL_PROVISIONAL':50,'CONTEXT_PROVISIONAL':4}
 r20=Counter(r['source_note_evidence_channel'] for r in a if r['source_verification_phase']=='R20')
 assert r20=={'NO_ASSISTED_HUMAN_CONTRAST_DOCUMENTED_IN_R20_SOURCE_NOTE':41,
               'OBSERVED_ASSISTED_VS_UNASSISTED_TASK':1,'OBSERVED_ABSTRACT_REPRESENTATION_TASK':1,
               'OBSERVED_HUMAN_ONLY_WORKFLOWS':1,'OBSERVED_HUMAN_VS_MACHINE_RUNTIME':3,
               'CALENDAR_ELAPSED_VS_MACHINE_RUNTIME':2}
 assert all(r['independent_final_eligibility']=='NOT_ADJUDICATED' for r in a)
 assert all(r['fulltext_source_admitted_to_54']=='NO' and r['final_review_inclusion']=='NOT_ADJUDICATED' for r in new)
 assert not {r['doi'].casefold() for r in new} & {r['doi'].casefold() for r in base if r['doi']}
 assert all(r['source_url']=='https://doi.org/'+r['doi'] for r in new)
 assert all(r['source_url'].startswith('https://') for r in a)
 assert all(r['database_export']=='NO' and r['returned_total_records']=='NOT_EXPOSED_BY_WEB_INTERFACE' for r in search)
 assert summary['systematic_review_claim']=='NOT_ADMISSIBLE'
 assert summary['cross_study_pooled_labor_saving']=='NOT_ESTIMATED'
 assert summary['source_checked_reports_at_last_lock']==54
 return {'ok':True,'source_note_atlas':len(a),'new_discovery_records':len(new),'logged_searches':len(search),'prior_art_comparators':len(prior),'r20_note_categories':dict(r20),'admission_boundary':'not systematic or final eligibility'}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
