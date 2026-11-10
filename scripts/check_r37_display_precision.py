#!/usr/bin/env python3
"""R37 source-display compatibility audit using exact rational arithmetic.

Published display numerals are transcribed into a separate input ledger; R34
source aggregates are never modified. No human reviewer outcome or probability
is estimated. Source rounding is an explicit *conditional assumption*.
"""
from fractions import Fraction as F
from pathlib import Path
import json
import csv

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/R34_FiveSource_ConstraintInputs.json'
PRINTED = ROOT / 'data/R37_SourceDisplay_Inputs.json'


def band(displayed: str, decimals: int, is_percent: bool = False):
    """Exact half-open interval for positive nearest-decimal display."""
    d = F(displayed)
    halfstep = F(1, 2 * 10**decimals)
    divisor = 100 if is_percent else 1
    return (max(F(0), (d-halfstep)/divisor),
            min(F(1), (d+halfstep)/divisor))


def in_band(value, displayed, decimals, is_percent=False):
    lo, hi = band(displayed, decimals, is_percent)
    # At probability 1 upper end is also included.
    return lo <= value <= hi if hi == 1 else lo <= value < hi


def percent(value):
    return f'{float(100*value):.6f}'


def janoudi_case(policy, source):
    A, FN0, B = [int(source[k]) for k in ('tp','fn','fp')]
    assert (A,FN0,B) == (284,3,167)
    m = int(policy['flagged_predicted_includes'])
    idx = source['simulated_review_counts'].index(m)
    C = B-int(source['simulated_remaining_fp'][idx])
    T = m-C
    assert (m,C,T) in ((145,102,43),(221,135,86))
    displayed = policy['displayed_precision_percent_one_decimal']
    P = lambda x,y: F(A-y,A+B-x-y)
    match = [(x,y) for y in range(T+1) for x in range(C+1)
             if in_band(P(x,y), displayed, 1, True)]
    maximum = P(C,0)
    # Monotonicity in x,y with retained FP>0: all alternative states have
    # P no greater than max(P(C-1,0),P(C,1)).
    second = max(P(C-1,0),P(C,1))
    assert all(P(x,y)<=second for x in range(C+1) for y in range(T+1) if (x,y)!=(C,0))
    lo,hi = band(displayed,1,True)
    assert lo <= maximum < hi and second < lo
    assert match == [(C,0)]
    return {
        'flagged_predicted_includes':m,
        'correctable_false_includes_C':C,
        'true_includes_at_risk_T':T,
        'displayed_precision_percent':displayed,
        'display_interval_fraction':[str(lo),str(hi)],
        'compatible_integer_count_states':len(match),
        'only_compatible_state':{'x':C,'y':0},
        'perfect_precision_percent_exact':percent(maximum),
        'highest_other_precision_percent_exact':percent(second),
        'highest_other_fraction':str(second),
        'one_wrong_tp_precision_percent':percent(P(C,1)),
        'one_unrepaired_fp_precision_percent':percent(P(C-1,0)),
        'conditional_on_fixed_source_and_rounding':True
    }


def li_case(display, source):
    assert source['n']==6331 and source['reference_positives']==113 and source['reference_negatives']==6218
    assert (display['displayed_precision_two_decimal'],
            display['displayed_recall_two_decimal'],
            display['displayed_npv_two_decimal'])==('0.34','0.77','1.00')
    candidates=[]
    for tp in range(114):
        if not in_band(F(tp,113),display['displayed_recall_two_decimal'],2):
            continue
        fn = 113-tp
        for fp in range(6219):
            if not in_band(F(tp,tp+fp),display['displayed_precision_two_decimal'],2):
                continue
            tn = 6218-fp
            if in_band(F(tn,tn+fn),display['displayed_npv_two_decimal'],2):
                candidates.append({'tp':tp,'fn':fn,'fp':fp,'tn':tn})
    assert len(candidates)==7 and {r['fn'] for r in candidates}=={26}
    return {
        'displayed_metrics':{k:display[k] for k in (
            'displayed_precision_two_decimal','displayed_recall_two_decimal','displayed_npv_two_decimal')},
        'same_cohort_rounded_candidates_not_observations':len(candidates),
        'conditional_matrices':candidates,
        'possible_false_negatives':[26],
        'possible_false_positives':[r['fp'] for r in candidates],
        'npv_exact_fraction_range':[str(min(F(r['tn'],r['tn']+r['fn']) for r in candidates)),
                                    str(max(F(r['tn'],r['tn']+r['fn']) for r in candidates))],
        'conditional_on_same_reference_and_rounding':True
    }


def audit():
    src=json.loads(SOURCE.read_text(encoding='utf-8'))['cases']
    d=json.loads(PRINTED.read_text(encoding='utf-8'))
    assert d['janoudi']['doi']==src['JANOUDI_2025']['doi']
    assert d['li']['doi']==src['LI_2026']['doi']
    j=[janoudi_case(p,src['JANOUDI_2025']) for p in d['janoudi']['policies']]
    l=li_case(d['li'],src['LI_2026'])
    return {'version':'R37',
            'audit_kind':'EXACT_DISPLAY_COMPATIBILITY_NOT_NEW_EMPIRICAL_RESULTS',
            'source_baseline_unchanged':True,
            'rounding_assumption':d['rounding_rule'],
            'janoudi_source_doi':d['janoudi']['doi'],
            'janoudi_policy_display_constraints':j,
            'li_source_doi':d['li']['doi'],
            'li_display_constraints':l,
            'interpretation':'The same act of rounding can isolate an ideal correction point or mask false negatives depending on the source counts and metric; no human behavior is estimated.',
            'claim_limits':[d['claim_boundary'],
               'Not a new general identification theorem or validation of a screening instrument.',
               'A different reference universe, rounding algorithm or review policy can change the results.']}


def write_outputs():
    obj=audit()
    (ROOT/'data/R37_DisplayCompatibility_Results.json').write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    with (ROOT/'data/R37_DisplayCompatibility_Summary.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f)
        w.writerow(['source','printed_metric','constraints','compatible_count_states','risk_or_hidden_error','interpretation'])
        for p in obj['janoudi_policy_display_constraints']:
            w.writerow(['Janoudi (2025)',p['displayed_precision_percent']+'% precision',
                str(p['flagged_predicted_includes'])+' flagged Include decisions',p['compatible_integer_count_states'],
                '0 new false negatives in sole compatible state','unique optimistic corner under explicit assumptions'])
        w.writerow(['Li (2026)','precision 0.34; recall 0.77; NPV 1.00',
            '6331 common records, 113 positives',len(obj['li_display_constraints']['conditional_matrices']),
            '26 false negatives in each feasible matrix','conditionally non-unique matrices despite NPV rounding to 1.00'])
    return obj

if __name__ == '__main__':
    obj=write_outputs()
    print(json.dumps({'status':'PASS','janoudi_compatible_states':[r['compatible_integer_count_states'] for r in obj['janoudi_policy_display_constraints']], 'li_compatible_matrices':obj['li_display_constraints']['same_cohort_rounded_candidates_not_observations']},indent=2))
