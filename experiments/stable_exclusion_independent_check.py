#!/usr/bin/env python3
"""Independent recordwise check of robust unanimous-exclusion counts and audit sizes.
Separate implementation: no imports from stable_exclusion_audit.py.
"""
import csv, gzip, hashlib, io, json, urllib.request
from collections import defaultdict
from pathlib import Path

UPSTREAM='https://raw.githubusercontent.com/matsuikentaro1/jev-title-abstract-screening/d911eafc5299aa3ca41a6aacf0167931c81fcbbc/'
SHA={
'data/records.csv':'4287fa288b91e1e4d8b7d990f8df9bc4b3d954de86cfcf03623dc4d89b281dcb',
'data/predictions.csv.gz':'3ac88823815ed659bac2fb803a2b89334561b2ffd1fb80620e4f32f59fa5444c',
'data/runs.json':'1d8c2fc79610a0e8532dfb7df36044c6d7f7c2be769172fb2d1b8049720c8cc3',
'configuration/reference_label_provenance.json':'fd84e981fd70849f3914055ee0d60679b8b5e32206b7a1c08ca0763fd0bca6da',
'configuration/included_reports.json':'ed54c5f146c739872609334b96ca93d6b935186ed744ebc29b08efcde84f8db4',
}

def get(name):
    req=urllib.request.Request(UPSTREAM+name,headers={'User-Agent':'99a-independent-persistence-audit'})
    with urllib.request.urlopen(req,timeout=90) as r: raw=r.read()
    assert hashlib.sha256(raw).hexdigest()==SHA[name]
    return gzip.decompress(raw) if name.endswith('.gz') else raw

def parse(name):return list(csv.DictReader(io.StringIO(get(name).decode('utf-8'))))

def audit95(N,B):
    if B==0:return None
    p_none=1.0
    for n in range(1,N+1):
        # Independently use the sequential, exact-without-replacement probability recurrence.
        p_none*=max(0,N-B-n+1)/(N-n+1)
        if p_none<=.05:
            return n
    raise ValueError('Impossible audit size')

