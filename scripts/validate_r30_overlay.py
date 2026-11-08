#!/usr/bin/env python3
"""R30 source-identity and source-access overlays; does not rerun studies."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
def read(name):
    with (DATA/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def audit():
    base=read('candidate_source_gates_60.csv')
    r28=read('R28_new_final_publisher_reports_3.csv')
    r29=read('R29_janoudi_final_publisher_and_supplement.csv')
    r30=read('R30_li_final_publisher_article_1.csv')
    s=json.loads((DATA/'R30_access_update_summary.json').read_text(encoding='utf-8'))
    assert len(base)==60 and len({r['candidate_id'] for r in base})==60
    old={r['candidate_id'] for r in base if r['final_fulltext_gate']=='NOT_OBTAINED'}
    assert old=={'LIT-003','LIT-021','LIT-025','LIT-068','LIT-076'}
    ids28={r['candidate_id'] for r in r28};ids29={r['candidate_id'] for r in r29}
    ids30={r['candidate_id'] for r in r30}
    assert ids28=={'LIT-021','LIT-025','LIT-068'}
    assert ids29=={'LIT-076'} and ids30=={'LIT-003'}
    assert not (ids28&ids29 or ids28&ids30 or ids29&ids30)
    assert old==ids28|ids29|ids30
    assert len(r30)==1 and r30[0]['doi']=='10.1016/j.ijmedinf.2025.106205'
    x=r30[0]
    assert x['journal_url']=='https://doi.org/'+x['doi']
    assert x['r30_source_gate']=='FINAL_PUBLISHER_PDF_SOURCE_CHECKED'
    assert x['r30_scientific_inclusion']=='SOURCE_REVIEWED_NOT_FINAL_ELIGIBILITY'
    assert x['net_human_minutes_observed']=='NO'
    assert len(x['publisher_pdf_sha256'])==64 and all(c in '0123456789abcdef' for c in x['publisher_pdf_sha256'])
    assert int(x['publisher_pdf_pages'])==11
    assert (int(x['gold_positive']),int(x['gold_negative']))==(113,6218)
    assert int(x['main_corpus_count'])==113+6218==6331
    assert (x['best_individual_precision'],x['best_individual_recall'],x['best_individual_NPV'],x['best_individual_gmean'])==('0.34','0.77','1.00','0.87')
    assert x['reported_workload_reduction_range_pct']=='94-98'
    assert int(x['additional_topics_count'])==10 and int(x['additional_topic_sample_count'])==327
    assert s['current_source_checked_full_reports']==49+3+1+1==54
    assert s['source_role_counts']=={'EMPIRICAL_PROVISIONAL':50,'CONTEXT_PROVISIONAL':4,'FULL_TEXT_HOLD':0,'SCOPE_EXCLUDE_PROVISIONAL':4,'CONTEXT_ABSTRACT_LIMITED':1,'LINKED_DUPLICATE_VERSION':1}
    assert sum(s['source_role_counts'].values())==60
    assert s['current_final_journal_fulltext_holds']==[]
    assert s['distinct_underlying_works_in_preexisting_interpretive_core_unchanged']==21
    assert s['final_included_studies']=='NOT_DETERMINED'
    return {'ok':True,'candidate_ids':60,'full_reports_access_checked':54,'final_publisher_holds':0,'provisional_roles':s['source_role_counts'],'interpretive_core':21,'r30_candidate':'LIT-003','measured_net_human_saving':False}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
