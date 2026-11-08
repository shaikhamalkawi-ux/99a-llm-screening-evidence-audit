#!/usr/bin/env python3
"""R29 metadata, source-identity and exact arithmetic integrity checks.

Tests source-entered *reported values*, not original experimental output.
No publisher full texts or personal disclosures are read or redistributed.
"""
from pathlib import Path
from fractions import Fraction
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def load_csv(filename):
    with (DATA / filename).open('r', encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


def audit():
    original = load_csv('candidate_source_gates_60.csv')
    r28 = load_csv('R28_new_final_publisher_reports_3.csv')
    r29 = load_csv('R29_janoudi_final_publisher_and_supplement.csv')
    summary = json.loads((DATA / 'R29_source_access_summary.json').read_text(encoding='utf-8'))
    ids = {r['candidate_id'] for r in original}
    assert len(original) == len(ids) == 60
    old_holds = {r['candidate_id'] for r in original if r['final_fulltext_gate'] == 'NOT_OBTAINED'}
    assert old_holds == {'LIT-003', 'LIT-021', 'LIT-025', 'LIT-068', 'LIT-076'}
    ids28 = {r['candidate_id'] for r in r28}
    ids29 = {r['candidate_id'] for r in r29}
    assert len(r28) == len(ids28) == 3 and ids28 == {'LIT-021','LIT-025','LIT-068'}
    assert len(r29) == 1 and ids29 == {'LIT-076'}
    assert not ids28.intersection(ids29)
    assert old_holds - ids28 - ids29 == {'LIT-003'}
    row = r29[0]
    assert row['doi'] == '10.1016/j.jval.2025.09.008'
    assert row['report_access_state'] == 'FINAL_PUBLISHER_PDF_SOURCE_CHECKED'
    assert row['full_staff_person_time_observed'] == 'NO'
    assert row['study_inclusion_status'] == 'PROVISIONAL_SOURCE_ONLY'
    assert row['journal_url'] == 'https://doi.org/' + row['doi']
    assert all(len(row[key]) == 64 and all(c in '0123456789abcdef' for c in row[key])
               for key in ('main_sha256', 'supplement_sha256', 'disclosure_sha256'))
    tp,fn,fp,tn = (int(row[k]) for k in ('true_included','false_excluded','false_included','true_excluded'))
    total = int(row['original_screened_citations'])
    assert total == 3796 == tp + fn + fp + tn
    assert tp + fn == int(row['original_reference_included']) == 287
    sensitivity = Fraction(tp,tp+fn)
    specificity = Fraction(tn,tn+fp)
    precision = Fraction(tp,tp+fp)
    # Compare displayed author percentages with exact count-derived ratios.
    # Authors show sensitivity as 98.9% in the abstract and 98.95% in the body;
    # 284/287=98.9547%, so avoid imposing our own rounding convention.
    assert all(abs(actual - displayed) < 0.11 for actual, displayed in
               zip((float(sensitivity)*100,float(specificity)*100,float(precision)*100),
                   (98.9,95.2,63.0)))
    review_counts = [int(row['hypothetical_screen_low_medium_include']),
                     int(row['hypothetical_screen_low_medium_high_include'])]
    assert review_counts == [145,221]
    assert round(review_counts[0] / total * 100, 1) == 3.8
    assert round(review_counts[1] / total * 100, 1) == 5.8
    assert 'perfectly' in row['simulation_assumption'].lower()
    assert row['model_AUC_confidence_only'] == '0.86'
    assert row['model_AUC_with_decision'] == '0.98'
    assert row['odds_ratio_include_vs_exclude'] == '329'
    assert summary['currently_verified_full_reports'] == 53
    assert summary['current_provisional_empirical'] == 49
    assert summary['current_provisional_contextual'] == 4
    assert summary['unresolved_final_journal_fulltext_ids'] == ['LIT-003']
    assert summary['interpretive_core_underlying_investigations_unchanged'] == 21
    assert summary['frozen_R20_source_note_timing_crosswalk_unchanged'] == 49
    return {'ok':True,'candidate_total':len(ids),'full_sources_checked':53,
            'remaining_final_text_holds':['LIT-003'], 'new_source_id':'LIT-076',
            'observed_counts':{'TP':tp,'FN':fn,'FP':fp,'TN':tn},
            'sensitivity':str(sensitivity),'specificity':str(specificity),'precision':str(precision),
            'hypothetical_review_records':review_counts,'simulation_not_human_time':True}


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
