#!/usr/bin/env python3
"""Public project 99a artifact integrity checks; no external packages required."""
from pathlib import Path
import collections,csv,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]

def verify_sha256_manifest():
    manifest=ROOT/'SHA256SUMS.txt'
    assert manifest.is_file(), 'SHA256 manifest missing'
    expected={}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        assert '  ' in line, 'malformed manifest row'
        digest,rel=line.split('  ',1)
        rel_path=Path(rel)
        assert len(digest)==64 and all(c in '0123456789abcdef' for c in digest)
        assert not rel_path.is_absolute() and '..' not in rel_path.parts and rel not in expected
        expected[rel]=digest
    actual=set()
    for p in ROOT.rglob('*'):
        if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts or p.suffix=='.pyc':continue
        rel=p.relative_to(ROOT).as_posix()
        if rel!='SHA256SUMS.txt':actual.add(rel)
    assert set(expected)==actual, {'missing':sorted(set(expected)-actual),'unlisted':sorted(actual-set(expected))}
    for rel,digest in expected.items():
        actual_hash=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
        assert digest==actual_hash, rel
    return len(expected)

def read(name):
    with (ROOT/'data'/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

def main():
    manifest_count=verify_sha256_manifest()
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
    # R20 is a frozen historical source snapshot; the additive R28-R30 overlays
    # are the present access state. Check them separately, never rewrite history.
    from validate_r30_overlay import audit as current_access_audit
    current=current_access_audit()
    print(json.dumps({'ok':True, 'manifest_files_checked':manifest_count,
                       'historical_R20_source_state':{'candidate_ids':len(rows),
                         'role_counts':dict(sorted(counts.items())),
                         'historical_publisher_fulltext_holds':len(holds)},
                       'current_access_overlay':{'full_reports_checked':current['full_reports_access_checked'],
                         'final_publisher_fulltext_holds':current['final_publisher_holds'],
                         'frozen_candidate_ids':current['candidate_ids']},
                       'current_manuscript_track':'PROPOSED_ORIGINAL_RESEARCH_ARTICLE',
                        'design':'RETROSPECTIVE_SOURCE_LINKED_DOCUMENTARY_REANALYSIS'},indent=2))

if __name__=='__main__':main()
