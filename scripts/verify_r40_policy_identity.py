#!/usr/bin/env python3
"""R40 independent source-derived policy-accounting certificate (standard library).

Reads public per-review derived CSV from the archived 99a external benchmark; does NOT
retrain classifiers or inspect/redistribute third-party candidate record abstracts.
"""
import argparse, csv, hashlib, json, math
from collections import defaultdict
from pathlib import Path

EXPECTED_HOLDOUT = {
    'test': {'records':30783,'positives':315,'review_units':8},
    'external':{'records':138902,'positives':598,'review_units':22},
}
EXPECTED_95 = {'test':(29247,1536),'external':(131967,6935)}
EXPECTED_FN = {('test',50):{'B0':67,'B1':49},('test',90):{'B0':0,'B1':2},
               ('external',50):{'B0':74,'B1':81},('external',90):{'B0':4,'B1':6}}

def cert(csv_path):
    raw=Path(csv_path).read_bytes()
    rows=list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
    paired=[r for r in rows if r['policy']=='matched' and r['split'] in EXPECTED_HOLDOUT]
    assert len(paired)==1680,(len(rows),len(paired))
    keys=defaultdict(dict)
    zero_rows=0
    for r in paired:
        N=int(r['records']); H=int(r['human_review']); P=int(r['provisional_include']); E=int(r['auto_excluded'])
        U=int(r['mandatory_review']); b=int(r['budget_pct'])
        R=math.ceil(b*N/100)
        assert H==max(U,R),(r['split'],r['review'],b,H,U,R)
        assert P==min(N//20,N-H)
        assert E==N-H-P and E>=0
        assert 0<=int(r['final_positives_auto_excluded'])<=E
        if b>=95:
            assert E==0 and int(r['final_positives_auto_excluded'])==0
            zero_rows+=1
        k=(r['split'],r['review'],b,int(r['simulated_abstract_mask_pct']))
        assert r['method'] not in keys[k]
        keys[k][r['method']]=r
    assert len(keys)==840
    pair_overruns=0
    for k,v in keys.items():
        assert set(v)=={'B0','B1'},(k,set(v))
        a,b=v['B0'],v['B1']
        for x in ('human_review','provisional_include','auto_excluded','records','final_reference_positives','mandatory_review'):
            assert a[x]==b[x],(k,x,a[x],b[x])
        if int(a['human_review'])>math.ceil(int(a['records'])*int(a['budget_pct'])/100):
            pair_overruns+=1
    assert zero_rows==480
    assert pair_overruns==184
    observed={}
    for split in ('test','external'):
        for budget in (50,90,95):
            sel=[r for r in paired if r['split']==split and int(r['budget_pct'])==budget and int(r['simulated_abstract_mask_pct'])==0]
            assert len(sel)==2*EXPECTED_HOLDOUT[split]['review_units'],len(sel)
            st={}
            for method in ('B0','B1'):
                u=[r for r in sel if r['method']==method]
                st[method]={key:sum(int(r[key]) for r in u) for key in ('records','final_reference_positives','human_review','provisional_include','auto_excluded','final_positives_auto_excluded')}
                assert st[method]['records']==EXPECTED_HOLDOUT[split]['records']
                assert st[method]['final_reference_positives']==EXPECTED_HOLDOUT[split]['positives']
            if budget==95:
                assert (st['B0']['human_review'],st['B0']['provisional_include'])==EXPECTED_95[split]
                assert all(s['auto_excluded']==0 for s in st.values())
            if budget in (50,90):
                assert {m:st[m]['final_positives_auto_excluded'] for m in st}==EXPECTED_FN[(split,budget)]
            observed[f'{split}_{budget}']=st
    return {'version':'R40','scope':'Post hoc arithmetic readback of derived benchmark CSV; not raw-source rerun',
            'source_csv_sha256':hashlib.sha256(raw).hexdigest(),'source_csv_bytes':len(raw),
            'all_derived_rows':len(rows),'matched_policy_rows':len(paired),'matched_review_budget_mask_pairs':len(keys),
            'budget_ge_95_structurally_no_auto_exclusion_rows':zero_rows,
            'scenario_pairs_over_nominal_human_budget':pair_overruns,
            'distinct_test_review_units':len({r['review'] for r in paired if r['split']=='test'}),
            'distinct_external_review_units':len({r['review'] for r in paired if r['split']=='external'}),
            'unmasked_observed_routing':observed,
            'theory_checks':{'all_rows_N_equals_H_plus_P_plus_E':True,'all_rows_H_equals_max_mandatory_and_nominal':True,
               'all_rows_P_equals_5percent_cap':True,'zero_auto_FN_is_structural_at_95plus':True},
            'claims_denied':['No fuzzy B2 calibration','No observed human review times','No causal effect',
                'No title/abstract reference separate from final inclusion','No 840 independent experiments']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input_csv');p.add_argument('output_json');a=p.parse_args()
    o=cert(a.input_csv)
    Path(a.output_json).write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','pairs':o['matched_review_budget_mask_pairs'],'zero_rows':o['budget_ge_95_structurally_no_auto_exclusion_rows']}))
