#!/usr/bin/env python3
"""R64 alternate set-based verification of queue floors, four-label audit and reviewwise gate.
No raw source files, human answers or bibliographic records redistributed.
"""
import itertools, json, math
from collections import defaultdict,Counter
from functools import lru_cache
from pathlib import Path
from r60_minimal_coverage import rows,rawfile,PIN,SHA
PROV="configuration/reference_label_provenance.json"
SHA[PROV]="fd84e981fd70849f3914055ee0d60679b8b5e32206b7a1c08ca0763fd0bca6da"
def main():
    prior=json.loads(Path("r64_budget_certificate.json").read_text())["results"]
    rec=rows("data/records.csv"); pred=rows("data/predictions.csv.gz")
    meta=json.loads(rawfile("data/runs.json")); reports=json.loads(rawfile("configuration/included_reports.json"))
    changes=json.loads(rawfile(PROV))["corrections_and_confirmations"]
    h={r["record_id"] for r in rec if r["reference_retained"]=="1"}
    f={i for r in reports for i in r["record_ids"]}
    dnames=sorted(c["record_id"] for c in changes if c["origin"].startswith(("published adjudication","current author-confirmed")))
    dset=set(dnames); n=len(dnames); full=(1<<n)-1
    assert len(h)==113 and len(f)==23 and f<=h and n==14 and not(h&dset)
    topics=sorted({r["dataset"] for r in rec})
    assert len(topics)==2
    bytopic={t:{r["record_id"] for r in rec if r["dataset"]==t} for t in topics}
    ht={t:h&ss for t,ss in bytopic.items()}
    dt={t:dset&ss for t,ss in bytopic.items()}
    def encode(s):return sum(1<<i for i,k in enumerate(dnames) if k in s)
    topicmask=[encode(dt[t]) for t in topics]
    names=sorted(x["run_id"] for x in meta)
    cond={x["run_id"]:x["condition"] for x in meta}; keep={k:set() for k in names}; cnt=Counter()
    for row in pred:
        k=row["run_id"];cnt[k]+=1
        take=(float(row["probability_retained"])>=.5) if row["probability_retained"] else row["decision"]=="I"
        if take:keep[k].add(row["record_id"])
    assert len(rec)==4527 and len(pred)==267093 and len(names)==59 and all(cnt[k]==4527 for k in names)
    def fam(c):return "Jev" if c.startswith(("choice-","noul-")) else "GPT5" if c.startswith("gpt-5") else "GPT6"
    # Alternate representation: actual source record sets, then compact sufficient
    # signatures with exact per-topic counts. Deduplicate by queue minimization only.
    families=defaultdict(dict)
    for rs in itertools.combinations(names,3):
        s=keep[rs[0]]|keep[rs[1]]|keep[rs[2]]
        if not f<=s:continue
        hs=tuple(len(s&ht[t]) for t in topics); d=encode(s&dset); q=len(s)
        sig=(hs,d)
        for family in ["all"]+(["family_balanced"] if {fam(cond[k]) for k in rs}=={"Jev","GPT5","GPT6"} else []):
            if sig not in families[family] or (q,rs)<(families[family][sig][0],families[family][sig][3]):
                families[family][sig]=(q,hs,d,rs)
    def passing(x,pos,known,num,den,reviewwise):
        # Construct explicit worst completion for this candidate: observed
        # positives + every unobserved optional record NOT retained.
        q,hs,d,rs=x
        z=pos|((full^known)&(full^d))
        if not reviewwise:
            return den*(sum(hs)+(z&d).bit_count())>=num*(len(h)+z.bit_count())
        return all(den*(hh+(z&d&m).bit_count())>=num*(len(ht[t])+(z&m).bit_count())
            for t,hh,m in zip(topics,hs,topicmask))
    def policy(x):
        return {"queue":x[0],"H_by_topic":dict(zip(topics,x[1])),"D_mask":x[2],"run_ids":x[3]}
    result={"source_pin":PIN,"source_hashes":SHA,"topic_H":{t:len(ht[t]) for t in topics},
        "topic_D":{t:len(dt[t]) for t in topics},"results":{}}
    checks=0
    for family,best in sorted(families.items()):
        candidates=sorted(best.values())
        for num,den in [(19,20),(49,50)]:
            for reviewwise in [False,True]:
                known=full
                # Iterate ordered candidates until first feasible; independent
                # of NumPy state lattice and dominance pruning.
                root=next((x for x in candidates if passing(x,0,0,num,den,reviewwise)),None)
                costs=[];worst_state=None;worst=-1
                for pos in range(1<<n):
                    x=next((x for x in candidates if passing(x,pos,known,num,den,reviewwise)),None)
                    v=x[0] if x else 65535;costs.append(v)
                    if v>worst:worst=v;worst_state=pos
                valid=[v for v in costs if v!=65535]
                out={"reviewwise":reviewwise,"fixed_policy":policy(root) if root else None,
                   "fixed_robust_queue":root[0] if root else None,"full_oracle_worst_queue":None if worst==65535 else worst,
                   "full_oracle_best_queue":min(valid,default=None),"adjusted_oracle_queue":None if costs[0]==65535 else costs[0],
                   "restored_oracle_queue":None if costs[-1]==65535 else costs[-1],
                   "infeasible_full_states":costs.count(65535),"full_states":len(costs),"worst_state_mask":worst_state,
                   "full_queue_histogram":dict(Counter(costs))}
                if not reviewwise:
                    r=prior[family+"_"+str(num)]
                    assert out["fixed_robust_queue"]==r["fixed_robust_queue"]
                    assert out["full_oracle_worst_queue"]==r["full_label_oracle_worst_queue"]
                    assert out["adjusted_oracle_queue"]==r["oracle_adjusted_queue"]
                    assert out["restored_oracle_queue"]==r["oracle_full_restored_queue"]
                    assert {str(k):v for k,v in out["full_queue_histogram"].items()}==r["oracle_queue_histogram"]
                    checks+=len(costs)
                result["results"][f"{family}_{num}_{'reviewwise' if reviewwise else 'pooled'}"]=out
    candidates=sorted(x for x in families["all"].values() if x[0]<=473)
    # Exhaustively search every fixed query set of size <=4, with every possible
    # answer pattern. A fixed set succeeds iff every branch has a common policy.
    @lru_cache(None)
    def find(known,pos):
        return next((x for x in candidates if passing(x,pos,known,19,20,False)),None)
    def submasks(x):
        s=x
        while True:
            yield s
            if not s:break
            s=(s-1)&x
    counts={};plans=[]
    for b in range(5):
        cnt=0
        for inds in itertools.combinations(range(n),b):
            m=sum(1<<i for i in inds)
            if all(find(m,s) is not None for s in submasks(m)):
                cnt+=1
                if b==4:plans.append(m)
        counts[b]=cnt
    assert counts=={0:0,1:0,2:0,3:0,4:4}
    @lru_cache(None)
    def can(known,pos,depth):
        if find(known,pos) is not None:return True
        if depth==0:return False
        return any(can(known|(1<<i),pos,depth-1) and can(known|(1<<i),pos|(1<<i),depth-1)
            for i in range(n) if not (known&(1<<i)))
    # independent depth-limited tree search, not the primary 3^14 lattice recurrence.
    assert not can(0,0,3) and can(0,0,4)
    m=min(plans);w=[]
    for pos in sorted(submasks(m)):
        x=find(m,pos);q,hs,d,rs=x
        real=keep[rs[0]]|keep[rs[1]]|keep[rs[2]]
        assert len(real)==q and f<=real and len(real&h)==sum(hs)
        checks_in_branch=0
        for s in submasks(full^m):
            finalpos=pos|s
            ref=h|{dnames[i] for i in range(n) if finalpos&(1<<i)}
            assert 20*len(real&ref)>=19*len(ref)
            checks_in_branch+=1
        # Unique IDs touched by either audit or forwarding; not measured work.
        audit_set={dnames[i] for i in range(n) if m&(1<<i)}
        w.append({"observed_positive_mask":pos,"policy":policy(x),
                  "audited_ids":sorted(audit_set),"audits_already_forwarded":len(audit_set&real),
                  "unique_union_count":len(real|audit_set),"completion_checks":checks_in_branch})
    assert sum(r["completion_checks"] for r in w)==16384 and max(r["policy"]["queue"] for r in w)==473
    result.update({"pooled_full_completion_parity":checks,"four_label_plan_masks":plans,"fixed_query_subset_counts":counts,
                  "adaptive_depth_le3_impossible":True,"adaptive_depth4_possible":True,
                  "direct_4label_plan_completion_checks":sum(r["completion_checks"] for r in w),
                  "chosen_mask":m,"chosen_plan_branches":w,"max_unique_forward_or_audit":max(r["unique_union_count"] for r in w),
                  "status":"PASS"})
    Path("r64_independent_certificate.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("R64_INDEPENDENT_PASS",json.dumps({"fixed_queries":counts,"adaptive_depth":4,"unique_touched_max":result["max_unique_forward_or_audit"],"cases":{k:{a:v for a,v in b.items() if a not in ("full_queue_histogram","fixed_policy")} for k,b in result["results"].items()}},sort_keys=True))
if __name__=="__main__":main()
