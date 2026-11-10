#!/usr/bin/env python3
"""Source-first audit for DOI 10.17632/4bgt2p5hrd.1 (Vallamchetla 2025).

Acquires a public CSV, hashes it, reconstructs record-level reviewer confusion
counts, and checks paired decisions. Does NOT infer treatment effects: four
reviewers were not randomly assigned, and no per-record time logs are supplied.
The original dataset remains a third-party source and is NEVER redistributed
in this audit package; only original derived numerical summaries are exported.
"""
import csv, io, json, hashlib, math, urllib.request, urllib.error, re, os, sys, time
from collections import Counter
from pathlib import Path

ID='4bgt2p5hrd'; VERSION=1
ROOT=Path(__file__).resolve().parents[2] if 'research_probes' in str(Path(__file__)) else Path(__file__).parent
OUT=Path(os.environ.get('R38_OUTPUT',str(ROOT/'r38_output')))
OUT.mkdir(exist_ok=True, parents=True)
LOG=[]

def note(s):
    t=str(s); print(t,flush=True); LOG.append(t)

def get(url,limit=20_000_000):
    req=urllib.request.Request(url,headers={'User-Agent':'99a-public-research-source-verifier/1.0 (academic metadata)','Accept':'application/json,text/csv,application/octet-stream,*/*'})
    with urllib.request.urlopen(req,timeout=40) as r:
        c=r.read(limit+1)
        if len(c)>limit:raise ValueError('Response exceeded size safety limit')
        return c, r.geturl(),r.headers.get('Content-Type','')

def get_json_candidates(urls):
    for u in urls:
        try:
            raw, final, ct=get(u)
            obj=json.loads(raw)
            note(f'METADATA PASS source={u.split("?")[0]} bytes={len(raw)} type={type(obj).__name__}')
            if isinstance(obj,dict):note(f'METADATA KEYS {sorted(obj.keys())}')
            return obj
        except Exception as e:note(f'METADATA TRY FAILED {u.split("?")[0]} {type(e).__name__}: {str(e)[:250]}')
    return None

def collect_files(obj):
    if not obj:return []
    if isinstance(obj,list):return obj
    for k in ['files','results','data']:
        v=obj.get(k)
        if isinstance(v,list):return v
        if isinstance(v,dict):return collect_files(v)
    return []

def download_csv():
    # Public API documented by the Mendeley/Elsevier Digital Commons Data API.
    base=f'https://api.data.mendeley.com/datasets/{ID}'
    obj=get_json_candidates([base+f'?version={VERSION}',base+f'/snapshot?version={VERSION}'])
    fs=collect_files(obj)
    if not fs:
        note('FILE LIST not provided in dataset metadata; querying public file endpoint')
        other=get_json_candidates([f'https://api.data.mendeley.com/datasets/publics/{ID}/files?version={VERSION}',base+f'/files?version={VERSION}'])
        fs=collect_files(other)
    note('PUBLIC FILE COUNT '+str(len(fs)))
    for f in fs:
        if not isinstance(f,dict):continue
        fn=f.get('filename') or f.get('name') or ''
        note('PUBLIC FILE metadata '+json.dumps({'filename':fn,'size':f.get('size'),'id':f.get('id')},ensure_ascii=False))
    candidates=[]
    for f in fs:
        if not isinstance(f,dict):continue
        fn=(f.get('filename') or f.get('name') or '').lower()
        if fn.endswith('.csv'):
            cd=f.get('content_details') or {}
            fid=f.get('id') or f.get('file_id')
            urls=[]
            if cd.get('download_url'):urls.append(cd['download_url'])
            if f.get('download_url'):urls.append(f['download_url'])
            if fid:
                urls.extend([f'https://api.data.mendeley.com/datasets/{ID}/files/{fid}/file_downloaded?version={VERSION}',f'https://api.data.mendeley.com/datasets/publics/{ID}/files/{fid}/file_downloaded?version={VERSION}'])
            candidates.append((f,urls))
    for f,urls in candidates:
        for u in urls:
            try:
                raw,final,typ=get(u)
                note(f'FILE DOWNLOAD PASS filename={f.get("filename")} bytes={len(raw)} type={typ}')
                if b'Gold' not in raw[:10000] and b'gold' not in raw[:10000]:
                    note('FILE HOLD: header did not include expected gold reference')
                return raw, f, obj
            except Exception as e: note(f'FILE DOWNLOAD failed {u.split("?")[0]}: {type(e).__name__} {str(e)[:200]}')
    raise RuntimeError('No authorized CSV bytes accessible through documented public API; do not infer data values')

