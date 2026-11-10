#!/usr/bin/env python3
"""R36: exact source-conditional two-objective review certificate.

Every input is a printed aggregate from Janoudi (2025) already admitted in
R34. No human error probability, real intervention, or person-time is inferred.
This file is an independent *derivation* of R35, not a replacement for R35.
"""
import csv
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/R34_FiveSource_ConstraintInputs.json"


def ceiling(q):
    assert isinstance(q, F)
    return -(-q.numerator // q.denominator)


def floor_fraction(q):
    assert isinstance(q, F)
    return q.numerator // q.denominator


def derived(C, T, A=284, FNs=3, B=167):
    assert C <= B and T <= A
    positives = A + FNs
    base = F(A, A + B)
    grid = {(x, y) for x in range(C+1) for y in range(T+1)}
    assert len(grid) == (C+1)*(T+1)
    def precision(x,y): return F(A-y, A-y+B-x)
    def recall(y): return F(A-y,positives)
    def threshold(p, y):
        # P >= p iff x >= B+A-A/p+((1-p)/p)*y
        assert F(0) < p <= F(1)
        return max(0, ceiling(F(A+B) - F(A)/p + (F(1)-p)*y/p))
    def max_y(r):
        assert F(0) <= r <= F(1)
        return min(T, floor_fraction(F(A)-r*positives))
    out=[]
    for p,r in [(F(4,5),F(49,50)), (F(17,20),F(49,50)), (F(9,10),F(49,50))]:
        brute=[(x,y) for (x,y) in grid if precision(x,y)>=p and recall(y)>=r]
        formula=[(x,y) for y in range(T+1) for x in range(C+1) if x>=threshold(p,y) and y<=max_y(r)]
        assert set(brute)==set(formula)
        xrows=[{'y':y,'min_fp_corrections':threshold(p,y) if threshold(p,y)<=C else None}
               for y in range(max(0,max_y(r))+1)]
        out.append({'precision_target':f'{p.numerator}/{p.denominator}',
                    'recall_target':f'{r.numerator}/{r.denominator}',
                    'feasible_policy_tagged_states_not_probabilities':len(brute),
                    'min_corrections_by_permitted_y':xrows,
                    'feasible':bool(brute)})
    assert all((precision(x,y)>base) == (A*x>B*y) for x,y in grid)
    return {
        'C':C,'T':T,'policy_tagged_states':len(grid),
        'feasible_target_certificates':out,
        'all_fp_and_all_tp_reversed':{
            'tp':A-T,'fp':B-C,'fn':FNs+T,
            'precision_fraction':f'{precision(C,T).numerator}/{precision(C,T).denominator}',
            'recall_fraction':f'{recall(T).numerator}/{recall(T).denominator}',
            'precision_pct':f'{float(precision(C,T))*100:.4f}',
            'recall_pct':f'{float(recall(T))*100:.4f}'},
        'precision_gain_iff':'284*x > 167*y',
        'recall_equals_baseline_iff':'y=0',
    }


def audit():
    source=json.loads(INPUT.read_text(encoding='utf-8'))['cases']['JANOUDI_2025']
    assert [source[k] for k in ('tp','fn','fp','tn','n')] == [284,3,167,3342,3796]
    C1=source['fp']-source['simulated_remaining_fp'][0]
    C2=source['fp']-source['simulated_remaining_fp'][1]
    T1=source['simulated_review_counts'][0]-C1
    T2=source['simulated_review_counts'][1]-C2
    assert (C1,T1,C2,T2)==(102,43,135,86)
    p1=derived(C1,T1);p2=derived(C2,T2)
    small={(x,y) for x in range(C1+1) for y in range(T1+1)}
    large={(x,y) for x in range(C2+1) for y in range(T2+1)}
    assert small.issubset(large)
    assert len(small)+len(large)==16364 and len(small|large)==11832
    # Nested queues: 76 extra flags comprise 33 false Includes and 43 true Includes.
    u,v=C2-C1,T2-T1
    assert (u,v,u+v)==(33,43,76)
    def prec(x,y):return F(284-y,451-x-y)
    assert all((prec(x+du,y+dv)>prec(x,y)) == ((284-y)*du>(167-x)*dv)
               for x in [0,20,96,102] for y in [0,2,20,43]
               for du in [0,1,12,33] for dv in [0,1,15,43])
    # Source-linked explicit policy expansion example: all added FP corrected,
    # but all added true Includes wrongly excluded in a hypothetical expansion.
    expanded={'small_x':102,'small_y':0,'extra_corrected_false_includes':33,
              'extra_wrongly_excluded_true_includes':43,'large_x':135,'large_y':43,
              'precision_pct':f'{float(prec(135,43))*100:.4f}',
              'recall_pct':f'{float(F(241,287))*100:.4f}'}
    # Strong disclosure on policy consistency: these paired comparisons presume
    # the same choices on the 145 citations shared by both routing policies.
    result={'version':'R36','source_doi':source['doi'],
        'source_only_post_hoc_counterfactual_not_human_measurement':True,
        'baseline_matrix':[284,3,167,3342],
        'policy_145':p1,'policy_221':p2,
        'policy_tagged_states_total':len(small)+len(large),
        'distinct_untagged_confusion_matrices':len(small|large),
        'nested_extra_flags':{'false_includes':u,'true_includes':v},
        'nested_precision_increase_iff':'(284-y)*delta_x > (167-x)*delta_y',
        'nested_policy_counterexample':expanded,
        'limits':['No probabilities assigned to count states','No observed human correction/errors/time',
                  'No review of initial model Excludes','Reference fixed to source adjudication',
                  'Cannot transport to other human-routing policies or cohorts without new inputs']}
    assert result['policy_145']['feasible_target_certificates'][0]['feasible_policy_tagged_states_not_probabilities']==19
    assert result['policy_221']['feasible_target_certificates'][0]['feasible_policy_tagged_states_not_probabilities']==118
    assert result['policy_221']['feasible_target_certificates'][1]['feasible_policy_tagged_states_not_probabilities']==55
    return result


def write_outputs():
    obj=audit()
    (ROOT/'data/R36_JointThreshold_Certificates.json').write_text(
        json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (ROOT/'data/R36_JointTarget_Counts.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['policy','precision_min_fraction','recall_min_fraction',
                                   'number_of_feasible_count_states_NOT_probabilities'])
        for name in ['policy_145','policy_221']:
            for cert in obj[name]['feasible_target_certificates']:
                w.writerow([name,cert['precision_target'],cert['recall_target'],
                            cert['feasible_policy_tagged_states_not_probabilities']])
    return obj

if __name__=='__main__':
    a=write_outputs()
    print(json.dumps({'status':'PASS','policy_tagged':a['policy_tagged_states_total'],
                      'unique_matrices':a['distinct_untagged_confusion_matrices']}))
