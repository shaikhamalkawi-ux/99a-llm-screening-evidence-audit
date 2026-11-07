#!/usr/bin/env python3
"""Public project 99a artifact integrity checks; no external packages required."""
from pathlib import Path
import collections,csv,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]

def read(name):
    with (ROOT/'data'/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

def main():
    rows=read('candidate_source_gates_60.csv')
    assert len(rows)==60
    assert len({r['candidate_id'] for r in rows})==60
    assert all(r['original_source_url'].startswith('https://') for r in rows)
    assert {r['candidate_id'] for r in rows if not r['doi']}=={'LIT-009'}
    assert all(r['independent_human_eligibility']=='NOT_PERFORMED' and r['independent_human_extraction']=='NOT_PERFORMED' for r in rows)
    counts=collections.Counter(r['provisional_evidence_role'] for r in rows)
    expected={'EMPIRICAL_PROVISIONAL':45, 'CONTEXT_PROVISIONAL':4, 'FULL_TEXT_HOLD':5,
      'SCOPE_EXCLUDE_PROVISIONAL':4,'CONTEXT_ABSTRACT_LIMITED':1,'LINKED_DUPLICATE_VERSION':1}
    assert counts==expected, (counts,expected)
    holds=[r for r in rows if r['final_fulltext_gate']=='NOT_OBTAINED']
    assert {r['candidate_id'] for r in holds}=={'LIT-003','LIT-021','LIT-025','LIT-068','LIT-076'}
    assert len(read('claim_certificate_rules_7.csv'))==7
    assert len(read('linked_publication_lineages_3.csv'))==3
    assert len(read('final_journal_fulltext_holds_5.csv'))==5
    assert len(read('related_reviews_and_guidance_3.csv'))==3
    assert len(read('selected_source_traceable_contrasts_9.csv'))==9
    for p in ROOT.rglob('*'):
        if not p.is_file() or p == Path(__file__): continue
        assert p.suffix.lower() not in {'.pdf','.docx','.zip','.rar','.7z','.jpg'}, p
        if p.suffix.lower() in {'.csv','.py','.md','.yml','.txt','.cff'}:
            t=p.read_text(encoding='utf-8')
            assert 'drive.google.com' not in t and '/mnt/data' not in t and 'shaikhamalkawi@gmail' not in t, p
    print(json.dumps({'ok':True,'candidate_ids':len(rows),'role_counts':dict(sorted(counts.items())),
                       'final_fulltext_holds':len(holds),'independent_human_verification':'NOT_PERFORMED',
                       'systematic_search':'NOT_COMPLETE'},indent=2))

if __name__=='__main__':main()
