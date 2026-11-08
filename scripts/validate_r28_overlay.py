#!/usr/bin/env python3
"""Validate additive source-access overlay; no source PDFs are distributed."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):
    with (ROOT/p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def audit():
    old=load('data/candidate_source_gates_60.csv');new=load('data/R28_new_final_publisher_reports_3.csv')
    summ=json.loads((ROOT/'data/R28_access_update_summary.json').read_text())
    assert len(old)==60 and len({r['candidate_id'] for r in old})==60
    assert len(new)==3 and len({r['candidate_id'] for r in new})==3
    assert {r['candidate_id'] for r in new}=={'LIT-021','LIT-025','LIT-068'}
    assert all(r['r28_access_state']=='FINAL_PUBLISHER_PDF_SOURCE_CHECKED' for r in new)
    assert all(len(r['original_sha256'])==64 for r in new)
    oldholds={r['candidate_id'] for r in old if r['final_fulltext_gate']=='NOT_OBTAINED'}
    assert oldholds=={'LIT-003','LIT-021','LIT-025','LIT-068','LIT-076'}
    assert {r['candidate_id'] for r in new}<=oldholds
    rest=oldholds-{r['candidate_id'] for r in new}
    assert rest=={'LIT-003','LIT-076'}
    assert summ['R28_fulltext_checked']==52 and summ['R28_final_journal_holds_count']==2
    assert summ['interpretive_core_distinct_works_unchanged']==21 and summ['R20_source_note_crosswalk_unchanged']==49
    return {'ok':True,'frozen_candidates':60,'R20_accessed':49,'newly_accessed':3,'R28_accessed':52,'unobtained':sorted(rest)}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
