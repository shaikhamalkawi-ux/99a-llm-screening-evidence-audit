#!/usr/bin/env python3
"""R61 independent endpoint-contrast certificate; alternative sets implementation.
The original third-party per-record predictions are read from source-pinned upstream
and never redistributed. This only writes aggregate counts and witness run IDs.
"""
import csv, io, itertools, json, math
from collections import Counter
from pathlib import Path
from r60_minimal_coverage import PIN, SHA, rawfile

def main():
    records=list(csv.DictReader(io.StringIO(rawfile('data/records.csv').decode())))
    predictions=list(csv.DictReader(io.StringIO(rawfile('data/predictions.csv.gz').decode())))
    run_meta=json.loads(rawfile('data/runs.json'))
    report_meta=json.loads(rawfile('configuration/included_reports.json'))
    id_to_ix={r['record_id']:j for j,r in enumerate(records)}
    human={i for i,r in enumerate(records) if r['reference_retained']=='1'}
    final={id_to_ix[s] for report in report_meta for s in report['record_ids']}
    run_names=sorted(r['run_id'] for r in run_meta)
    run_includes={k:set() for k in run_names}
    counts=Counter()
    for r in predictions:
        key=r['run_id']
        keep=(float(r['probability_retained'])>=0.5 if r['probability_retained'] else r['decision']=='I')
        if keep:run_includes[key].add(id_to_ix[r['record_id']])
        counts[key]+=1
    assert len(records)==4527 and len(predictions)==267093
    assert len(run_names)==59 and all(counts[k]==4527 for k in run_names)
    assert len(human)==113 and len(final)==23 and final.issubset(human)
    baseline=json.loads(Path('r61_reference_blindness.json').read_text())
    pairs=Counter(); hdist=Counter(); fdist=Counter(); distinct_pairs=Counter(); family_pairs=Counter()
    exemplar={}
    fcomplete_min_h=(float('inf'),None,None)
    fcomplete_max_h=(-1,None,None)
    fcomplete_min_queue=(float('inf'),None,None)
    min_queue_by_h={}
    distinct_condition=0; n=0
    condition={r['run_id']:r['condition'] for r in run_meta}
    def family(cond):
        if cond.startswith(('choice-','noul-')): return 'Jev'
        if cond.startswith('gpt-5'): return 'GPT5'
        if cond.startswith('gpt-6'): return 'GPT6'
        raise ValueError(cond)
    for keys in itertools.combinations(run_names,3):
        keep=run_includes[keys[0]] | run_includes[keys[1]] | run_includes[keys[2]]
        h=len(keep & human); f=len(keep & final); w=len(keep)
        n+=1; pairs[(f,h)]+=1;hdist[h]+=1;fdist[f]+=1
        if len({condition[x] for x in keys})==3:
            distinct_condition+=1;distinct_pairs[(f,h)]+=1
        if {family(condition[x]) for x in keys}=={'Jev','GPT5','GPT6'}:
            family_pairs[(f,h)]+=1
        if (f,h) not in exemplar:exemplar[(f,h)]={'runs':list(keys),'forwarded':w}
        if h not in min_queue_by_h or w<min_queue_by_h[h]['forwarded']:
            min_queue_by_h[h]={'runs':list(keys),'forwarded':w,'F_covered':f}
        if f==23:
            if h<fcomplete_min_h[0] or (h==fcomplete_min_h[0] and w<fcomplete_min_h[2]['forwarded'] if fcomplete_min_h[2] else True):
                fcomplete_min_h=(h,keys,{'forwarded':w})
            if h>fcomplete_max_h[0] or (h==fcomplete_max_h[0] and w<fcomplete_max_h[2]['forwarded'] if fcomplete_max_h[2] else True):
                fcomplete_max_h=(h,keys,{'forwarded':w})
            if w<fcomplete_min_queue[0]:
                fcomplete_min_queue=(w,keys,{'H_covered':h})
    assert n==math.comb(59,3)==baseline['triplets_enumerated']
    assert sum(family_pairs.values())==50*6*3==900
    assert sum(distinct_pairs.values())==distinct_condition
    assert {str(k):v for k,v in hdist.items()}==baseline['triplet_H_distribution']
    assert {str(k):v for k,v in fdist.items()}==baseline['triplet_F_distribution']
    assert sum(v for (f,h),v in pairs.items() if f==23)==baseline['triplets_F23']
    assert sum(v for (f,h),v in pairs.items() if h==112)==baseline['triplets_H112']
    assert fcomplete_min_queue[0]==baseline['F_oracle']['forwarded']
    assert fcomplete_max_h[0]==baseline['H_oracle']['H_covered']
    assert min_queue_by_h[112]['forwarded']==baseline['H_oracle']['forwarded']
    out={
        'source_commit':PIN,'source_sha256':SHA,
        'method':'Independently coded set unions / stage-paired exact exhaustive checks',
        'triplets':n,'distinct_condition_triplets':distinct_condition,
        'distinct_condition_F_complete':sum(c for (f,h),c in distinct_pairs.items() if f==23),
        'distinct_condition_H112':sum(c for (f,h),c in distinct_pairs.items() if h==112),
        'distinct_condition_joint_F_H_counts':{f'F{f}_H{h}':c for (f,h),c in sorted(distinct_pairs.items())},
        'family_balanced_triplets':sum(family_pairs.values()),
        'family_balanced_F_complete':sum(c for (f,h),c in family_pairs.items() if f==23),
        'family_balanced_H112':sum(c for (f,h),c in family_pairs.items() if h==112),
        'family_balanced_joint_F_H_counts':{f'F{f}_H{h}':c for (f,h),c in sorted(family_pairs.items())},
        'joint_F_H_counts':{f'F{f}_H{h}':c for (f,h),c in sorted(pairs.items())},
        'H_histogram':{str(k):v for k,v in sorted(hdist.items())},
        'F_histogram':{str(k):v for k,v in sorted(fdist.items())},
        'F_complete_H_min':{'H_covered':fcomplete_min_h[0], 'witness_runs':list(fcomplete_min_h[1]),**fcomplete_min_h[2]},
        'F_complete_H_max':{'H_covered':fcomplete_max_h[0], 'witness_runs':list(fcomplete_max_h[1]),**fcomplete_max_h[2]},
        'F_complete_min_queue':{'forwarded':fcomplete_min_queue[0], 'witness_runs':list(fcomplete_min_queue[1]),**fcomplete_min_queue[2]},
        'min_queue_by_H':{str(k):v for k,v in sorted(min_queue_by_h.items())},
        'f_complete_but_h_below_112':sum(v for (f,h),v in pairs.items() if f==23 and h<112),
        'independent_verifier':'PASS',
        'limits':['No independent human eligibility','Joint counts are conditionally source-specific','Repeated portfolios are not independent samples','No human time or prospective policy inference']}
    Path('r61_independent_endpoint_certificate.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print('R61_ALTERNATE_SET_VERIFIER_PASS '+json.dumps({'triplets':n,'F_complete_H_range':[out['F_complete_H_min']['H_covered'],out['F_complete_H_max']['H_covered']],'F_complete_but_H_below_112':out['f_complete_but_h_below_112'],'F23_family_balanced':out['family_balanced_F_complete'],'H112_family_balanced':out['family_balanced_H112'],'H112_min_queue':min_queue_by_h[112]['forwarded'],'F23_min_queue':fcomplete_min_queue[0]},sort_keys=True))
if __name__=='__main__':main()
