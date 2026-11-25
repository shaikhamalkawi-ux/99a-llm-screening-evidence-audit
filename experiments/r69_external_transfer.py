#!/usr/bin/env python3
"""Frozen R68 lexical-ordering transfer, on Aigner et al. public saved binary outputs.
Never rerun an LLM; no redistribution of source texts, IDs or predictions.
"""
import hashlib,io,json,math,unicodedata,re,urllib.request
from fractions import Fraction
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from scipy.stats import hypergeom

PIN="c854aa341fb7b19a0b33f4f14898d841ccbc2e0d"
ROOT="https://raw.githubusercontent.com/MarcoAigner/automated_title_abstract_screening/"+PIN+"/"
FILES={
"adhd":("08f506c17e182c4e4516f9c544efcd17bf9c3e47","a454528178aff3e999b27687b6b9ef0c7102d274"),
"animal_depression":("6dd01ec0550f0c95c46e8eb87daae2db85523519","120e7786f5fc526ec6d3cb1a6ed6edf9b2b21b67"),
"atypical_antipsychotics":("cdd32dfef558ec1e5dc6e49bc70b4979952a45bd","d935bf5f346b162f43dfe93c754942bef586e35c"),
"calcium_channel_blockers":("6cfc0755fe4602871b3f8780a14abd021f08b76a","e150c35fe853d2682364e258c5b87d4c6c2c836a"),
"oral_hypoglycemics":("11922e1ed76fb157ee4415eb622004941cad9c28","9b42fdc9675ab5ecd75c66e58787032634d2fd79")}
GRID=(0,1,2,5,10,25,50,100,250,500,1000)
def get(path,sha):
    with urllib.request.urlopen(ROOT+path,timeout=40) as r:b=r.read()
    assert hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()==sha,("blob mismatch",path)
    return pd.read_csv(io.BytesIO(b),dtype=str,keep_default_na=False),{"path":path,"git_blob":sha,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
def norm(s):return " ".join(unicodedata.normalize("NFKC",s).split())
def idnorm(s):
    s=norm(s).lower()
    if s in {"","nan","none","null","na"}:return ""
    if re.fullmatch(r"[0-9]+\.0+",s):return s.split(".")[0]
    return s
def bools(s):
    x=s.str.lower().str.strip()
    assert set(x)<={"true","false","0","1"},("nonbinary",sorted(set(x)))
    return x.isin(["true","1"]).to_numpy()
def rank(text,yes):
    X=TfidfVectorizer(lowercase=True,stop_words="english",ngram_range=(1,2),min_df=1,sublinear_tf=True,norm="l2",dtype=np.float64).fit_transform(text)
    assert yes.any()
    center=normalize(np.asarray(X[yes].mean(axis=0)))
    scores=np.asarray(X@center.T).ravel()
    excluded=np.flatnonzero(~yes)
    ix=sorted(excluded,key=lambda i:(-scores[i],int(i)))
    # alternate numerical calculation, verify scores and prefix set to tolerance
    center2=np.asarray(X[yes].sum(axis=0)).ravel();center2/=np.linalg.norm(center2)
    score2=np.asarray(X.dot(center2)).ravel()
    assert np.max(np.abs(score2-scores))<=1e-12
    return np.asarray(ix,dtype=int),scores
def prob(N,K,b,s):
    if s<=0:return Fraction(1)
    return Fraction(sum(math.comb(K,j)*math.comb(N-K,b-j) for j in range(s,min(K,b)+1) if 0<=b-j<=N-K),math.comb(N,b))
def evaluate(topic):
    a,ma=get("data/datasets/04_preprocessed/"+topic+"_preprocessed.csv",FILES[topic][0])
    p,mp=get("data/predictions/llama_3_1_8B/"+topic+"_pred.csv",FILES[topic][1])
    assert {"title","abstract","include","index","doi","pubmed_id"}<=set(a),("data schema",list(a))
    assert {"title","include","doi","pubmed_id"}<=set(p),("pred schema",list(p))
    assert len(a)==len(p) and a["index"].is_unique and (a["index"]!="").all(),("nonidentical population",len(a),len(p))
    checks={}
    for col,fn in [("title",norm),("doi",idnorm),("pubmed_id",idnorm)]:
        x=a[col].map(fn).tolist();y=p[col].map(fn).tolist()
        assert x==y,("row-order identity mismatch",col,sum(u!=v for u,v in zip(x,y)))
        checks[col]=len(x)
    yes=bools(p["include"])
    # rank without the source reference column; no test labels passed to rank().
    text=(a["title"]+"\n"+a["abstract"]).tolist()
    ix,scores=rank(text,yes)
    y=bools(a["include"]);N=len(y);P=int(y.sum());M=int((~yes&y).sum());q=int(yes.sum())
    assert P>0 and len(ix)==N-q
    h=int((y&yes).sum())
    ranks=[int(i+1) for i,x in enumerate(ix) if y[x]]
    assert len(ranks)==M
    req=max(0,(49*P+49)//50-h)
    rows=[]
    for b0 in GRID:
        b=min(b0,len(ix));rec=sum(k<=b for k in ranks);r=h+rec
        expect=Fraction(M*b,len(ix)) if len(ix) else Fraction(0)
        ch=prob(len(ix),M,b,req)
        # direct recordwise set equality; hypergeometric agreement, only numerical comparison
        accepted=set(np.flatnonzero(yes))|set(ix[:b])
        assert len(accepted)==q+b and sum(bool(y[i]) for i in accepted)==r
        assert abs(float(ch)-(1. if req==0 else float(hypergeom.sf(req-1,len(ix),M,b))))<1e-10
        rows.append({"b_nominal":b0,"b_actual":b,"touched":q+b,"positives_retained":r,"misses_recovered":rec,"passes_98":50*r>=49*P,
                     "expected_uniform_hits":str(expect),"uniform_probability_98":float(ch)})
    # Exact possible identity-overlap guarantee at same nominal budget; no statistical claim.
    b=min(50,len(ix));g=max(0,b+M-len(ix))
    ties=sum(abs(scores[j]-scores[ix[b-1]])<=1e-12 for j in ix) if b else 0
    return {"topic":topic,"N":N,"P":P,"base_touched":q,"base_TP":h,"missed":M,"missed_ranks":ranks,
            "required_to_recover_98":req,"oracle_rank_prefix_98":ranks[req-1] if req else 0,
            "guaranteed_random_or_arbitrary_identity_hits_at_50":g,"tie_size_at_50":ties,"grid":rows,
            "row_alignment_checks":checks,"hashes":[ma,mp],"status":"PASS"}
def main():
    ans=[]
    for t in FILES:
        try:ans.append(evaluate(t))
        except Exception as e:ans.append({"topic":t,"status":"HOLD","reason":str(e)[:2000]})
    out={"source":"Aigner et al. 2026 doi:10.1186/s13643-026-03199-6; five public SYNERGY-derived reviews, source inclusion flags; not H/full-text forwarding labels",
         "source_commit":PIN,"primary":"R68 text ranking and 50-record budget locked before external label analysis; binary Llama Include as centroid seed; source row order tie-break",
         "scope":"Post hoc independent model-output archive transfer, not independent of all older SYNERGY data in project; no prospective certification, no human timing, no retraining",
         "results":ans}
    Path("r69_external_transfer.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
