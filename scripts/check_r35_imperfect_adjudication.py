#!/usr/bin/env python3
"""Finite deterministic stress envelope for hypothetical Include-only human overrides.

Source: Janoudi et al. (2025), Value in Health, 10.1016/j.jval.2025.09.008,
Table 2 baseline and Table 4 simulated 145/221 Include-only strategies.

This code does not observe human decisions or time, estimate human error rates,
rerun Loon Lens, or validate the reference standard. Original published values
are retained and the synthetic override states are separately labeled.
"""
import csv
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'data' / 'R34_FiveSource_ConstraintInputs.json'


def fmt_percent(q, places=4):
    return f'{100 * float(q):.{places}f}'


def state(tp0, fn0, fp0, tn0, x, y):
    # x: falsely Included citations correctly changed to Exclude
    # y: correctly Included citations mistakenly changed to Exclude
    tp, fn, fp, tn = tp0 - y, fn0 + y, fp0 - x, tn0 + x
    assert min(tp, fn, fp, tn) >= 0
    n = tp + fn + fp + tn
    return {
        'tp': tp, 'fn': fn, 'fp': fp, 'tn': tn,
        'precision': Fraction(tp, tp + fp),
        'recall': Fraction(tp, tp + fn),
        'specificity': Fraction(tn, tn + fp),
        'accuracy': Fraction(tp + tn, n)
    }


