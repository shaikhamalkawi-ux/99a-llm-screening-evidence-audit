#!/usr/bin/env python3
"""R64: fixed-forwarding, fixed-target decision and audit-budget analysis.
No new human labels or model calls; hypothetical restorations of 14 documented records.
"""
import itertools,json,math
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from r60_minimal_coverage import rows,rawfile,PIN,SHA
PROV="configuration/reference_label_provenance.json"
SHA[PROV]="fd84e981fd70849f3914055ee0d60679b8b5e32206b7a1c08ca0763fd0bca6da"
D=14; FULL=(1<<D)-1; INF=65535
def load():
    records=rows("data/records.csv");pred=rows("data/predictions.csv.gz")
    runs=json.loads(rawfile("data/runs.json"));report=json.loads(rawfile("configuration/included_reports.json"))
    changes=json.loads(rawfile(PROV))["corrections_and_confirmations"]
    ids={r["record_id"]:i for i,r in enumerate(records)}
    names=sorted(r["run_id"] for r in runs); ridx={r:i for i,r in enumerate(names)}
    config={r["run_id"]:r["condition"] for r in runs}
    H=sum(1<<i for i,r in enumerate(records) if r["reference_retained"]=="1")
    F=sum(1<<i for i in {ids[s] for e in report for s in e["record_ids"]})
    dnames=sorted(c["record_id"] for c in changes if c["origin"].startswith(("published adjudication","current author-confirmed")))
    assert len(records)==4527 and len(pred)==267093 and len(names)==59 and len(dnames)==14
    assert H.bit_count()==113 and F.bit_count()==23 and F&H==F
    assert all(not(H&(1<<ids[x])) for x in dnames)
    M=[0]*59;seen=set()
    for r in pred:
        i=ids[r["record_id"]];j=ridx[r["run_id"]]
        assert (i,j) not in seen;seen.add((i,j))
        keep=float(r["probability_retained"])>=0.5 if r["probability_retained"] else r["decision"]=="I"
        if keep:M[j]|=1<<i
    assert len(seen)==4527*59
    def family(c):
        return "Jev" if c.startswith(("noul-","choice-")) else "GPT5" if c.startswith("gpt-5") else "GPT6"
    cases={"all":[],"family_balanced":[]}
    for comb in itertools.combinations(range(59),3):
        m=M[comb[0]]|M[comb[1]]|M[comb[2]]
        if (m&F)!=F:continue
        h=(m&H).bit_count()
        d=sum(1<<i for i,x in enumerate(dnames) if m&(1<<ids[x]))
        row=(m.bit_count(),h,d,tuple(names[i] for i in comb))
        cases["all"].append(row)
        if {family(config[names[i]]) for i in comb}=={"Jev","GPT5","GPT6"}:cases["family_balanced"].append(row)
    assert len(cases["all"])==32505 and len(cases["family_balanced"])==900
    return cases,dnames

def witness(x):
    q,h,d,rs=x
    return {"Q":q,"H_covered":h,"D_covered":d.bit_count(),"D_mask":d,"runs":list(rs)}

