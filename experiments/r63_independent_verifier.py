#!/usr/bin/env python3
"""Direct record-set and explicit matched-pair replay independent of the grouped R63 counts.
Outputs derived aggregate counts; no source bibliographic text or raw predictions.
"""
from itertools import combinations, product
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
import json
from r60_minimal_coverage import rows, rawfile, PIN, SHA
PROV="configuration/reference_label_provenance.json"
SHA[PROV]="fd84e981fd70849f3914055ee0d60679b8b5e32206b7a1c08ca0763fd0bca6da"
def main():
    baseline=json.loads(Path("r63_adjudication_certificate.json").read_text())
    records=rows("data/records.csv"); preds=rows("data/predictions.csv.gz")
    configs=json.loads(rawfile("data/runs.json")); reports=json.loads(rawfile("configuration/included_reports.json"))
    changes=json.loads(rawfile(PROV))["corrections_and_confirmations"]
    h={r["record_id"] for r in records if r["reference_retained"]=="1"}
    f={x for r in reports for x in r["record_ids"]}
    d13={c["record_id"] for c in changes if c["origin"].startswith("published adjudication")}
    d14=d13|{c["record_id"] for c in changes if c["origin"].startswith("current author-confirmed")}
    names=sorted(r["run_id"] for r in configs)
    conditions={r["run_id"]:r["condition"] for r in configs}
    keep={k:set() for k in names}
    counts=Counter()
    for r in preds:
        key=r["run_id"]; counts[key]+=1
        if float(r["probability_retained"])>=.5 if r["probability_retained"] else r["decision"]=="I":
            keep[key].add(r["record_id"])
    assert len(h)==113 and len(f)==23 and f<=h and len(d13)==13 and len(d14)==14 and not(h&d14)
    assert all(counts[k]==4527 for k in names)
    assert len(names)==59
    def fam(c):
        return "Jev" if c.startswith(("noul-","choice-")) else "GPT5" if c.startswith("gpt-5") else "GPT6"
    family=defaultdict(list)
    for ids in combinations(names,3):
        s=keep[ids[0]]|keep[ids[1]]|keep[ids[2]]
        x=(len(s),len(s&h),len(s&f),frozenset(s&d13),frozenset(s&d14))
        family["all"].append(x)
        cc={conditions[i] for i in ids}
        if len(cc)==3:family["distinct_configuration"].append(x)
        if {fam(c) for c in cc}=={"Jev","GPT5","GPT6"}:family["family_balanced"].append(x)
    assert [len(family[k]) for k in ("all","distinct_configuration","family_balanced")]==[32509,20377,900]
    out={}; threshold_checks=0; pair_checks=0
    for k,ps in family.items():
        source=baseline["families"][k]
        for target in (Fraction(19,20),Fraction(49,50)):
            for kind in ("H","H13","H14","H_to_H13_all","H_to_H14_all","F_to_H14_all","F"):
                qs=[]
                for q,hh,ff,s13,s14 in ps:
                    a=len(s13);b=len(s14)
                    num,den={"H":(hh,113),"H13":(hh+a,126),"H14":(hh+b,127),"H_to_H13_all":(hh,126-a),"H_to_H14_all":(hh,127-b),"F_to_H14_all":(ff,127-hh-b+ff),"F":(ff,23)}[kind]
                    if num*target.denominator>=den*target.numerator:qs.append(q)
                z=source["targets"][str(target)][kind]
                assert (len(qs),min(qs,default=None))==(z["n"],z["min_queue"])
                threshold_checks+=2
        for label in ("paired_qualified","paired_all_F_complete"):
            byq=defaultdict(list)
            for p in ps:
                q,hh,ff,s13,s14=p
                if ff==23 and (label!="paired_qualified" or hh>=108):
                    byq[q].append(p)
            c=Counter(); radii=Counter(); cert=Counter(); reversed_cert=Counter()
            c["eligible_portfolios"]=sum(len(z) for z in byq.values())
            for q,pp in byq.items():
                for a,b in combinations(pp,2):
                    c["matched_pairs"]+=1
                    if a[1]<b[1]:a,b=b,a
                    delta=a[1]-b[1]; A13,B13=a[3],b[3]; A14,B14=a[4],b[4]
                    v13=len(B13-A13);v=len(B14-A14);u=len(A14-B14)
                    p13=delta+len(A13)-len(B13);p14=delta+len(A14)-len(B14)
                    if delta==0:
                        c["H_ties"]+=1
                        if p13:c["H_tie_broken_H13"]+=1
                        if p14:c["H_tie_broken_H14"]+=1
                        continue
                    c["strict_H_order_pairs"]+=1
                    if p13<0:c["strict_reversal_H13"]+=1
                    if p14<0:
                        c["strict_reversal_H14"]+=1
                        # Under the replay in which every restored record is positive,
                        # the shortest certificate for B strictly winning needs delta+u+1
                        # favorable revealed memberships; all such memberships are B-only.
                        needed=delta+u+1
                        assert needed<=v
                        reversed_cert[needed]+=1
                    if p13==0:c["strict_becomes_tie_H13"]+=1
                    if p14==0:c["strict_becomes_tie_H14"]+=1
                    if v>=delta:c["not_uniform_strict_D14"]+=1
                    if v13>delta:c["some_D13_subset_strict_reversal"]+=1
                    if v>delta:
                        c["some_D14_subset_strict_reversal"]+=1
                        radii[delta+1]+=1
                    if v>0 and v>=delta:cert[v-delta+1]+=1
            orig=source[label]
            assert dict(c)==orig["counts"],(k,label,c,orig["counts"])
            assert {str(i):n for i,n in radii.items()}==orig["min_reversal_restorations_histogram"]
            assert {str(i):n for i,n in cert.items()}==orig["optimistic_A_certificate_size_histogram"]
            assert sum(reversed_cert.values())==c["strict_reversal_H14"]
            pair_checks+=c["matched_pairs"]
            out[k+"_"+label]={"pairs":c["matched_pairs"],"strict":c["strict_H_order_pairs"],"reverse":c["strict_reversal_H14"],"B_winner_certificate_histogram_full_restoration":dict(sorted(reversed_cert.items()))}
    # Verify exact certificate lengths against exhaustive partial observation sets in
    # abstract ternary states. The three possible outputs are strict A, tie, strict B.
    checks=0
    for u in range(5):
        for v in range(5):
            n=u+v
            for delta in range(-5,6):
                for outcome in product((0,1),repeat=n):
                    score=delta+sum(outcome[:u])-sum(outcome[u:])
                    sign=(score>0)-(score<0)
                    target=max(0,v-delta+1) if sign>0 else max(0,delta+u+1) if sign<0 else n
                    best=n+1
                    for r in range(n+1):
                        for ss in combinations(range(n),r):
                            known=set(ss);k=delta+sum(outcome[i] for i in known if i<u)-sum(outcome[i] for i in known if i>=u)
                            lo=k-sum(i not in known for i in range(u,n));hi=k+sum(i not in known for i in range(u))
                            if (sign>0 and lo>0) or (sign<0 and hi<0) or (sign==0 and lo==hi==0):
                                best=r;break
                        if best!=n+1:break
                    assert best==target,(u,v,delta,outcome,best,target)
                    checks+=1
    result={"status":"PASS","source_pin":PIN,"source_hashes":SHA,"direct_pair_replays":pair_checks,
        "threshold_count_and_queue_checks":threshold_checks,"finite_certificate_checks":checks,
        "results":out,"scope":"All counts are conditional on the archived model outputs and declared label variants; no new adjudication or independent corpus."}
    Path("r63_independent_verifier.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("R63_INDEPENDENT_PASS",json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
