#!/usr/bin/env python3
"""Source-pinned retrospective consensus audit of Matsui & Takaesu (2026) saved predictions.
No model inference. Third-party raw predictions are never redistributed.
"""
import csv
import gzip
import hashlib
import io
import itertools
import json
import statistics
import urllib.request
from collections import defaultdict
from pathlib import Path

PIN = 'd911eafc5299aa3ca41a6aacf0167931c81fcbbc'
EXPECTED = {
    'data/predictions.csv.gz': '3ac88823815ed659bac2fb803a2b89334561b2ffd1fb80620e4f32f59fa5444c',
    'data/records.csv': '4287fa288b91e1e4d8b7d990f8df9bc4b3d954de86cfcf03623dc4d89b281dcb',
    'data/runs.json': '1d8c2fc79610a0e8532dfb7df36044c6d7f7c2be769172fb2d1b8049720c8cc3',
    'configuration/included_reports.json': 'ed54c5f146c739872609334b96ca93d6b935186ed744ebc29b08efcde84f8db4'
}
BASE = f'https://raw.githubusercontent.com/matsuikentaro1/jev-title-abstract-screening/{PIN}/'

def source(path):
    req=urllib.request.Request(BASE+path,headers={'User-Agent':'99a-research-source-conditional-audit/1.0'})
    with urllib.request.urlopen(req,timeout=90) as r: data=r.read()
    digest=hashlib.sha256(data).hexdigest()
    assert digest==EXPECTED[path], (path,digest,EXPECTED[path])
    return gzip.decompress(data) if path.endswith('.gz') else data

def parse_csv(data): return list(csv.DictReader(io.StringIO(data.decode('utf8'))))

def analyze():
    records=parse_csv(source('data/records.csv'))
    runs=json.loads(source('data/runs.json'))
    preds=parse_csv(source('data/predictions.csv.gz'))
    included=json.loads(source('configuration/included_reports.json'))
    assert len(records)==4527 and len(runs)==59 and len(preds)==4527*59
    reference={r['record_id'] for r in records if r['reference_retained']=='1'}
    assert len(reference)==113
    cohort={d:{r['record_id'] for r in records if r['dataset']==d} for d in ('takeshima','maruki')}
    assert {d:len(v) for d,v in cohort.items()}=={'takeshima':1381,'maruki':3146}
    assert {d:len(v&reference) for d,v in cohort.items()}=={'takeshima':26,'maruki':87}
    final_studies={d:set() for d in cohort}
    for r in included:
        if r['dataset'] in final_studies:
            final_studies[r['dataset']].update(r.get('record_ids',[]))
    groups=defaultdict(list)
    for r in runs: groups[r['condition']].append((int(r['rep']),r['run_id']))
    assert len(groups)==8
    ids={r['record_id'] for r in records}
    positive=defaultdict(set)
    run_seen=defaultdict(set)
    for r in preds:
        run_id=r['run_id'];i=r['record_id']
        assert i in ids and i not in run_seen[run_id]
        run_seen[run_id].add(i)
        score=r['probability_retained']
        vote=(float(score)>=0.5) if score else (r['decision']=='I')
        assert r['decision'] in ('I','E')
        if vote:positive[run_id].add(i)
    assert all(len(run_seen[r['run_id']])==len(ids) for r in runs)

    def row(condition, run_ids, dataset):
        univ=cohort[dataset]; ref=univ&reference
        s=[positive[r]&univ for r in run_ids]
        unanimous_positive=set.intersection(*s)
        any_positive=set.union(*s)
        unanimous_negative=univ-any_positive
        discordant=any_positive-unanimous_positive
        return {
            'condition':condition,'dataset':dataset,'n_runs':len(run_ids),'n_records':len(univ),
            'reference_positives':len(ref),
            'average_individual_FNs':sum(len(ref-a) for a in s)/len(s),
            'intersection_FN':len(ref-unanimous_positive),
            'union_FN':len(ref-any_positive),
            'all_negative_reference_positives':len(unanimous_negative&ref),
            'discordant_reference_positives':len(discordant&ref),
            'unanimous_positive_reference_positives':len(unanimous_positive&ref),
            'automatic_negative_records':len(unanimous_negative),
            'automatic_positive_records':len(unanimous_positive),
            'human_review_disagreements':len(discordant),
            'fraction_human_review_disagreement':len(discordant)/len(univ),
            'source_final_included_total':len(univ&final_studies[dataset]),
            'source_final_included_all_negative':len(final_studies[dataset]&unanimous_negative),
        }

    rows=[]; ranges=[]
    for condition,rep_runs in sorted(groups.items()):
        allr=[r for _,r in sorted(rep_runs)]
        assert len(allr)==(3 if condition.startswith('gpt-') else 10), (condition,len(allr))
        triplets=list(itertools.combinations(allr,3))
        for d in cohort:
            current=[row(condition, rr,d) for rr in triplets]
            chosen=row(condition,allr[:3],d)
            rows.append(chosen)
            ranges.append({'condition':condition,'dataset':d,'triplets':len(triplets),
                'blindspot_min':min(x['all_negative_reference_positives'] for x in current),
                'blindspot_max':max(x['all_negative_reference_positives'] for x in current),
                'disagreement_min':min(x['human_review_disagreements'] for x in current),
                'disagreement_max':max(x['human_review_disagreements'] for x in current),
                'any_unanimous_false_exclusion':sum(x['all_negative_reference_positives']>0 for x in current),
                'final_included_blindspot_min':min(x['source_final_included_all_negative'] for x in current),
                'final_included_blindspot_max':max(x['source_final_included_all_negative'] for x in current),
            })
    result={'design':'retrospective post-hoc decisions across repeated runs of the same models; no human corrections performed',
      'source_commit':PIN, 'source_doi':'10.3390/info17111160',
      'sources_sha256':EXPECTED, 'source_records':len(records),'source_predictions':len(preds),
      'conditions':{k:len(v) for k,v in groups.items()},'first_three_rows':rows,'triplet_range_rows':ranges,
      'limits':['Human screening-retention labels, not fully adjudicated underlying eligibility',
        'Repeated same-model runs are dependent, not three independent model families',
        'Ideal disagreement resolution only describes a counterfactual; it cannot recover unanimous false exclusions',
        'No human person-time, no model inference or prospective intervention']}
    outfile=Path('external_consensus_results.json')
    outfile.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for row_ in rows:
        print('AUDIT_ROW '+json.dumps({k:row_[k] for k in ('condition','dataset','reference_positives','average_individual_FNs','intersection_FN','union_FN','automatic_negative_records','human_review_disagreements','source_final_included_all_negative')},sort_keys=True))
    for rr in ranges:
        print('RANGE_ROW '+json.dumps(rr,sort_keys=True))
    print('AUDIT_PASS',json.dumps({'upstream':PIN,'records':len(records),'predictions':len(preds),'conditions':len(groups),'rows':len(rows),'out':str(outfile)}))

if __name__=='__main__': analyze()