def calc(fam,rows,targetnum,targetden):
    # 3^14 states; trits: 0 unknown, 1 absent, 2 present.
    pc=np.array([i.bit_count() for i in range(1<<D)],dtype=np.uint8)
    states=np.arange(3**D,dtype=np.int32)
    known=np.zeros(len(states),dtype=np.uint16);pos=np.zeros_like(known)
    pow3=np.array([3**i for i in range(D)],dtype=np.int32)
    for i,p in enumerate(pow3):
        trit=(states//p)%3
        known|=np.where(trit!=0,1<<i,0).astype(np.uint16)
        pos|=np.where(trit==2,1<<i,0).astype(np.uint16)
    # In a given cube, worst completion adds all unread misses and none of unread hits.
    # Recall pass equivalent to targetden*(h+known covered)>=targetnum*(113+known positives+unknown misses).
    # Pareto-safe compression: identical h,d -> lowest q; discard if an earlier cheaper
    # signature covers superset D and >=h. All signatures remain available to independent check.
    best={}
    for x in sorted(rows):
        key=x[1:3]
        best.setdefault(key,x)
    cand=[]
    for x in sorted(best.values()):
        q,h,d,rs=x
        if h+(D*d.bit_count())<0:raise AssertionError()
        if any(y[1]>=h and (y[2]|d)==y[2] for y in cand):continue
        cand.append(x)
    g=np.full(len(states),INF,dtype=np.uint16)
    remaining=states
    winners={}
    # g(s)=min queue of one common policy valid for every completion of s.
    for x in cand:
        q,h,d,rs=x
        k=known[remaining];p=pos[remaining]
        missed_unknown=pc[(FULL^k)&(FULL^d)].astype(np.int16)
        num=h+pc[p&d].astype(np.int16)
        den=113+pc[p].astype(np.int16)+missed_unknown
        ok=(targetden*num>=targetnum*den)
        if np.any(ok):
            g[remaining[ok]]=q;winners.setdefault(q,0);winners[q]+=int(ok.sum())
            remaining=remaining[~ok]
        if not len(remaining):break
    # Direct full completion check across the complete portfolio family (not compressed).
    completed=np.arange(1<<D,dtype=np.uint16)
    truth_idx=np.zeros(len(completed),dtype=np.int32)
    for i,p in enumerate(pow3):truth_idx+=p*(1+((completed>>i)&1).astype(np.int32))
    oracle=np.full(len(completed),INF,dtype=np.uint16)
    # Independently form all possible full references from original records' count.
    # Unique signatures suffice, including every dominated signature, no dominance pruning.
    for q,h,d,rs in sorted(best.values()):
        hit=pc[completed&d].astype(np.int16)
        den=113+pc[completed].astype(np.int16)
        accept=targetden*(h+hit)>=targetnum*den
        oracle[accept]=np.minimum(oracle[accept],q)
    assert np.array_equal(oracle,g[truth_idx])
    levels=[states[pc[known]==i] for i in range(D+1)]
    # min/max cost with full reference available, conditioned on each partial state.
    lo=np.full_like(g,INF);hi=np.zeros_like(g);lo[truth_idx]=oracle;hi[truth_idx]=oracle
    for l in range(D-1,-1,-1):
        level=levels[l]
        # use the first unknown coordinate; completion extrema are independent of choice.
        rest=level
        for p in pow3:
            sel=rest[(rest//p)%3==0]
            if len(sel):
                lo[sel]=np.minimum(lo[sel+p],lo[sel+2*p]);hi[sel]=np.maximum(hi[sel+p],hi[sel+2*p])
            rest=rest[(rest//p)%3!=0]
        assert not len(rest)
    assert np.all(lo<=hi) and np.all(hi<=g)
    # Exhaustive independent robust queue checks: root, full states, all 1-label states,
    # deterministic sample of 2,048 partial states. For each test compare all original signatures.
    rng=np.random.default_rng(640113)
    tests=np.unique(np.concatenate((np.array([0],dtype=np.int32),truth_idx,levels[1],rng.choice(states,2048,replace=False))))
    k=known[tests];p=pos[tests];chk=np.full(len(tests),INF,dtype=np.uint16)
    for q,h,d,rs in best.values():
        # Use sharp worst reference missed count; equivalent but different formula.
        missed=113-h+pc[(p|(FULL^k))&(FULL^d)].astype(np.int16)
        denom=113+pc[p&d].astype(np.int16)+pc[(p|(FULL^k))&(FULL^d)].astype(np.int16)
        accept=targetden*(denom-missed)>=targetnum*denom
        chk[accept]=np.minimum(chk[accept],q)
    # The separate formula must also include known positives missed (already in denom).
    assert np.array_equal(chk,g[tests]),(fam,targetnum,targetden,np.sum(chk!=g[tests]))
    # Preselected nonadaptive audits: query the same labels on every completion, then
    # pick a policy certified to satisfy the threshold with the remaining labels unknown.
    worst=np.zeros(1<<D,dtype=np.uint16)
    np.maximum.at(worst,known,g)
    nonadaptive=[]
    for b in range(D+1):
        ks=np.flatnonzero(pc==b);v=int(worst[ks].min())
        opts=ks[worst[ks]==v]
        nonadaptive.append({"labels":b,"worst_queue":None if v==INF else v,"optimal_subsets":len(opts),"first_mask":int(opts[0])})
    assert int(worst[0])==int(g[0]) and int(worst[FULL])==int(hi[0])
    # Minimax acquisition (allow certifiable infeasibility, not forced choice).
    # For each cap, a state can stop with guaranteed success if g<=cap, or
    # guaranteed impossibility if lo>cap. A query uses one label and both branches
    # must be solved, hence exact recurrence 1+min max. Unit number of resolutions.
    caps=sorted({350,400,424,450,473,475,492,500,607,int(lo[0]),int(hi[0]),int(g[0])}-{INF})
    depth_results=[]
    for cap in caps:
        leaf=(g<=cap)|(lo>cap)
        depth=np.where(leaf,0,31).astype(np.uint8)
        first=np.full(len(states),255,dtype=np.uint8)
        for l in range(D-1,-1,-1):
            lev=levels[l];lev=lev[~leaf[lev]]
            if not len(lev):continue
            for i,p3 in enumerate(pow3):
                ix=lev[(lev//p3)%3==0]
                cost=1+np.maximum(depth[ix+p3],depth[ix+2*p3])
                better=cost<depth[ix]
                depth[ix[better]]=cost[better];first[ix[better]]=i
        assert depth[0]<=D
        # Replay optimal minimax tree on EVERY complete reference. This verifies
        # all terminal certificates and root worst depth, not just oracle endpoint.
        st=np.zeros(1<<D,dtype=np.int32);count=np.zeros(1<<D,dtype=np.uint8)
        for step in range(D):
            active=~leaf[st]
            if not active.any():break
            i=first[st[active]].astype(np.int32)
            assert np.all(i<D)
            bit=((completed[active]>>i)&1).astype(np.int32)
            st[active]+=pow3[i]*(1+bit);count[active]+=1
        assert leaf[st].all() and int(count.max())==int(depth[0])
        succeeds=g[st]<=cap; infeasible=lo[st]>cap
        assert np.all(succeeds^(infeasible))
        assert np.array_equal(succeeds,oracle<=cap)
        # fixed upfront subset needed to certify success or impossibility under all completions.
        failure=np.zeros(1<<D,dtype=np.uint8)
        np.maximum.at(failure,known,(~leaf).astype(np.uint8))
        masks=np.flatnonzero(failure==0)
        qmin=int(pc[masks].min())
        assert int(depth[0])<=qmin
        # Distribution over logical completions only, not probabilities of human judgment.
        depth_results.append({"cap":cap,"full_states_feasible":int((oracle<=cap).sum()),
           "worst_adaptive_queries":int(depth[0]),"min_fixed_upfront_queries":qmin,
           "endpoint_adaptive_queries":{"adjusted":int(count[0]),"all_restored":int(count[-1])},
           "logical_completion_query_histogram":{str(k):v for k,v in sorted(Counter(count.tolist()).items())},
           "first_query_index":None if first[0]==255 else int(first[0])})
    def val(v):return None if v==INF else int(v)
    # Verify baseline exact values for the main family at 95%.
    if fam=="all" and targetnum==19 and targetden==20:
        assert int(g[0])==492 and int(oracle[0])==350 and int(oracle[-1])==424
    return {"family":fam,"target":f"{targetnum}/{targetden}","F_complete_triples":len(rows),
        "unique_signatures":len(best),"undominated_in_cost_order":len(cand),
        "fixed_robust_queue":val(g[0]),"full_label_oracle_worst_queue":val(hi[0]),"full_label_oracle_best_queue":val(lo[0]),
        "oracle_adjusted_queue":val(oracle[0]),"oracle_full_restored_queue":val(oracle[-1]),
        "full_completions":len(oracle),"partial_states":len(states),
        "oracle_queue_histogram":{str(k):v for k,v in sorted(Counter(oracle.tolist()).items())},
        "direct_full_state_parity":len(oracle),"independent_partial_state_checks":len(tests),
        "nonadaptive_worst_queue_frontier":nonadaptive,"cap_certification":depth_results}

def main():
    cases,dnames=load()
    result={"source_commit":PIN,"source_hashes":SHA,"uncertain_label_count":D,"reference_H":113,"reference_F":23,
      "scope":"Historical label-restoration stress only. Shared pool of 14 documented disputed labels, each optionally restored. No new judgments. All candidate choices retrospective; unknown labels outside D fixed by design, not assumed true.",
      "target":"Recall against H plus restored subset; additionally F complete for every candidate.",
      "results":{}}
    for family,rows in cases.items():
        for t in [(19,20),(49,50)]:
            result["results"][family+"_"+str(t[0])]=calc(family,rows,*t)
            print(family,t, json.dumps({k:v for k,v in result["results"][family+"_"+str(t[0])].items() if k!="oracle_queue_histogram"},sort_keys=True),flush=True)
    Path("r64_budget_certificate.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("R64_PASS",flush=True)
if __name__=="__main__":main()
