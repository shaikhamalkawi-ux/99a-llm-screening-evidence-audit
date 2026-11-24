#!/usr/bin/env python3
"""99a R61 exploratory source-label and unlabeled selection diagnostics.
Read only the upstream source-pinned 59x4527 decisions. Not a deployed policy.
Never release third-party per-record model outputs from this research workflow.
"""
import itertools, json, math
from collections import Counter
from pathlib import Path
from r60_minimal_coverage import rows, rawfile, PIN, SHA

def bitids(m):
    while m:
        bit = m & -m
        yield bit.bit_length()-1
        m -= bit

def main():
    rec = rows('data/records.csv')
    preds = rows('data/predictions.csv.gz')
    runs = json.loads(rawfile('data/runs.json'))
    reports = json.loads(rawfile('configuration/included_reports.json'))
    assert len(rec)==4527 and len(preds)==267093 and len(runs)==59
    ids={r['record_id']:i for i,r in enumerate(rec)}
    names=sorted(r['run_id'] for r in runs)
    ridx={n:i for i,n in enumerate(names)}
    cond={r['run_id']:r['condition'] for r in runs}
    masks=[0]*59
    seen=Counter()
    for row in preds:
        j=ridx[row['run_id']]
        i=ids[row['record_id']]
        incl=(float(row['probability_retained'])>=.5) if row['probability_retained'] else row['decision']=='I'
        if incl:masks[j] |= 1<<i
        seen[j]+=1
    assert len(seen)==59 and all(v==4527 for v in seen.values())
    def bits(ii):
        m=0
        for i in ii:m|=1<<i
        return m
    H=bits(i for i,r in enumerate(rec) if r['reference_retained']=='1')
    F=bits(ids[rid] for e in reports for rid in e['record_ids'])
    assert (H.bit_count(),F.bit_count())==(113,23) and not(F&~H)
    total=0
    for m in masks:total|=m
    assert (total.bit_count(),(total&H).bit_count(),(total&F).bit_count())==(1002,112,23)
    freq=[0]*4527
    for m in masks:
        for i in bitids(m):freq[i]+=1
    def profile(ref):
        c=Counter()
        for i in bitids(ref):
            v=freq[i]
            c['0' if v==0 else '1' if v==1 else '2-3' if v<=3 else '4-9' if v<=9 else '10-19' if v<=19 else '20-39' if v<=39 else '40-58' if v<=58 else '59']+=1
        return dict(sorted(c.items()))
    def witness(ind,m):
        return {'run_ids':[names[i] for i in ind], 'conditions':[cond[names[i]] for i in ind], 'forwarded':m.bit_count(), 'H_covered':(m&H).bit_count(), 'F_covered':(m&F).bit_count()}
    histogram_H=Counter();histogram_F=Counter()
    n112=n112w=nF23=0
    bestH=(-1,10**9,(),0)
    bestF=(-1,10**9,(),0)
    diverse=(-1,10**9,(),0)
    minW=(10**9,(),0)
    maxW=(-1,(),0)
    for ind in itertools.combinations(range(59),3):
        m=masks[ind[0]]|masks[ind[1]]|masks[ind[2]]
        h=(m&H).bit_count();f=(m&F).bit_count();w=m.bit_count()
        histogram_H[h]+=1;histogram_F[f]+=1
        if h>bestH[0] or (h==bestH[0] and w<bestH[1]):bestH=(h,w,ind,m)
        if f>bestF[0] or (f==bestF[0] and w<bestF[1]):bestF=(f,w,ind,m)
        if w<minW[0]:minW=(w,ind,m)
        if w>maxW[0]:maxW=(w,ind,m)
        if len({cond[names[i]] for i in ind})==3 and (h>diverse[0] or (h==diverse[0] and w<diverse[1])):diverse=(h,w,ind,m)
        if h==112:
            n112+=1
            if w<=483:n112w+=1
        if f==23:nF23+=1
    assert sum(histogram_H.values())==math.comb(59,3)
    assert bestH[:2]==(112,483)
    def greed(rare=False):
        chosen=[];used=0
        for _ in range(3):
            candidates=[]
            for i,m in enumerate(masks):
                if i in chosen:continue
                fresh=m&~used
                score=sum(1/freq[j] for j in bitids(fresh)) if rare else fresh.bit_count()
                candidates.append((-score,(used|m).bit_count(),names[i],i))
            i=min(candidates)[3]
            chosen.append(i);used|=masks[i]
        return witness(chosen,used)
    def expect(ref):
        return sum(1-math.comb(59-freq[i],3)/math.comb(59,3) for i in bitids(ref))
    eh=sum(k*v for k,v in histogram_H.items())/math.comb(59,3)
    ef=sum(k*v for k,v in histogram_F.items())/math.comb(59,3)
    assert abs(eh-expect(H))<1e-9 and abs(ef-expect(F))<1e-9
    result={'project':'99a','candidate':'R61','source_commit':PIN,'source_sha256':SHA,
      'records':4527,'predictions':267093,'runs':59,
      'reference_H':'source human retained for full text, NOT true eligibility',
      'reference_F':'source final-report-linked IDs, NOT an exhaustive eligibility standard',
      'H_vote_support_histogram':profile(H),'F_vote_support_histogram':profile(F),
      'triplets_enumerated':math.comb(59,3),
      'triplet_H_distribution':dict(sorted(histogram_H.items())),
      'triplet_F_distribution':dict(sorted(histogram_F.items())),
      'triplets_H112':n112,'triplets_H112_and_forwarded_at_most_483':n112w,
      'triplets_F23':nF23,'fraction_H112':n112/math.comb(59,3),
      'mean_H_uniform_triple':eh,'mean_F_uniform_triple':ef,
      'analytical_H_expected_from_vote_support':expect(H),
      'analytical_F_expected_from_vote_support':expect(F),
      'H_oracle':witness(bestH[2],bestH[3]),
      'F_oracle':witness(bestF[2],bestF[3]),
      'condition_distinct_H_oracle':witness(diverse[2],diverse[3]),
      'minimum_forwarded_three_runs_unlabeled':witness(minW[1],minW[2]),
      'maximum_forwarded_three_runs_unlabeled':witness(maxW[1],maxW[2]),
      'greedy_maximum_unlabeled_coverage':greed(),
      'greedy_inverse_frequency_coverage':greed(True),
      'limits':['Retrospective fixed-source, not new model decisions or prospective human study',
        'Triplets share the same underlying archive; enumerated fractions are combinatorial proportions, not independent trial probabilities',
        'H and F are stage-specific source sets; neither covers all true eligible papers',
        'Label-blind policies still observe all 59 model outputs; no real budget advantage is inferred',
        'No reviewer time savings, unbiased true recall, safety guarantee or generalization claim']}
    Path('r61_reference_blindness.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('R61_SOURCE_PINNED_PASS '+json.dumps({'triplets':result['triplets_enumerated'],
     'H112_count':n112,'H112_with_queue_483_count':n112w,'F23_count':nF23,
     'H_oracle':result['H_oracle'],'F_oracle':result['F_oracle'],
     'data_only_greedy':result['greedy_maximum_unlabeled_coverage']},sort_keys=True))
if __name__=='__main__':main()