def normalize(s):
    if s is None:return None
    a=str(s).strip().casefold()
    a=re.sub(r'[\s_\-.]+','',a)
    if a in ('include','included','inclusion','yes','y','1','true','relevant','accept','accepted','positive'):return 1
    if a in ('exclude','excluded','exclusion','no','n','0','false','irrelevant','reject','rejected','negative'):return 0
    return None

def colmap(fields):
    def norm(s):return re.sub('[^a-z0-9]','',s.lower())
    d={norm(k):k for k in fields}
    names={
      'gold':['goldstd','goldstddataset','goldstandard','goldlabel','reference','gold'],
      'A1':['a1reviewer','reviewera1','a1'],
      'A2':['a2reviewer','reviewera2','a2'],
      'B1':['b1reviewer','reviewerb1','b1'],
      'B2':['b2reviewer','reviewerb2','b2']}
    out={}
    for key,aliases in names.items():
        for a in aliases:
            if a in d:out[key]=d[a];break
        if key not in out:
            for k,v in d.items():
                if any(k.startswith(a) for a in aliases):out[key]=v;break
    return out

def paired_exact_p(b,c):
    n=b+c
    if n==0:return 1.0
    # P(two-sided exact McNemar) = min(1,2*P[Bin(n,0.5)<=min(b,c)])
    k=min(b,c)
    return min(1.0,2*sum(math.comb(n,i) for i in range(k+1))/(2**n))