def audit():
    source = json.loads(SRC.read_text(encoding='utf-8'))['cases']['JANOUDI_2025']
    tp, fn, fp, tn = [int(source[k]) for k in ('tp', 'fn', 'fp', 'tn')]
    n = int(source['n'])
    assert (tp, fn, fp, tn, n) == (284, 3, 167, 3342, 3796)
    baseline = state(tp, fn, fp, tn, 0, 0)
    policy_rows, scenario_rows = [], []
    total_states = 0
    for label, m, published_fp_after, published_fn_after in zip(
        ['Low/Medium Includes', 'Low/Medium/High Includes'],
        source['simulated_review_counts'],
        source['simulated_remaining_fp'],
        source['simulated_remaining_fn']
    ):
        m, published_fp_after, published_fn_after = int(m), int(published_fp_after), int(published_fn_after)
        assert published_fn_after == fn
        correctable_fp = fp - published_fp_after
        correct_tp_at_risk = m - correctable_fp
        assert (m, correctable_fp, correct_tp_at_risk) in ((145, 102, 43), (221, 135, 86))
        # All possible deterministic override outcomes; these are mathematical
        # possibilities, not equally likely states and not observations.
        count = 0
        for x in range(correctable_fp + 1):
            for y in range(correct_tp_at_risk + 1):
                out = state(tp, fn, fp, tn, x, y)
                assert out['tp'] + out['fn'] == tp + fn
                assert out['fp'] + out['tn'] == fp + tn
                count += 1
        total_states += count
        assert count == (correctable_fp + 1) * (correct_tp_at_risk + 1)
        perfect = state(tp, fn, fp, tn, correctable_fp, 0)
        mistaken_one = state(tp, fn, fp, tn, correctable_fp, 1)
        optimistic_low90 = state(tp, fn, fp, tn, (9 * correctable_fp) // 10, 0)
        assert perfect['fp'] == published_fp_after
        assert perfect['fn'] == published_fn_after
        # A single wrongly overruled true Include reduces reference recall
        # despite near-identical precision, even if all FPs are corrected.
        assert mistaken_one['recall'] < baseline['recall']
        assert mistaken_one['precision'] > baseline['precision']
        def x_needed(q):
            return next((x for x in range(correctable_fp + 1)
                         if state(tp, fn, fp, tn, x, 0)['precision'] >= q), None)
        need80 = x_needed(Fraction(4, 5))
        need85 = x_needed(Fraction(85, 100))
        need90 = x_needed(Fraction(9, 10))
        max_y_for98 = max(y for y in range(correct_tp_at_risk + 1)
                          if state(tp, fn, fp, tn, correctable_fp, y)['recall'] >= Fraction(98, 100))
        policy_rows.append({
            'policy': label,
            'flagged_predicted_includes': m,
            'source_perfect_correction_available_fp': correctable_fp,
            'source_flagged_originally_correct_tp_at_risk': correct_tp_at_risk,
            'finite_override_states_not_probabilities': count,
            'perfect_precision_pct': fmt_percent(perfect['precision']),
            'perfect_recall_pct': fmt_percent(perfect['recall']),
            'one_wrong_override_precision_pct': fmt_percent(mistaken_one['precision']),
            'one_wrong_override_recall_pct': fmt_percent(mistaken_one['recall']),
            'max_wrong_overrides_to_keep_recall_at_least_98pct': max_y_for98,
            'fp_corrected_needed_for_precision_80pct_if_no_new_error': need80,
            'fp_corrected_needed_for_precision_85pct_if_no_new_error': need85,
            'fp_corrected_needed_for_precision_90pct_if_no_new_error': need90,
            'counterfactual_only': True
        })
        scenarios = [
            ('baseline_no_overrides', 0, 0),
            ('source_perfect_correction', correctable_fp, 0),
            ('ninety_percent_of_correctable_fp_floor_no_new_errors', (9 * correctable_fp)//10, 0),
            ('all_fp_corrected_one_new_false_negative', correctable_fp, 1),
        ]
        for title, x, y in scenarios:
            a = state(tp, fn, fp, tn, x, y)
            scenario_rows.append({
                'policy': label, 'counterfactual_scenario': title,
                'fp_correctly_overridden': x, 'tp_incorrectly_overridden': y,
                'tp': a['tp'], 'fn': a['fn'], 'fp': a['fp'], 'tn': a['tn'],
                'precision_pct': fmt_percent(a['precision']),
                'recall_pct': fmt_percent(a['recall']),
                'accuracy_pct': fmt_percent(a['accuracy']),
                'source_kind': 'MATHEMATICAL_COUNTERFACTUAL_NOT_HUMAN_OBSERVATION'
            })
    assert total_states == (103*44 + 136*87) == 16364
    assert [r['fp_corrected_needed_for_precision_80pct_if_no_new_error'] for r in policy_rows] == [96, 96]
    assert [r['fp_corrected_needed_for_precision_85pct_if_no_new_error'] for r in policy_rows] == [None, 117]
    assert [r['fp_corrected_needed_for_precision_90pct_if_no_new_error'] for r in policy_rows] == [None, None]
    assert [r['max_wrong_overrides_to_keep_recall_at_least_98pct'] for r in policy_rows] == [2, 2]
    return {
        'audit_pass': True,
        'source_doi': source['doi'],
        'baseline': {'tp': tp, 'fn': fn, 'fp': fp, 'tn': tn, 'n': n,
                     'precision_pct': fmt_percent(baseline['precision']),
                     'recall_pct': fmt_percent(baseline['recall'])},
        'policies': policy_rows,
        'scenarios': scenario_rows,
        'lattice_states_enumerated': total_states,
        'limitations': [
            'Post hoc deterministic possibilities, not observed human error or probabilistic prediction.',
            'Assumes fixed adjudicated reference, identical cohort, one binary final decision per flagged predicted Include, and no change to predicted Excludes.',
            'No reviewer minutes, review costs, independent second coding, or net labor effect is estimated.'
        ]
    }


def write_outputs(root=None):
    root = Path(root) if root else ROOT
    obj = audit()
    (root/'data'/'R35_AdjudicationEnvelope_Results.json').write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n',encoding='utf-8')
    with (root/'data'/'R35_AdjudicationEnvelope_Scenarios.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(obj['scenarios'][0].keys()));w.writeheader();w.writerows(obj['scenarios'])
    return obj

if __name__=='__main__':
    result=write_outputs()
    print(json.dumps({'audit_pass':result['audit_pass'], 'lattice_states_enumerated':result['lattice_states_enumerated'], 'policies':result['policies']}, indent=2))