def run():
    records=parse('data/records.csv')
    predictions=parse('data/predictions.csv.gz')
    runs=json.loads(get('data/runs.json'))
    assert len(records)==4527 and len(predictions)==267093 and len(runs)==59
    source_provenance=json.loads(get('configuration/reference_label_provenance.json'))
    included=json.loads(get('configuration/included_reports.json'))
    saved=json.loads(Path('source_conditional_persistence_results.json').read_text())
    positive_by_topic={}
    for row in records:
        if row['reference_retained']=='1':
            positive_by_topic.setdefault(row['dataset'],set()).add(row['record_id'])
    run_ids=defaultdict(list)
    for r in runs:
        run_ids[r['condition']].append(r['run_id'])
    excludes=defaultdict(set)
    for p in predictions:
        positive= (float(p['probability_retained'])>=.5) if p['probability_retained'] else (p['decision']=='I')
        if not positive:
            excludes[p['run_id']].add(p['record_id'])
    expected={'JevChoice_plus_GPT5default_plus_GPT6':('choice-v4','gpt-5-mini-default','gpt-6-astra-default'),
       'Three_LLM_configs_minimal_default_GPT6':('gpt-5-mini-minimal','gpt-5-mini-default','gpt-6-astra-default')}
    checks=[]
    for row in saved['rows']:
        names=expected[row['family']]
        cohort=row['cohort']
        p=positive_by_topic[cohort]
        # An all-run set intersection is not a loop over mixed combinations.
        every_run_excludes=set(p)
        for family in names:
            for rr in run_ids[family]:every_run_excludes.intersection_update(excludes[rr])
        assert len(every_run_excludes)==row['same_ids_blind_in_every_combination_count']
        hashed=hashlib.sha256(('\n'.join(sorted(every_run_excludes))+'\n').encode()).hexdigest()
        assert hashed==row['same_ids_blind_in_every_combination_sha256']
        first=row['sample_first_combination']
        assert audit95(first['unanimously_excluded_total'],first['blind_human_retained'])==first['exact_audit_size_for_95pct_chance_detect_at_least_one_source_positive']
        checks.append({'family':row['family'],'cohort':cohort,'persistent_reference_positive_exclusions':len(every_run_excludes),'sha256':hashed,'audit95':audit95(first['unanimously_excluded_total'],first['blind_human_retained'])})
    assert len(checks)==4
    # Secondary check across the union of four model configurations; not a new independent study.
    all_four=('choice-v4','gpt-5-mini-minimal','gpt-5-mini-default','gpt-6-astra-default')
    four_core={}
    for cohort,p in positive_by_topic.items():
        v=set(p)
        for family in all_four:
            for rid in run_ids[family]:v.intersection_update(excludes[rid])
        four_core[cohort]=len(v)
    base_families=('choice-v4','gpt-5-mini-default','gpt-6-astra-default')
    extra_families=tuple(sorted(set(run_ids)-set(base_families)))
    marginal=[]
    all59_core={}
    all59_core_ids={}
    for cohort,p in positive_by_topic.items():
        baseline_core=set(p)
        for family in base_families:
            for rid in run_ids[family]: baseline_core.intersection_update(excludes[rid])
        full_core=set(p)
        for family in run_ids:
            for rid in run_ids[family]: full_core.intersection_update(excludes[rid])
        all59_core[cohort]=len(full_core)
        all59_core_ids[cohort]=sorted(full_core)
        assert len(full_core)<=len(baseline_core)
        for family in extra_families:
            with_added=set(baseline_core)
            for rid in run_ids[family]:with_added.intersection_update(excludes[rid])
            marginal.append({'cohort':cohort,'additional_configuration':family,
               'baseline_all_run_misses':len(baseline_core),
               'remaining_misses_after_adding_all_runs_of_configuration':len(with_added),
               'reference_positive_records_recovered_by_added_configuration':len(baseline_core)-len(with_added),
               'additional_run_count':len(run_ids[family])})
    expected_full=saved['all_59_run_union_source_conditional_certificate']
    assert expected_full['archived_decision_vectors']==len(runs)==59
    assert expected_full['all_run_union_reference_retention']==len(positive_by_topic['maruki'])+len(positive_by_topic['takeshima'])-sum(all59_core.values())
    assert expected_full['human_retained_positive_records_excluded_in_every_archived_run']==sum(all59_core.values())
    assert {d:sorted(ids) for d,ids in all59_core_ids.items()}==expected_full['by_cohort_persistent_source_record_ids']
    witness_ids=[i for ids in all59_core_ids.values() for i in ids]
    expected_hash=hashlib.sha256(('\n'.join(sorted(witness_ids))+'\n').encode()).hexdigest()
    assert expected_hash==expected_full['persistent_source_record_ids_sha256']
    source_by_id={r['record_id']:r for r in records}
    corrections={r['record_id']:r.get('origin','') for r in source_provenance.get('corrections_and_confirmations',[])}
    final_ids=set().union(*(set(r['record_ids']) for r in included))
    source_witness=[]
    for cohort,ids in all59_core_ids.items():
        for i in ids:
            rr=source_by_id[i]
            witness={'record_id':i,'cohort':cohort,'source_row':rr.get('source_row'),
                     'abstract_missing':rr.get('abstract_missing'),
                     'reference_retained':rr.get('reference_retained'),
                     'in_original_final_included_report_id_set':i in final_ids,
                     'reference_label_correction_provenance':corrections.get(i,'not listed in correction register')}
            source_witness.append(witness)
            print('GLOBAL_SOURCE_WITNESS '+json.dumps(witness,sort_keys=True))
    out={'all_59_run_source_witness':source_witness,'pass':True,'validation_count':len(checks),'result_rows':checks,'four_configuration_persistent_core_count':four_core,
         'all_59_run_persistent_core_count':all59_core,'conditional_configuration_rescue':marginal,
         'sampling_bound_interpretation':'Conditional demonstration: assumes known number of reference disagreements and perfect identification in uniform random sampling; not a real prospective study.'}
    Path('stable_exclusion_independent_verification.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    for c in checks:print('INDEPENDENT_PERSISTENCE_ROW '+json.dumps(c,sort_keys=True))
    for r in marginal:print('CONFIG_RESCUE_ROW '+json.dumps(r,sort_keys=True))
    print('INDEPENDENT_PERSISTENCE_PASS '+json.dumps({'verified':len(checks),'four_configuration_core':four_core,'all59_core':all59_core},sort_keys=True))

if __name__=='__main__':run()
