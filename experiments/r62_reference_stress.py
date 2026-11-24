#!/usr/bin/env python3
"""R62 exploratory exact reference-stage robustness, source-pinned Matsui archive.
No third-party record-level inputs or labels are redistributed.
All hypothetical intermediate reference sets are sensitivity cases, not true eligibility.
"""
import itertools, json, math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from r60_minimal_coverage import rows, rawfile, PIN, SHA

def masks_from_source():
    rec=rows('data/records.csv')
    pred=rows('data/predictions.csv.gz')
    meta=json.loads(rawfile('data/runs.json'))
    report=json.loads(rawfile('configuration/included_reports.json'))
    ids={r['record_id']:i for i,r in enumerate(rec)}
    assert len(ids)==len(rec)==4527 and len(pred)==267093 and len(meta)==59
    names=sorted(r['run_id'] for r in meta)
    condition={r['run_id']:r['condition'] for r in meta}
    ind={x:i for i,x in enumerate(names)}
    H=sum(1<<i for i,r in enumerate(rec) if r['reference_retained']=='1')
    F=sum(1<<i for i in {ids[s] for e in report for s in e['record_ids']})
    assert (H.bit_count(),F.bit_count())==(113,23) and not(F&~H)
    X=[0]*59; seen=set()
    for p in pred:
        j=ind[p['run_id']];i=ids[p['record_id']]
        assert (j,i) not in seen
        seen.add((j,i))
        keep=float(p['probability_retained'])>=.5 if p['probability_retained'] else p['decision']=='I'
        if keep:X[j]|=1<<i
    assert len(seen)==59*4527
    return rec,pred,meta,report,ids,names,condition,H,F,X

def family(c):
    if c.startswith(('choice-','noul-')):return 'Jev'
    if c.startswith('gpt-5'):return 'GPT5'
    if c.startswith('gpt-6'):return 'GPT6'
    raise ValueError(c)

def lower(h,f,H=113,F=23):
    assert 0<=f<=F and 0<=h-f<=H-F
    return Fraction(f,H-h+f) if H-h+f else Fraction(0)

def policy(ind,U,H,F,names):
    h=(U&H).bit_count();f=(U&F).bit_count()
    return {'run_ids':[names[i] for i in ind],'queue':U.bit_count(),'H':h,'F':f,
            'lower_all_intermediate_references':str(lower(h,f))}

def summaries(data,H,F,names):
    hist=Counter((r[3],r[2]) for r in data)
    risk={}
    for r in [Fraction(9,10),Fraction(95,100),Fraction(98,100),Fraction(99,100),Fraction(1)]:
        tests={'F':lambda h,f:Fraction(f,23)>=r,
               'H':lambda h,f:Fraction(h,113)>=r,
               'both':lambda h,f:Fraction(f,23)>=r and Fraction(h,113)>=r,
               'all_intermediate':lambda h,f:lower(h,f)>=r}
        row={}
        for k,test in tests.items():
            eligible=[x for x in data if test(x[2],x[3])]
            best=min(eligible,key=lambda x:(x[1],x[0])) if eligible else None
            row[k]={'count':len(eligible),'minimum_queue':best[1] if best else None,
                    'witness':policy(best[0],best[5],H,F,names) if best else None}
        risk[str(r)]=row
    # Predeclared eligibility: both endpoints >=95%, F complete, identical queue.
    qualified=[x for x in data if x[3]==23 and x[2]>=108]
    grouped=defaultdict(lambda:defaultdict(list))
    for x in qualified:
        grouped[x[1]][x[4]].append(x)
    ctr=Counter()
    best_reversal=None; best_tie=None
    for q,groups in sorted(grouped.items()):
        members=sum(len(v) for v in groups.values())
        ctr['matched_queue_pairs']+=math.comb(members,2)
        for (ma,aa),(mb,bb) in itertools.combinations(sorted(groups.items()),2):
            n=len(aa)*len(bb)
            ha=ma.bit_count(); hb=mb.bit_count()
            u=(ma&~mb).bit_count();v=(mb&~ma).bit_count()
            assert u-v==ha-hb
            ctr['different_H_set_pairs']+=n
            if ha==hb:
                ctr['equal_endpoint_count_but_different_H_set_pairs']+=n
                assert u==v>0
                key=(v,-q,aa[0][0],bb[0][0])
                if best_tie is None or key>best_tie[0]:best_tie=(key,aa[0],bb[0],u,v)
            else:
                ctr['strict_H_count_order_pairs']+=n
                if ha<hb:aa,bb,u,v=bb,aa,v,u
                # A has strictly higher H retention but B may retain a positive A misses.
                if v>0:
                    ctr['strict_H_winner_reversed_at_some_intermediate_reference']+=n
                    if Fraction(23,23+v)<Fraction(95,100):
                        ctr['strict_H_winner_fails95_B_perfect_at_some_intermediate_reference']+=n
                    key=(v,u-v,-q,aa[0][0],bb[0][0])
                    if best_reversal is None or key>best_reversal[0]:best_reversal=(key,aa[0],bb[0],u,v)
    def witness(t):
        if t is None:return None
        _,a,b,u,v=t
        assert a[1]==b[1] and a[3]==b[3]==23
        return {'A':policy(a[0],a[5],H,F,names),'B':policy(b[0],b[5],H,F,names),
                'A_only_optional':u,'B_only_optional':v,
                'reference_F_plus_B_only_optional':{'size':23+v,'A_retained':23,'B_retained':23+v,'A_recall':str(Fraction(23,23+v)),'B_recall':'1'},
                'reference_F_plus_A_only_optional':{'size':23+u,'A_retained':23+u,'B_retained':23,'A_recall':'1','B_recall':str(Fraction(23,23+u))}}
    return {'portfolios':len(data),'joint_counts':{f'F{f}_H{h}':n for (f,h),n in sorted(hist.items())},
            'target_diagnostics':risk,'qualified_matched_queue_portfolios':len(qualified),
            'matched_queue_pair_counts':dict(ctr),'strict_winner_reversal_witness':witness(best_reversal),
            'equal_endpoint_tie_witness':witness(best_tie)}

