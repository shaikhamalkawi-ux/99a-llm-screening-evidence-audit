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
    out={'pass':True,'validation_count':len(checks),'result_rows':checks,'four_configuration_persistent_core_count':four_core,
         'sampling_bound_interpretation':'Conditional demonstration: assumes known number of reference disagreements and perfect identification in uniform random sampling; not a real prospective study.'}
    Path('stable_exclusion_independent_verification.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    for c in checks:print('INDEPENDENT_PERSISTENCE_ROW '+json.dumps(c,sort_keys=True))
    print('INDEPENDENT_PERSISTENCE_PASS '+json.dumps({'verified':len(checks),'four_configuration_core':four_core},sort_keys=True))

if __name__=='__main__':run()
