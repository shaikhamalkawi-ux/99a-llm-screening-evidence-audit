#!/usr/bin/env python3
"""R67: same-shortlist direct-forward comparator, compared with passive label observation.
Uses the five pinned Matsui source inputs. No original text, predictions, or new adjudications.
"""
import itertools,json,math
from pathlib import Path
from collections import defaultdict
from r60_minimal_coverage import rows,rawfile,PIN,SHA
PROV="configuration/reference_label_provenance.json"
SHA[PROV]="fd84e981fd70849f3914055ee0d60679b8b5e32206b7a1c08ca0763fd0bca6da"
def main():
    rec=rows("data/records.csv");pred=rows("data/predictions.csv.gz")
    meta=json.loads(rawfile("data/runs.json"));reports=json.loads(rawfile("configuration/included_reports.json"))
    prov=json.loads(rawfile(PROV))
    ids={r["record_id"]:i for i,r in enumerate(rec)}
    names=sorted(r["run_id"] for r in meta);idx={n:i for i,n in enumerate(names)}
    cond={r["run_id"]:r["condition"] for r in meta}
    topics=sorted({r["dataset"] for r in rec})
    H=sum(1<<i for i,r in enumerate(rec) if r["reference_retained"]=="1")
    F=sum(1<<i for i in {ids[s] for e in reports for s in e["record_ids"]})
    ds=sorted(c["record_id"] for c in prov["corrections_and_confirmations"] if c["origin"].startswith(("published adjudication","current author-confirmed")))
    D=sum(1<<ids[x] for x in ds)
    T=[sum(1<<i for i,r in enumerate(rec) if r["dataset"]==t) for t in topics]
    assert len(rec)==4527 and len(pred)==267093 and len(names)==59 and (H.bit_count(),F.bit_count(),D.bit_count())==(113,23,14)
    assert not(D&H) and F&H==F
    M=[0]*59; seen=set(); sets={n:set() for n in names}
    for row in pred:
        i=ids[row["record_id"]];j=idx[row["run_id"]]
        assert (i,j) not in seen;seen.add((i,j))
        take=(float(row["probability_retained"])>=.5) if row["probability_retained"] else row["decision"]=="I"
        if take:
            M[j]|=1<<i;sets[row["run_id"]].add(row["record_id"])
    assert len(seen)==267093
    def fam(c):
        return "Jev" if c.startswith(("choice-","noul-")) else "GPT5" if c.startswith("gpt-5") else "GPT6"
    cand=defaultdict(list); base=tuple((H&t).bit_count() for t in T)
    for r in itertools.combinations(range(59),3):
        A=M[r[0]]|M[r[1]]|M[r[2]]
        if A&F!=F:continue
        key=tuple(names[i] for i in r)
        h=tuple((A&H&t).bit_count() for t in T)
        m=tuple((D&~A&t).bit_count() for t in T)
        x=(A.bit_count(),h,m,key)
        cand["all"].append(x)
        if {fam(cond[n]) for n in key}=={"Jev","GPT5","GPT6"}:cand["family_balanced"].append(x)
    assert len(cand["all"])==32505 and len(cand["family_balanced"])==900
    def need(h,B,m,num,den):
        if den*h<num*B:return None
        return max(0,m-(den*h-num*B)//num)
    def brute_need(h,B,m,num,den):
        return next((x for x in range(m+1) if den*h>=num*(B+m-x)),None)
    def score(x,num,den,rw):
        q,h,m,rs=x
        if rw:
            v=[need(a,b,c,num,den) for a,b,c in zip(h,base,m)]
            w=[brute_need(a,b,c,num,den) for a,b,c in zip(h,base,m)]
            assert v==w
            if None in v:return None
            n=sum(v)
        else:
            n=need(sum(h),sum(base),sum(m),num,den)
            assert n==brute_need(sum(h),sum(base),sum(m),num,den)
            if n is None:return None
        return q+n,n,q,rs
    results={};candidate_checks=0;replay_checks=0
    HH={r["record_id"] for r in rec if r["reference_retained"]=="1"}
    FF={s for e in reports for s in e["record_ids"]}
    tt=[{r["record_id"] for r in rec if r["dataset"]==t} for t in topics]
    DD=set(ds)
    for family,ps in cand.items():
        # Independently reconstruct every source portfolio as a union of Python sets.
        # Verify both original queue and every sufficient count signature.
        for q,h,m,key in ps:
            A=set.union(*(sets[n] for n in key))
            assert len(A)==q and FF<=A
            assert h==tuple(len(A&HH&g) for g in tt)
            assert m==tuple(len((DD-A)&g) for g in tt)
            candidate_checks+=1
        for num,den in ((19,20),(49,50)):
            for rw in (False,True):
                key=f"{family}_{num}_{'reviewwise' if rw else 'pooled'}"
                options=[v for x in ps if (v:=score(x,num,den,rw)) is not None]
                out=[]
                for b in range(15):
                    valid=[v for v in options if v[1]<=b]
                    if not valid:out.append(None);continue
                    touch,n,q,rs=min(valid)
                    A=set.union(*(sets[s] for s in rs))
                    if rw:
                        S=set()
                        for g in tt:
                            miss=sorted((DD-A)&g)
                            z=need(len(A&HH&g),len(HH&g),len(miss),num,den)
                            S.update(miss[:z])
                    else:S=set(sorted(DD-A)[:n])
                    assert len(S)==n and len(A|S)==touch and FF<=A
                    # Independent witness: enumerate the entire 2^14 reference cube.
                    C=A|S;checks=0
                    for mask in range(1<<14):
                        R=HH|{d for i,d in enumerate(ds) if mask&(1<<i)}
                        def ok(r):return den*len(C&r)>=num*len(r)
                        assert all(ok(R&g) for g in tt) if rw else ok(R)
                        checks+=1
                    replay_checks+=checks
                    out.append({"touch":touch,"extra":n,"base_queue":q,"runs":rs,"supplement_ids":sorted(S),"all_reference_checks":checks})
                results[key]=out
    # Locked fixed policy baselines from R64, None means infeasible.
    assert [results[k][0]["touch"] if results[k][0] else None for k in ["all_19_pooled","all_19_reviewwise","all_49_pooled","family_balanced_19_pooled","family_balanced_49_pooled"]]==[492,492,607,547,None]
    data={"source_pin":PIN,"source_hashes":SHA,"records":4527,"runs":59,"optional":14,"F":23,
          "policy_set_checks":candidate_checks,"reference_witness_checks":replay_checks,
          "results":results,"scope":"Direct-forward supplements chosen only from same 14 documented restoration IDs; all query outcomes hypothetical. Finite conditional hindsight comparison, no prospective workload."}
    Path("r67_matsui_rescue.json").write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print("R67_PASS",json.dumps({"policy_set_checks":candidate_checks,"reference_witness_checks":replay_checks,
           "frontiers":{k:[None if x is None else x["touch"] for x in v] for k,v in results.items()}},sort_keys=True))
if __name__=="__main__":main()
