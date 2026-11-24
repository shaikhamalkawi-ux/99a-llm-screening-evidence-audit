#!/usr/bin/env python3
"""R60 cross-review transfer diagnostic for archived run-set policies.

Pre-selection in the source review uses ONLY that review's published reference and
record throughput, never the held-out review's labels. Testing is retrospective
on the second of two reused reviews, not an independent prospective experiment.
"""
from __future__ import annotations
import csv, gzip, hashlib, io, itertools, json, urllib.request
from collections import Counter
from pathlib import Path
ROOT='https://raw.githubusercontent.com/matsuikentaro1/jev-title-abstract-screening/d911eafc5299aa3ca41a6aacf0167931c81fcbbc/'
CHECK={
'data/records.csv':'4287fa288b91e1e4d8b7d990f8df9bc4b3d954de86cfcf03623dc4d89b281dcb',
'data/predictions.csv.gz':'3ac88823815ed659bac2fb803a2b89334561b2ffd1fb80620e4f32f59fa5444c',
'data/runs.json':'1d8c2fc79610a0e8532dfb7df36044c6d7f7c2be769172fb2d1b8049720c8cc3',
'configuration/included_reports.json':'ed54c5f146c739872609334b96ca93d6b935186ed744ebc29b08efcde84f8db4',
}
def read(path):
    req=urllib.request.Request(ROOT+path,headers={'User-Agent':'99a-r60-crossreview-transfer/1.0'})
    with urllib.request.urlopen(req,timeout=90) as f: b=f.read()
    assert hashlib.sha256(b).hexdigest()==CHECK[path],path
    return gzip.decompress(b) if path.endswith('.gz') else b
def csvrows(path):return list(csv.DictReader(io.StringIO(read(path).decode('utf-8'))))
def main():
    records=csvrows('data/records.csv'); predictions=csvrows('data/predictions.csv.gz')
    runs=json.loads(read('data/runs.json')); included=json.loads(read('configuration/included_reports.json'))
    assert len(records)==4527 and len(predictions)==267093 and len(runs)==59
    names=sorted(r['run_id'] for r in runs); idx={x:i for i,x in enumerate(names)}
    ri={r['record_id']:j for j,r in enumerate(records)}
    fullmask=(1<<len(records))-1
    selected=[0]*59;seen=Counter()
    for r in predictions:
        j=idx[r['run_id']];i=ri[r['record_id']]
        positive=(float(r['probability_retained'])>=.5) if r['probability_retained'] else r['decision']=='I'
        if positive:selected[j]|=1<<i
        seen[j]+=1
    assert all(seen[j]==4527 for j in range(59))
    def mask(filt):
        m=0
        for i,r in enumerate(records):
            if filt(r):m|=1<<i
        return m
    U={d:mask(lambda r:r['dataset']==d) for d in ('takeshima','maruki')}
    H={d:mask(lambda r:r['dataset']==d and r['reference_retained']=='1') for d in U}
    F={d:sum(1<<ri[i] for ent in included if ent['dataset']==d for i in ent['record_ids']) for d in U}
    assert [(U[d].bit_count(),H[d].bit_count()) for d in U]==[(1381,26),(3146,87)]
    rows=[]
    for k in (1,2,3):
        for source,test in (('takeshima','maruki'),('maruki','takeshima')):
            # The optimisation below MUST NOT reference H[test] or U[test].
            best=(-1,10**9,(),0)
            for combo in itertools.combinations(range(59),k):
                union=0
                for j in combo:union|=selected[j]
                h=(union&H[source]).bit_count()
                w=(union&U[source]).bit_count()
                if h>best[0] or (h==best[0] and w<best[1]):best=(h,w,combo,union)
            train_h,train_w,combo,full_union=best
            assert train_h==(full_union&H[source]).bit_count()
            result={'selection_review':source,'held_out_review':test,'number_of_runs':k,
                    'searched_combinations':int(__import__('math').comb(59,k)),
                    'label_aware_selection_on_training_only':True,
                    'selected_run_ids':[names[j] for j in combo],
                    'train_retained_source_positives':train_h,'train_reference_positives':H[source].bit_count(),
                    'train_forwarded_records':train_w,'train_total_records':U[source].bit_count(),
                    'heldout_retained_source_positives':(full_union&H[test]).bit_count(),
                    'heldout_reference_positives':H[test].bit_count(),
                    'heldout_forwarded_records':(full_union&U[test]).bit_count(),
                    'heldout_total_records':U[test].bit_count(),
                    'heldout_final_report_ids_retained':(full_union&F[test]).bit_count(),
                    'heldout_final_report_ids_total':F[test].bit_count()}
            rows.append(result)
            print('TRANSFER_ROW '+json.dumps(result,sort_keys=True))
    assert len(rows)==6
    output={'design':'Two-way cross-topic holdout on two reviews from one archive; runs chosen using only the training review labels and forwarded counts; all results retrospective and selection is overfit','source_pin':'d911eafc5299aa3ca41a6aacf0167931c81fcbbc','source_hashes':CHECK,'records':4527,'runs':59,'predictions':267093,'transfer_rows':rows,'claims_not_admitted':['not generalization to new model instances or review fields','not a deployment rule','not measured human hours or model execution costs','not an independent external randomized validation','selected review directions share source outputs and 59 run IDs']}
    Path('r60_transfer_diagnostic.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print('TRANSFER_PASS '+json.dumps({'rows':len(rows),'records':4527,'predictions':267093,'selection_uses_no_heldout_reference':True},sort_keys=True))
if __name__=='__main__':main()