def independent_witness_check(rec,pred,report,ids,result):
    # Alternative record-set representation on original rows, verifying each published witness.
    names={r['run_id'] for r in pred}
    ref={r['record_id'] for r in rec if r['reference_retained']=='1'}
    final={s for e in report for s in e['record_ids']}
    wanted={x for fam in result.values() for typ in ('strict_winner_reversal_witness','equal_endpoint_tie_witness') if fam[typ] for side in ('A','B') for x in fam[typ][side]['run_ids']}
    sets={r:set() for r in wanted}
    for p in pred:
        if p['run_id'] in wanted and (float(p['probability_retained'])>=.5 if p['probability_retained'] else p['decision']=='I'):
            sets[p['run_id']].add(p['record_id'])
    checks=0
    for fam in result.values():
        for typ in ('strict_winner_reversal_witness','equal_endpoint_tie_witness'):
            w=fam[typ]
            if w is None:continue
            A=set.union(*(sets[r] for r in w['A']['run_ids']))
            B=set.union(*(sets[r] for r in w['B']['run_ids']))
            for k,s in [('A',A),('B',B)]:
                assert (len(s),len(s&ref),len(s&final))==(w[k]['queue'],w[k]['H'],w[k]['F'])
            a=(A-B)&(ref-final);b=(B-A)&(ref-final)
            assert (len(a),len(b))==(w['A_only_optional'],w['B_only_optional'])
            assert (len(A&(final|b)),len(B&(final|b)))==(23,23+len(b))
            assert (len(A&(final|a)),len(B&(final|a)))==(23+len(a),23)
            checks+=1
    return checks

def main():
    rec,pred,meta,report,ids,names,cond,H,F,X=masks_from_source()
    families={'all':[],'distinct_configuration':[],'family_balanced':[]}
    for ind in itertools.combinations(range(59),3):
        U=X[ind[0]]|X[ind[1]]|X[ind[2]]
        x=(ind,U.bit_count(),(U&H).bit_count(),(U&F).bit_count(),U&H,U)
        families['all'].append(x)
        cs={cond[names[i]] for i in ind}
        if len(cs)==3:families['distinct_configuration'].append(x)
        if {family(c) for c in cs}=={'Jev','GPT5','GPT6'}:families['family_balanced'].append(x)
    assert [len(x) for x in families.values()]==[32509,20377,900]
    result={k:summaries(v,H,F,names) for k,v in families.items()}
    assert result['all']['target_diagnostics']['19/20']['both']['count']==27215
    assert result['all']['target_diagnostics']['19/20']['all_intermediate']['count']==243
    assert result['family_balanced']['target_diagnostics']['19/20']['both']['count']==774
    assert result['family_balanced']['target_diagnostics']['19/20']['all_intermediate']['count']==117
    checked=independent_witness_check(rec,pred,report,ids,result)
    out={'source_commit':PIN,'source_sha256':SHA,'reference_H':113,'reference_F':23,
         'reference_stress_definition':'All F subset R subset H; a hypothetical stress family, NOT latent true eligibility',
         'source_records':len(rec),'source_decisions':len(pred),'families':result,
         'independently_checked_matched_queue_witnesses':checked,
         'limits':['Same original source decisions and two topics; portfolio/pair counts are dependent combinatorial counts.',
                   'Reference perturbations are constructed stress witnesses, not new screening outcomes.',
                   'Forwarded records are not measured person-minutes.',
                   'All witness and target minima are retrospective and evaluation-label conditioned.']}
    Path('r62_source_reference_stress.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('R62_SOURCE_PASS '+json.dumps({k:{'target95':v['target_diagnostics']['19/20'],'matched':v['matched_queue_pair_counts'],'strict_witness':v['strict_winner_reversal_witness']} for k,v in result.items()},sort_keys=True))
if __name__=='__main__':main()
