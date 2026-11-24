#!/usr/bin/env python3
"""Exact exploratory audit of source-documented reference restorations.
No model inference, new human judgments or redistributions of source records.
"""
import itertools, json, math
from collections import Counter,defaultdict
from fractions import Fraction
from pathlib import Path
from r60_minimal_coverage import rows,rawfile,PIN,SHA
PROV="configuration/reference_label_provenance.json"
SHA[PROV]="fd84e981fd70849f3914055ee0d60679b8b5e32206b7a1c08ca0763fd0bca6da"

def main():
    rec=rows("data/records.csv"); pred=rows("data/predictions.csv.gz")
    run=json.loads(rawfile("data/runs.json")); reports=json.loads(rawfile("configuration/included_reports.json"))
    prov=json.loads(rawfile(PROV))
    assert prov["fixed_before_final_runs"]
    ids={r["record_id"]:i for i,r in enumerate(rec)}
    names=sorted(x["run_id"] for x in run); byrun={n:i for i,n in enumerate(names)}
    cond={x["run_id"]:x["condition"] for x in run}
    assert len(rec)==len(ids)==4527 and len(names)==59 and len(pred)==267093
    H=sum(1<<i for i,r in enumerate(rec) if r["reference_retained"]=="1")
    F=sum(1<<i for i in {ids[s] for e in reports for s in e["record_ids"]})
    changes=prov["corrections_and_confirmations"]
    d13=[c["record_id"] for c in changes if c["origin"].startswith("published adjudication")]
    extra=[c["record_id"] for c in changes if c["origin"].startswith("current author-confirmed")]
    assert len(changes)==16 and len(d13)==13 and extra==["maruki:1240"]
    assert len(set(d13+extra))==14
    dnames=sorted(d13+extra)
    D=sum(1<<ids[x] for x in dnames)
    D13=sum(1<<ids[x] for x in d13)
    assert (H.bit_count(),F.bit_count(),D.bit_count())==(113,23,14)
    assert not (D&H) and not(F&~H)
    M=[0]*59; seen=set()
    for r in pred:
        j=byrun[r["run_id"]];i=ids[r["record_id"]]
        assert (j,i) not in seen
        seen.add((j,i))
        keep=float(r["probability_retained"])>=.5 if r["probability_retained"] else r["decision"]=="I"
        if keep:M[j]|=1<<i
    assert len(seen)==4527*59
    def fam(c):
        if c.startswith(("choice-","noul-")):return "Jev"
        if c.startswith("gpt-5"):return "GPT5"
        if c.startswith("gpt-6"):return "GPT6"
        raise ValueError(c)
    def dm(m):
        return sum(1<<j for j,x in enumerate(dnames) if m&(1<<ids[x]))
    d13small=dm(D13)
    def item(ind,m):
        return (ind,m.bit_count(),(m&H).bit_count(),(m&F).bit_count(),dm(m))
    def serialize(x):
        ind,q,h,f,d=x
        return {"runs":[names[i] for i in ind],"queue":q,"H":h,"F":f,"D13_covered":(d&d13small).bit_count(),"D14_covered":d.bit_count(),"H13":h+(d&d13small).bit_count(),"H14":h+d.bit_count(),"D_mask":d}
    def cutoff(data,target,kind):
        def good(x):
            _,q,h,f,d=x;a13=(d&d13small).bit_count();a=d.bit_count()
            rates={"H":Fraction(h,113),"H13":Fraction(h+a13,126),"H14":Fraction(h+a,127),
                   "H_to_H13_all":Fraction(h,126-a13),"H_to_H14_all":Fraction(h,127-a),
                   "F_to_H14_all":Fraction(f,127-h-a+f),"F":Fraction(f,23)}
            return rates[kind]>=target
        eligible=[x for x in data if good(x)]
        return {"n":len(eligible),"min_queue":min((x[1] for x in eligible),default=None),
                "witness":serialize(min(eligible,key=lambda x:(x[1],x[0]))) if eligible else None}
    refs=["H","H13","H14","H_to_H13_all","H_to_H14_all","F_to_H14_all","F"]
    full=0
    for m in M: full|=m
    data={}; balanced=[]; diffconfig=[]
    for k in (1,2,3):
        xs=[]
        for ind in itertools.combinations(range(59),k):
            m=0
            for j in ind:m|=M[j]
            x=item(ind,m);xs.append(x)
            if k==3:
                cs={cond[names[j]] for j in ind}
                if len(cs)==3:diffconfig.append(x)
                if {fam(c) for c in cs}=={"Jev","GPT5","GPT6"}:balanced.append(x)
        data[str(k)]=xs
    assert list(map(len,data.values()))==[59,1711,32509]
    assert (len(diffconfig),len(balanced))==(20377,900)
    def frontier(xs):
        out={}
        for kind in ["H","H13","H14"]:
            def value(x):
                return x[2]+({"H":0,"H13":(x[4]&d13small).bit_count(),"H14":x[4].bit_count()}[kind])
            w=min(xs,key=lambda x:(-value(x),x[1],x[0]))
            out[kind]={"max":value(w),"min_queue_at_max":w[1],"witness":serialize(w)}
        return out
    def audit_pairs(xs,qualify):
        groups=defaultdict(dict)
        for x in xs:
            if x[3]!=23 or (qualify and x[2]<108):continue
            key=(x[2],x[4]); g=groups[x[1]]
            if key not in g:g[key]=[0,x]
            g[key][0]+=1
        totals=Counter(); radius=Counter(); witnesses={}; sizes=Counter()
        def add(k,n):totals[k]+=n
        def store(kind,a,b,delta,extra_a,extra_b,extra_a13,extra_b13,u,v,u13,v13):
            if kind in witnesses:return
            witnesses[kind]={"A":serialize(a),"B":serialize(b),"delta_H":delta,"delta_H13":delta+extra_a13-extra_b13,
               "delta_H14":delta+extra_a-extra_b,"D14_A_only":u,"D14_B_only":v,"D13_A_only":u13,"D13_B_only":v13,
               "min_restorations_to_strict_reverse":delta+1 if v>delta else None}
        for q,g in sorted(groups.items()):
            n=sum(z[0] for z in g.values())
            totals["eligible_portfolios"]+=n;totals["matched_pairs"]+=math.comb(n,2)
            for (h,d),(c,x) in g.items():
                totals["H_ties"]+=math.comb(c,2)
            for (ha,da),(hb,db) in itertools.combinations(sorted(g,reverse=True),2):
                ca,a=g[(ha,da)];cb,b=g[(hb,db)];n=ca*cb
                delta=ha-hb; a14=da.bit_count();b14=db.bit_count();a13=(da&d13small).bit_count();b13=(db&d13small).bit_count()
                d14=delta+a14-b14;d13=delta+a13-b13
                u=(da&~db).bit_count();v=(db&~da).bit_count();u13=(da&~db&d13small).bit_count();v13=(db&~da&d13small).bit_count()
                assert d14==delta+u-v and d13==delta+u13-v13
                if not delta:
                    add("H_ties",n)
                    if d14:add("H_tie_broken_H14",n)
                    if d13:add("H_tie_broken_H13",n)
                    continue
                add("strict_H_order_pairs",n)
                if d14<0:add("strict_reversal_H14",n);store("actual_H14_reversal",a,b,delta,a14,b14,a13,b13,u,v,u13,v13)
                if d13<0:add("strict_reversal_H13",n);store("actual_H13_reversal",a,b,delta,a14,b14,a13,b13,u,v,u13,v13)
                if d14==0:add("strict_becomes_tie_H14",n)
                if d13==0:add("strict_becomes_tie_H13",n)
                if v>=delta:add("not_uniform_strict_D14",n)
                if v>delta:
                    add("some_D14_subset_strict_reversal",n);radius[delta+1]+=n
                    store("subset_reversal",a,b,delta,a14,b14,a13,b13,u,v,u13,v13)
                if v13>delta:add("some_D13_subset_strict_reversal",n)
                if v>0 and delta-v<=0:
                    # Best-case number of resolved informative bits necessary and sufficient to certify A,
                    # if a completion favoring A is available; not measured human workload.
                    sizes[v-delta+1]+=n
        assert totals["H_ties"]+totals["strict_H_order_pairs"]==totals["matched_pairs"]
        assert totals["strict_reversal_H14"]<=totals["some_D14_subset_strict_reversal"]
        return {"counts":dict(totals),"min_reversal_restorations_histogram":dict(radius),"optimistic_A_certificate_size_histogram":dict(sizes),"witnesses":witnesses}
    dsets={"all":data["3"],"distinct_configuration":diffconfig,"family_balanced":balanced}
    res={"pin":PIN,"hashes":SHA,"reference_totals":{"H":113,"H13":126,"H14":127,"F":23},
         "source_semantics":"Exactly source-defined scenarios, 13 published adjudications restored, plus one related report for 14; two other resolutions remain unchanged. Not independently re-adjudicated labels.",
         "N":4527,"predictions":267093,"full_union":serialize(item(tuple(range(59)),full)),
         "restored_vote_histogram":dict(Counter(sum(bool(m&(1<<ids[x])) for m in M) for x in dnames)),
         "frontier":{k:frontier(xs) for k,xs in data.items()},
         "families":{k:{"n":len(xs),"targets":{str(t):{kind:cutoff(xs,t,kind) for kind in refs} for t in (Fraction(19,20),Fraction(49,50))},
            "paired_qualified":audit_pairs(xs,True),"paired_all_F_complete":audit_pairs(xs,False)} for k,xs in dsets.items()},
         "limits":["Retrospective exact combinatorial counts; not independent trials.",
          "Restorations are historical reference variants, not true eligibility.",
          "All subset restorations are hypothetical sensitivity scenarios.",
          "Queue is number of distinct records, not observed human labor."]}
    # Verify the published pair witnesses using independently reconstructed record sets.
    witness_count=0
    for group in res["families"].values():
        for typ in ("paired_qualified","paired_all_F_complete"):
            for w in group[typ]["witnesses"].values():
                keep={}
                for side in ("A","B"):
                    rr=set(w[side]["runs"])
                    ss={p["record_id"] for p in pred if p["run_id"] in rr and (float(p["probability_retained"])>=.5 if p["probability_retained"] else p["decision"]=="I")}
                    keep[side]=ss
                    hh={r["record_id"] for r in rec if r["reference_retained"]=="1"}
                    ff={s for e in reports for s in e["record_ids"]}
                    assert (len(ss),len(ss&hh),len(ss&ff),len(ss&set(d13)),len(ss&set(dnames)))==tuple(w[side][k] for k in ("queue","H","F","D13_covered","D14_covered"))
                u=(keep["A"]-keep["B"])&set(dnames);v=(keep["B"]-keep["A"])&set(dnames)
                assert (len(u),len(v))==(w["D14_A_only"],w["D14_B_only"])
                # Enumerate every admissible restoration on the DIFFERING identities.
                vals=[]
                for z in itertools.product((0,1),repeat=len(u)+len(v)):
                    vals.append(w["delta_H"]+sum(z[:len(u)])-sum(z[len(u):]))
                assert min(vals)==w["delta_H"]-len(v) and max(vals)==w["delta_H"]+len(u)
                witness_count+=1
    res["alternate_set_witness_checks"]=witness_count
    Path("r63_adjudication_certificate.json").write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print("R63_PASS",json.dumps({"full_union":res["full_union"],"frontier":res["frontier"],"qualified":{k:v["paired_qualified"] for k,v in res["families"].items()}},sort_keys=True))
if __name__=="__main__":main()
