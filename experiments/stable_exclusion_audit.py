#!/usr/bin/env python3
"""Retrospective fixed-source, finite-population agreement-error persistence audit.

Uses author-released labels and 59 saved outputs from Matsui & Takaesu 2026.
Recomputes outputs from source-pinned hashes, never model-infers or redistributes the input.
This is a novel source-specific analysis, not a new theory of consensus correctness.
"""
from __future__ import annotations
import csv, gzip, hashlib, io, itertools, json, math, urllib.request
from collections import defaultdict, Counter
from pathlib import Path

PIN='d911eafc5299aa3ca41a6aacf0167931c81fcbbc'
ROOT=f'https://raw.githubusercontent.com/matsuikentaro1/jev-title-abstract-screening/{PIN}/'
EXPECTED={
 'data/records.csv':'4287fa288b91e1e4d8b7d990f8df9bc4b3d954de86cfcf03623dc4d89b281dcb',
 'data/predictions.csv.gz':'3ac88823815ed659bac2fb803a2b89334561b2ffd1fb80620e4f32f59fa5444c',
 'data/runs.json':'1d8c2fc79610a0e8532dfb7df36044c6d7f7c2be769172fb2d1b8049720c8cc3',
 'configuration/included_reports.json':'ed54c5f146c739872609334b96ca93d6b935186ed744ebc29b08efcde84f8db4',
}

def read_binary(rel):
    req=urllib.request.Request(ROOT+rel,headers={'User-Agent':'99a-20261124-scoped-originality-audit'})
    with urllib.request.urlopen(req,timeout=90) as res: raw=res.read()
    assert hashlib.sha256(raw).hexdigest()==EXPECTED[rel],('source SHA mismatch',rel)
    return gzip.decompress(raw) if rel.endswith('.gz') else raw

def csvrows(rel):
    return list(csv.DictReader(io.StringIO(read_binary(rel).decode('utf-8'))))

def sha_set(ids):
    return hashlib.sha256(('\n'.join(sorted(ids))+'\n').encode()).hexdigest()

def exact_audit_size(N,B,conf_num=95,conf_den=100):
    """Minimum SRSWOR audits required to observe >=1 among B source-positive misses.

    This is a descriptive finite-population probability if the true count B were known;
    it does not estimate the true number of eligible studies.
    """
    if B==0:return None
    lo,hi=-1,N
    while hi-lo>1:
        mid=(hi+lo)//2
        none=math.comb(N-B,mid) if mid<=N-B else 0
        all_choices=math.comb(N,mid)
        if none*conf_den <= all_choices*(conf_den-conf_num):hi=mid
        else:lo=mid
    assert hi>=1 and hi<=N
    return hi

