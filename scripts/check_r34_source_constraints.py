#!/usr/bin/env python3
"""Post-hoc, conditional constraints from five printed journal reports.

This script never repairs, re-estimates, or replicates original authors' model runs.
The conditional integer solutions are falsification probes against common
reader inferences, NOT validated new confusion matrices for those articles.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
import json

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'data'/'R34_FiveSource_ConstraintInputs.json'

def two_decimals(value):
    return Decimal(value.numerator)/Decimal(value.denominator) if isinstance(value,Fraction) else Decimal(str(value))

def displays(value,places):
    q=Decimal('1').scaleb(-places)
    return two_decimals(value).quantize(q,rounding=ROUND_HALF_UP)

def check():
    inputs=json.loads(P.read_text(encoding='utf-8'))['cases']
    # Zhang: 61 records cannot be both 6.5% of 959 and 6.5% of 936 at 1 dp.
    z=inputs['ZHANG_2025']
    pct959=displays(Fraction(100*z['reported_mci_included'],z['abstract_and_table1_mci_records']),1)
    pct936=displays(Fraction(100*z['reported_mci_included'],z['methods_mci_records']),1)
    assert (str(pct959),str(pct936))==('6.4','6.5')

    # Insuk: source arithmetic was independently tested in R31. Do not replace it.
    from check_insuk_2025 import audit as insuk_audit
    i=insuk_audit()
    assert i['ok'] and len(i['results'])==3

    # Cao: an upper *coverage ceiling*, not deployed sensitivity, if all
    # unavailable full texts are discarded rather than routed elsewhere.
    c=inputs['CAO_2025']
    assert c['full_texts_available_for_test']==12690
    assert Decimal(c['source_reported_final_included_access_coverage_pct'])==Decimal('59.16')
    assumed_ten_k_h=Fraction(c['assumed_manual_abstract_seconds']*10000,3600)
    assert round(float(assumed_ten_k_h),2)==83.33

    # Janoudi: only flagged Include records are hypothetically human-corrected,
    # so the 3 baseline false negatives are never corrected by those policies.
    j=inputs['JANOUDI_2025']
    assert j['n']==sum(j[k] for k in ('tp','fn','fp','tn'))==3796
    base_errors=j['fp']+j['fn']
    solved=[]
    for count,fp,fn in zip(j['simulated_review_counts'],j['simulated_remaining_fp'],j['simulated_remaining_fn']):
        corrected=base_errors-fp-fn
        assert fn==j['fn'] and 0<=corrected<=count
        solved.append({'flagged_records':count,'fraction_of_corpus_pct_1dp':str(displays(Fraction(100*count,j['n']),1)),
                       'corrected_errors_if_perfect':corrected,
                       'fraction_of_total_errors_corrected_pct_1dp':str(displays(Fraction(100*corrected,base_errors),1)),
                       'remaining_false_negatives':fn})
    assert [q['corrected_errors_if_perfect'] for q in solved]==[102,135]

    # Li: a source-printed 0.77 recall and 0.34 precision can coexist with
    # a 1.00 rounded NPV, even though there are strictly positive FNs.
    # This IS NOT a reconstruction of the authors' private confusion matrix.
    l=inputs['LI_2026']; n=l['n'];pos=l['reference_positives'];neg=l['reference_negatives']
    assert n==pos+neg
    feasible=[]
    for tp in range(pos+1):
        if displays(Fraction(tp,pos),2)!=Decimal(l['printed_best_rule_deepseek_recall_2dp']):continue
        for predpos in range(tp,n+1):
            if predpos==0:continue
            if displays(Fraction(tp,predpos),2)!=Decimal(l['printed_best_rule_deepseek_precision_2dp']):continue
            fp=predpos-tp;fn=pos-tp;tn=neg-fp
            if min(fp,fn,tn)<0:continue
            if displays(Fraction(tn,tn+fn),2)!=Decimal(l['printed_best_rule_deepseek_npv_2dp']):continue
            feasible.append((tp,fn,fp,tn,predpos))
    assert len(feasible)==7 and {t[0] for t in feasible}=={87}
    assert {t[1] for t in feasible}=={26}
    predpos=sorted(t[4] for t in feasible)
    assert predpos==list(range(253,260))
    npvs=[float(Fraction(x[3],x[3]+x[1])) for x in feasible]
    assert all(0.995<x<1.0 for x in npvs)
    # Assumes all predicted positive records are manually screened; this
    # calculation is only a conditional queue fraction, not human hours.
    queue_reduction=[1-Fraction(x,n) for x in predpos]
    assert min(queue_reduction)>.95
    return {
        'ok':True,'scope':'five final publisher reports, printed-source conditional arithmetic only',
        'zhang':{'source_table_n':959,'source_methods_n':936,'source_included':61,
                 'percent_of_table_n_1dp':str(pct959),'percent_of_methods_n_1dp':str(pct936),
                 'published_percent_1dp':z['printed_inclusion_pct_one_decimal'],
                 'source_denominator_unresolved':True},
        'insuk':{'published_count_ambiguity':True,'source_specific_rows':len(i['results']),
                 'no_author_error_certified':True},
        'cao':{'reported_final_included_covered_percent':c['source_reported_final_included_access_coverage_pct'],
               'counterfactual_coverage_ceiling_if_all_unavailable_excluded_percent':c['source_reported_final_included_access_coverage_pct'],
               'assumed_ten_thousand_abstract_human_hours':str(displays(assumed_ten_k_h,2)),
               'no_observed_net_person_time':True},
        'janoudi':{'baseline_errors':base_errors,'simulated_cases':solved,'human_routing_executed':False},
        'li':{'shared_universe_assumption_necessary':True,'two_decimal_rounding_assumption_necessary':True,
              'conditionally_feasible_matrices':len(feasible),'feasible_tp':87,'feasible_fn':26,
              'feasible_predicted_include_counts':[predpos[0],predpos[-1]],
              'npv_exact_feasible_range':[round(min(npvs),6),round(max(npvs),6)],
              'counterfactual_auto_excluded_fraction_pct_range':[str(displays(Fraction(100*(n-predpos[-1]),n),2)),str(displays(Fraction(100*(n-predpos[0]),n),2))],
              'not_the_actual_reported_model_confusion_matrix':True,'no_empirical_person_time':True},
        'study_inclusion_denominator_unchanged':True,
        'claim':'Selected source-view constraints, not systematic prevalence, revised original authors results, net personnel savings, or a model replication'}

if __name__=='__main__': print(json.dumps(check(),indent=2,ensure_ascii=False))
