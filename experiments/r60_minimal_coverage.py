#!/usr/bin/env python3
"""Source-locked exploratory finite set-cover frontier for 99a R60.

Reuses archived Matsui/Takaesu decisions, never prompts a model. The portfolios
are SELECTED USING THE EVALUATION LABELS (oracle hindsight), not a deployable
or externally validated screening policy. All 59 runs reuse two source reviews.
"""
from __future__ import annotations
import csv, gzip, hashlib, io, itertools, json, math, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

PIN = 'd911eafc5299aa3ca41a6aacf0167931c81fcbbc'
ROOT = f'https://raw.githubusercontent.com/matsuikentaro1/jev-title-abstract-screening/{PIN}/'
SHA = {
'data/records.csv':'4287fa288b91e1e4d8b7d990f8df9bc4b3d954de86cfcf03623dc4d89b281dcb',
'data/predictions.csv.gz':'3ac88823815ed659bac2fb803a2b89334561b2ffd1fb80620e4f32f59fa5444c',
'data/runs.json':'1d8c2fc79610a0e8532dfb7df36044c6d7f7c2be769172fb2d1b8049720c8cc3',
'configuration/included_reports.json':'ed54c5f146c739872609334b96ca93d6b935186ed744ebc29b08efcde84f8db4',
}

def rawfile(path):
    request=urllib.request.Request(ROOT+path, headers={'User-Agent':'99a-r60-exploratory-hindsight-frontier/1.0'})
    with urllib.request.urlopen(request,timeout=90) as response: data=response.read()
    assert hashlib.sha256(data).hexdigest()==SHA[path], path
    return gzip.decompress(data) if path.endswith('.gz') else data

def rows(path):
    return list(csv.DictReader(io.StringIO(rawfile(path).decode('utf-8'))))

def main():
    records=rows('data/records.csv')
    preds=rows('data/predictions.csv.gz')
    runs=json.loads(rawfile('data/runs.json'))
    incl=json.loads(rawfile('configuration/included_reports.json'))
    assert len(records)==4527 and len(preds)==267093 and len(runs)==59
    n=len(records)
    ids={row['record_id']:i for i,row in enumerate(records)}
    reference={i for i,row in enumerate(records) if row['reference_retained']=='1'}
    assert len(reference)==113
    final={ids[rec_id] for entry in incl for rec_id in entry['record_ids']}
    assert len(final)==23 and final<=reference
    bycohort={c:set(i for i,r in enumerate(records) if r['dataset']==c) for c in ('takeshima','maruki')}
    runnames=[r['run_id'] for r in sorted(runs,key=lambda r:(r['condition'],int(r['rep'])))]
    byrun={r:i for i,r in enumerate(runnames)}
    masks=[0]*len(runnames)
    counts=Counter()
    for row in preds:
        ri=byrun[row['run_id']];j=ids[row['record_id']]
        keep=(float(row['probability_retained'])>=0.5) if row['probability_retained'] else row['decision']=='I'
        if keep:masks[ri]|=1<<j
        counts[ri]+=1
    assert all(counts[i]==n for i in range(len(runnames)))
    def mask_of(indices):
        result=0
        for i in indices:result|=1<<i
        return result
    refmask=mask_of(reference)
    finalmask=mask_of(final)
    cohort_masks={c:mask_of(idx) for c,idx in bycohort.items()}
    union59=0
    for m in masks:union59|=m
    available=union59&refmask
    inaccessible=refmask&~union59
    assert available.bit_count()==112 and inaccessible.bit_count()==1
    all59={'run_count':59,'records_retained':union59.bit_count(),'human_reference_retained':available.bit_count(),'final_report_id_retained':(finalmask&union59).bit_count(), 'missed_H_count':inaccessible.bit_count()}
    print('GLOBAL_UPPER '+json.dumps(all59,sort_keys=True))
    # Each k's Pareto-relevant witness uses the largest number of H positives recovered
    # and, among those attaining that maximum, the fewest total forwarded records.
    # This is a label-aware oracle tie-break and must never be deployed as measured.
    tested=0;frontier=[];minimum_complete=None
    for k in range(1,5):
        best=(-1,10**9,None,None)
        best_recall_for_minimum_work=(-1,10**9,None)
        for combo in itertools.combinations(range(len(masks)),k):
            select=0
            for j in combo: select|=masks[j]
            c=(select&refmask).bit_count()
            w=select.bit_count()
            tested+=1
            if c>best[0] or (c==best[0] and w<best[1]):
                best=(c,w,combo,select)
            if w<best_recall_for_minimum_work[1] or (w==best_recall_for_minimum_work[1] and c>best_recall_for_minimum_work[0]):
                best_recall_for_minimum_work=(c,w,combo)
        b,h,combo,selected=best
        line={'k':k,'combinations_enumerated':math.comb(59,k),'maximum_human_reference_positives':b,'oracle_minimum_retained_given_maximum_reference_positives':h,'final_report_ids_in_oracle_witness':(selected&finalmask).bit_count(),'oracle_witness_run_ids':[runnames[j] for j in combo], 'human_retained_by_cohort':{c:(selected&refmask&cm).bit_count() for c,cm in cohort_masks.items()},'retained_total_by_cohort':{c:(selected&cm).bit_count() for c,cm in cohort_masks.items()},'minimum_retained_records_any_k_portfolio':best_recall_for_minimum_work[1],'human_reference_at_minimum_retained':best_recall_for_minimum_work[0]}
        frontier.append(line)
        print('FRONTIER_ROW '+json.dumps(line,sort_keys=True))
        if b==112:
            minimum_complete=k
            break
    assert all(r['maximum_human_reference_positives']<=112 for r in frontier)
    # Exact independent identity for the selected witness: intersection of non-Includes
    # equals reference missed and is a complement of selected union.
    for line in frontier:
        chosen=[masks[byrun[name]] for name in line['oracle_witness_run_ids']]
        miss=refmask
        for m in chosen:miss &= ~m
        assert miss.bit_count()==113-line['maximum_human_reference_positives']
    report={'upstream_commit':PIN,'sources_sha256':SHA,'reference_stages':{'H':'human-retained-for-full-text','F':'eventually included report-linked record IDs'},'records':n,'predictions':len(preds),'runs':len(runs),'conditions':len({x['condition'] for x in runs}),'source_H':len(reference),'source_F':len(final),'source_conditional_fixed_050_upper':all59,'frontier':frontier,'complete_112_minimum_k_if_le_4':minimum_complete,'enumerated_portfolios':tested,'method':'exact exhaustive run-set enumeration for k=1..minimum_k (or k<=4), with evaluation-label-aware tie-break','not_admissible_claims':['not independent validations','not a prospective policy','not measured human work','not full true eligibility','not novel set-cover optimization','no threshold optimization is claimed']}
    Path('r60_oracle_frontier.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('R60_FRONTIER_PASS '+json.dumps({'records':n,'runs':len(runs),'tested':tested,'max_H':112,'minimum_k':minimum_complete,'results':'r60_oracle_frontier.json'},sort_keys=True))

if __name__=='__main__':main()