def analysis():
    records=csvrows('data/records.csv')
    predictions=csvrows('data/predictions.csv.gz')
    runs=json.loads(read_binary('data/runs.json'))
    included=json.loads(read_binary('configuration/included_reports.json'))
    assert len(records)==4527 and len(predictions)==267093 and len(runs)==59
    H={r['record_id'] for r in records if r['reference_retained']=='1'}
    F=set().union(*(set(r['record_ids']) for r in included))
    cohort={d:{r['record_id'] for r in records if r['dataset']==d} for d in ('takeshima','maruki')}
    assert len(H)==113 and len(F)==23 and F<=H
    assert [(len(cohort[d]),len(H&cohort[d])) for d in cohort]==[(1381,26),(3146,87)]
    by_group=defaultdict(list)
    for r in runs:by_group[r['condition']].append((int(r['rep']),r['run_id']))
    assert len(by_group)==8
    for k in by_group:by_group[k].sort()
    include=defaultdict(set)
    count=Counter()
    for p in predictions:
        r,i=p['run_id'],p['record_id']
        v= float(p['probability_retained'])>=0.5 if p['probability_retained'] else p['decision']=='I'
        if v:include[r].add(i)
        count[(r,i)]+=1
    assert len(count)==267093 and all(x==1 for x in count.values())
    all_records=set().union(*cohort.values())
    assert all(len([i for i in all_records if (r['run_id'],i) in count])==4527 for r in runs)
    families={
       'JevChoice_plus_GPT5default_plus_GPT6':('choice-v4','gpt-5-mini-default','gpt-6-astra-default'),
       'Three_LLM_configs_minimal_default_GPT6':('gpt-5-mini-minimal','gpt-5-mini-default','gpt-6-astra-default'),
    }
    results=[]
    for name,types in families.items():
        choices=[[rid for _,rid in by_group[k]] for k in types]
        combos=list(itertools.product(*choices))
        expected_n=90 if name.startswith('Jev') else 27
        assert len(combos)==expected_n
        for d,U in cohort.items():
            h=H&U;f=F&U
            miss=[]; disagreement=[];autoneg=[];missF=[]
            for triad in combos:
                inc=[include[r]&U for r in triad]
                any_in=set.union(*inc)
                all_in=set.intersection(*inc)
                any_ex=U-any_in
                miss.append(h&any_ex)
                disagreement.append(len(any_in-all_in))
                autoneg.append(len(any_ex))
                missF.append(len(f&any_ex))
            permanent=set.intersection(*miss)
            ever=set.union(*miss)
            # A second, non-enumeration formula must equal the intersection:
            # every mixed triple omits i iff every run of every constituent family omits i.
            all_runs=[rid for group in choices for rid in group]
            permanent_from_all=h-set.union(*(include[r]&U for r in all_runs))
            assert permanent==permanent_from_all
            assert len(h)==(26 if d=='takeshima' else 87)
            assert all(k==0 for k in missF)  # GPT-6 covers each source-final report ID
            if name.startswith('Jev'):
                assert (min(map(len,miss)),max(map(len,miss)))==((1,1) if d=='takeshima' else (5,7))
                assert (min(disagreement),max(disagreement))==((26,30) if d=='takeshima' else (260,273))
            misses_by_positive={v:sum(v in m for m in miss) for v in h}
            freq=Counter(misses_by_positive.values())
            firstB=len(miss[0]);firstN=autoneg[0]
            row={
                'family':name,'cohort':d,'n_records':len(U),'human_retained_reference_positives':len(h),
                'final_report_ID_count':len(f),'final_within_human_reference':len(f)==len(F&U),
                'model_configuration_members':list(types),'number_of_reused_run_combinations':len(combos),
                'human_reference_blindspot_min':min(map(len,miss)),
                'human_reference_blindspot_max':max(map(len,miss)),
                'all_combinations_have_blindspot':all(bool(m) for m in miss),
                'same_ids_blind_in_every_combination_count':len(permanent),
                'same_ids_blind_in_every_combination_sha256':sha_set(permanent),
                'distinct_human_retained_ids_blind_in_at_least_one_combination':len(ever),
                'distinct_blind_ids_not_common_to_every_combination':len(ever-permanent),
                'miss_frequency_distribution_over_combinations':{str(i):freq[i] for i in sorted(freq)},
                'hypothetical_disagreement_referral_min':min(disagreement),
                'hypothetical_disagreement_referral_max':max(disagreement),
                'final_report_id_blindspot_max':max(missF),
                'sample_first_combination':{
                    'blind_human_retained':firstB,'unanimously_excluded_total':firstN,
                    'hypothetical_disagreement_review_queue':disagreement[0],
                    'exact_audit_size_for_95pct_chance_detect_at_least_one_source_positive':exact_audit_size(firstN,firstB),
                    'audit_detection_probability_at_10pct_excluded_sample':1-(math.comb(firstN-firstB,math.ceil(.1*firstN))/math.comb(firstN,math.ceil(.1*firstN)) if math.ceil(.1*firstN)<=firstN-firstB else 0),
                    'audit_is_a_hypothetical_uniform_sample_not_executed':True,
                },
            }
            results.append(row)
            print('PERSISTENCE_ROW '+json.dumps({k:row[k] for k in ('family','cohort','number_of_reused_run_combinations','human_reference_blindspot_min','human_reference_blindspot_max','same_ids_blind_in_every_combination_count','distinct_human_retained_ids_blind_in_at_least_one_combination','hypothetical_disagreement_referral_min','hypothetical_disagreement_referral_max','sample_first_combination')},sort_keys=True))
    outcome={'upstream_commit':PIN,'upstream_doi':'10.3390/info17111160',
       'source_sha256':EXPECTED,'sampled_records':len(records),'saved_predictions':len(predictions),
       'source_human_retained':len(H),'source_final_included_record_ids':len(F),
       'model_runs':len(runs),'observations_are_not_independent_across_combinations':True,
       'reference_label_is_human_retained_for_full_text_not_true_final_eligibility':True,
       'sample_detection_is_conditional_on_known_inherited_label_and_perfect_detection':True,
       'prior_art_not_a_new_theorem':['Hilkenmeier et al 2026 full agreement screening','Chang and Zhang 2026 arXiv:2611.12705 shared error/non-identification and negative auditing'],
       'rows':results}
    Path('source_conditional_persistence_results.json').write_text(json.dumps(outcome,indent=2,sort_keys=True)+'\n')
    print('PERSISTENCE_PASS '+json.dumps({'rows':len(results),'records':len(records),'predictions':len(predictions),'source_sha256_verified':True}))

if __name__=='__main__':analysis()