def analyze(raw,metadata,source_meta):
    sha=hashlib.sha256(raw).hexdigest()
    text=None;encoding=None
    for enc in ['utf-8-sig','utf-8','latin-1']:
        try:text=raw.decode(enc);encoding=enc;break
        except UnicodeDecodeError:continue
    if text is None:raise RuntimeError('CSV undecodable')
    sep='\t' if text.splitlines()[0].count('\t')>text.splitlines()[0].count(',') else ','
    rd=csv.DictReader(io.StringIO(text,newline=''),delimiter=sep)
    names=rd.fieldnames or []
    note('CSV HEADER '+repr(names))
    cols=colmap(names)
    if set(cols)!={'gold','A1','A2','B1','B2'}:
        raise ValueError(f'critical columns missing; found={cols}; all={names}')
    rows=list(rd)
    note('CSV ROW COUNT '+str(len(rows)))
    n=len(rows)
    summary={'status':'ADMITTED_SOURCE_REANALYSIS','source_dataset_doi':'10.17632/4bgt2p5hrd.1','source_article_doi':'10.1016/j.jbi.2025.104860', 'dataset_version':1,
     'license':'CC BY-NC 4.0; original raw file not redistributed','file_name':metadata.get('filename'), 'downloaded_bytes':len(raw),'sha256_of_original_bytes':sha,'n_records':n,'column_names':names,'detected_columns':cols,'encoding':encoding,
     'design':'4 human reviewers, two assisted with LLM-generated PICOS, two without, same record set; reviewer identity and experience confounded with assistance; nonrandom',
     'cautions':['Reference is authors expert gold standard; cannot independently verify actual eligibility','Aggregate screening times are from article, not per-record time logs','Record-level paired comparisons between distinct reviewers do not identify an AI assistance causal effect','No LLM model predictions rerun','Sample is one task/review and not a cross-study prevalence estimate']}
    if n!=1003:
        summary['status']='HOLD_COHORT_MISMATCH'; note('HOLD expected N=1003 but got '+str(n))
    valids=[]; bad=Counter()
    for i,row in enumerate(rows):
        v={k:normalize(row[col]) for k,col in cols.items()}
        if any(z is None for z in v.values()):
            for k,z in v.items():
                if z is None:bad[(k,str(row[cols[k]])[:50])]+=1
        else:valids.append(v)
    summary['complete_rows']=len(valids);summary['invalid_label_values']=[{'field':k,'value':val,'count':ct} for (k,val),ct in bad.items()]
    note('COMPLETE LABEL ROWS '+str(len(valids))+' INVALID '+str(sum(bad.values())))
    if len(valids)!=n:
        summary['status']='HOLD_INVALID_LABELS'; note('HOLD: not all reviewer labels recognized, source audit requires decision')
        return summary,[],[]
    pos=sum(v['gold'] for v in valids);summary['gold_positives']=pos;summary['gold_negatives']=n-pos
    dmetrics=[]
    for k,assisted,minutes in [('A1',True,116),('A2',False,463),('B1',True,90),('B2',False,370)]:
        tp=sum(v['gold']==1 and v[k]==1 for v in valids);fp=sum(v['gold']==0 and v[k]==1 for v in valids)
        tn=sum(v['gold']==0 and v[k]==0 for v in valids);fn=sum(v['gold']==1 and v[k]==0 for v in valids)
        d={'reviewer':k,'picos_assisted':assisted,'total':n,'gold_positives':pos,'tp':tp,'fp':fp,'fn':fn,'tn':tn,
           'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/pos if pos else None,'specificity':tn/(n-pos) if n>pos else None,
           'accuracy':(tp+tn)/n,'minutes_reported_in_published_article_NOT_per_record_log':minutes,
           'seconds_per_record_aggregate':minutes*60/n}
        dmetrics.append(d)
    pairs=[]
    for ass,un in [('A1','A2'),('B1','B2')]:
        b=sum((v[ass]==v['gold']) and (v[un]!=v['gold']) for v in valids)
        c=sum((v[ass]!=v['gold']) and (v[un]==v['gold']) for v in valids)
        both=sum((v[ass]==v['gold']) and (v[un]==v['gold']) for v in valids)
        neither=n-b-c-both
        bpos=sum(v['gold'] and (v[ass]==v['gold']) and (v[un]!=v['gold']) for v in valids)
        cpos=sum(v['gold'] and (v[ass]!=v['gold']) and (v[un]==v['gold']) for v in valids)
        tm={'A1':116,'A2':463,'B1':90,'B2':370}
        pairs.append({'assisted_reviewer':ass,'unassisted_reviewer':un,
          'both_correct':both,'assisted_only_correct':b,'unassisted_only_correct':c,'neither_correct':neither,
          'positive_reference_assisted_only_correct':bpos,'positive_reference_unassisted_only_correct':cpos,
          'exact_paired_discordance_p_DESCRIPTIVE_NOT_TREATMENT_TEST':paired_exact_p(b,c),
          'assisted_published_minutes':tm[ass],'unassisted_published_minutes':tm[un],
          'ratio_assisted_time_to_unassisted_reported_time':tm[ass]/tm[un],
          'minutes_difference_noncausal':tm[un]-tm[ass]})
    summary['reviewers']=dmetrics;summary['paired_reviewers']=pairs
    note('REVIEWER COUNTS '+json.dumps([{k:v for k,v in z.items() if k in ('reviewer','tp','fp','fn','tn')} for z in dmetrics]))
    return summary,dmetrics,pairs

def write_csv(path,rows):
    if not rows:return
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    result={'status':'HOLD_ACCESS','source_dataset_doi':'10.17632/4bgt2p5hrd.1','source_link':'https://data.mendeley.com/datasets/4bgt2p5hrd/1',
            'source_article_doi':'10.1016/j.jbi.2025.104860','license':'CC BY-NC 4.0','raw_file_copied_to_public_package':False}
    try:
        raw,metadata,source_meta=download_csv()
        result,reviewers,pairs=analyze(raw,metadata,source_meta)
        result['raw_file_copied_to_public_package']=False
        write_csv(OUT/'R38_Reviewer_Matrices.csv',reviewers)
        write_csv(OUT/'R38_Paired_Contrasts.csv',pairs)
    except Exception as e:
        result['status']='HOLD_ACQUISITION_OR_VALIDATION'
        result['error_type']=type(e).__name__;result['error_message']=str(e)[:800]
        note('HOLD '+str(e))
    (OUT/'R38_PICOS_SourceAdmission.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'R38_Acquisition_Log.txt').write_text('\n'.join(LOG)+'\n',encoding='utf-8')
    note('FINAL STATUS '+result['status'])
    return 0 if result['status']=='ADMITTED_SOURCE_REANALYSIS' else 2

if __name__=='__main__':sys.exit(main())
