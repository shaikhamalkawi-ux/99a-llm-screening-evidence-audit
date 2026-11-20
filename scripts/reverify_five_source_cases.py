#!/usr/bin/env python3
"""Independent arithmetic readback of FIVE publisher PDFs for Project 99a.

Usage:
    python reverify_five_source_cases.py --source-dir /mnt/data --out R45_FiveCase_Readback.json

Only reported aggregate inputs are used. The source copies are user-provided and
are NEVER included in public reproducibility ZIPs or manuscript packages.
Source-stage/aggregation alternatives remain unresolved, not silently repaired.
"""
import argparse,hashlib,json,re
from pathlib import Path
from fractions import Fraction as Q

PUBLISHERS={
 'zhang': {'filename':'1-s2.0-S1386505625002527-main.pdf','sha256':'736940c3a95a216cc0b864e92d3bf4ba95a5c3bd1a3137c7f5fd1c72423f9b8c','doi':'10.1016/j.ijmedinf.2025.106035','pages':[1,2]},
 'insuk': {'filename':'s10916-025-02246-4.pdf','sha256':'50bd7c2f3d58de827a18b6325f6524ab6a6107f784d41fa8108b98084c208eed','doi':'10.1007/s10916-025-02246-4','pages':[3,5]},
 'cao': {'filename':'cao-et-al-2025-development-of-prompt-templates-for-large-language-model-driven-screening-in-systematic-reviews.pdf','sha256':'0734a7b3b07cc37166608ad627309e1e4c45854a7ce1a60ed272c3bc90ec4a1b','doi':'10.7326/ANNALS-24-02189','pages':[4,6,7]},
 'janoudi': {'filename':'PIIS1098301525025653 (1).pdf','sha256':'07fb23032dbd81fb09cfba5e004a887c34b44f2d2c0483d152ba7b74feb1ad7c','doi':'10.1016/j.jval.2025.09.008','pages':[3,4,5]},
 'li': {'filename':'1-s2.0-S1386505625004228-main (2).pdf','sha256':'04bbfe3d75ee90b96d4f211d964ae38b8cedc808a3c6bc40592192a1cff800da','doi':'10.1016/j.ijmedinf.2025.106205','pages':[1,3,5]}
}

def ratio(x,y):return Q(x,y)
def round2(p,d):
    # ordinary nearest rounding half-open [display - 0.5*10^-d, display +0.5*10^-d)
    lower=p-Q(1,2*10**d)
    upper=p+Q(1,2*10**d)
    return lower,upper

def independent_arithmetic():
    results={}
    # Zhang: contradictory displayed source cohort sizes without claiming one is corrected
    a,b=Q(6100,959),Q(6100,936)
    assert round(float(a),1)==6.4 and round(float(b),1)==6.5
    results['zhang']={'original_abstract_and_table_1_N':959,'methods_sentence_N':936,'source_included':61,
        'inclusion_rate_if_959_pct':float(a),'inclusion_rate_if_936_pct':float(b),
        'verdict':'UNRESOLVED_WITHIN_REPORT_STAGE_DENOMINATOR; no correction proposed'}
    # Insuk: use same reference set and published auto-exclude/recall; independent count recon
    n=1648; pos=33; refneg=n-pos
    excl={'junior':1572,'chatgpt':1485,'claude':1536}; tp={'junior':21,'chatgpt':27,'claude':27}
    shown={'junior':Q(378,10000),'chatgpt':Q(884,10000),'claude':Q(574,10000)}
    out={}
    for k in excl:
        tp0=tp[k];fn=pos-tp0;fp=(n-excl[k])-tp0;tn=refneg-fp
        assert tp0+fn+fp+tn==n and fn>=0 and fp>=0 and tn>=0
        fpr=ratio(fp,fp+tn)
        out[k]={'TP':tp0,'FP':fp,'FN':fn,'TN':tn,'standard_FPR':float(fpr),'printed_FPR':float(shown[k]),'delta_FPR':float(fpr-shown[k])}
    assert [out[k]['FP'] for k in ('junior','chatgpt','claude')]==[55,136,85]
    results['insuk']={'screening_records_reported':1648,'experienced_reviewer_excluded':1615,'positive_reference':33,
         'table3_heading_reports_n':1684,'conditional_common_reference_matrices':out,
         'verdict':'FPR_AND_HEADING_NOT_RECONCILED; no confirmed study error'}
    # Cao: time is a declared model input and full-text availability not stage-wide recall.
    hours=Q(10_000*30,3600)
    assert float(hours)>83.3 and float(hours)<83.4
    results['cao']={'source_estimated_abstract_seconds_per_record':30,'hypothetical_manual_hours_for_10000':float(hours),
        'publisher_free_fulltext_count':12690,'share_all_search_pct':7.56,'share_original_included_pct':59.16,
        'counterfactual_upper_recall_percent_if_unavailable_fulltext_auto_excluded':59.16,
        'verdict':'MODELED_NOT_OBSERVED_PERSON_TIME; fulltext gate only counterfactual'}
    # Janoudi: all numbers are model-to-reference or hypothetical perfect repair of positive Include queues.
    TP0,FN0,FP0,TN0=284,3,167,3342
    assert TP0+FN0+FP0+TN0==3796
    vals={}
    for m,c,t,target in [(145,102,43,Q(814,1000)),(221,135,86,Q(899,1000))]:
        assert c+t==m
        ideal_precision=Q(TP0,TP0+FP0-c)
        lo,hi=round2(target,3) # fraction percent as proportions one decimal pct = 0.001
        compatible=[]
        for x in range(c+1):
            for y in range(t+1):
                p=Q(TP0-y,TP0-y+FP0-x)
                if lo<=p<hi:compatible.append([x,y])
        assert compatible==[[c,0]],compatible
        vals[str(m)]={'false_includes_corrected_under_ideal':c,'true_includes_flagged':t,
            'ideal_precision':float(ideal_precision),'one_decimal_published_pct':float(target*100),
            'all_binary_reversal_states_matching_display':compatible,'baseline_false_negatives_persist':FN0}
    results['janoudi']={'baseline':{'TP':TP0,'FN':FN0,'FP':FP0,'TN':TN0},'include_only_simulation':vals,
          'verdict':'UNIQUE_IDEAL_CORRECTION_DISPLAY_UNDER_BINARY_GRID; not executed human work'}
    # Li: full exact integer enumeration for one common-unweighted 6331 record source reference.
    compatible=[]
    for tp in range(114):
        fn=113-tp
        for fp in range(6219):
            tn=6218-fp
            if tp+fp==0 or tn+fn==0:continue
            if (Q(765,1000)<=Q(tp,113)<Q(775,1000)
               and Q(335,1000)<=Q(tp,tp+fp)<Q(345,1000)
               and Q(995,1000)<=Q(tn,tn+fn)<=1):
                compatible.append({'TP':tp,'FP':fp,'FN':fn,'TN':tn,'unrounded_NPV':float(Q(tn,tn+fn))})
    assert len(compatible)==7 and {x['FN'] for x in compatible}=={26}
    results['li']={'total_records':6331,'reference_positive':113,'reference_negative':6218,'printed_P':0.34,
                  'printed_R':0.77,'printed_NPV':1.00,'compatible_matrices':compatible,
                  'verdict':'SEVEN_INTEGER_STATES_IF_COMMON_REFERENCE; no recovered unpublished matrix or measured labor'}
    return results

def source_gate(dir):
    import fitz
    texts={}
    for label,meta in PUBLISHERS.items():
        p=dir/meta['filename']; assert p.is_file(),p
        assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256'],label
        doc=fitz.open(p)
        texts[label]=[pg.get_text() for pg in doc]
    # evidence exists on exact source page(s) (1 based)
    e={
       'zhang':[(1,'959'),(2,'936'),(2,'959'),(2,'61')],
       'insuk':[(3,'1,648'),(5,'0.0884'),(5,'1684')],
       'cao':[(4,'30 seconds'),(6,'7.56%'),(6,'59.16%'),(7,'17.15')],
       'janoudi':[(3,'perfect'),(4,'3342'),(5,'145'),(5,'221')],
       'li':[(1,'0.77'),(3,'113'),(3,'6218'),(5,'94 %')]
    }
    for k,v in e.items():
        for page,needle in v:
            t=texts[k][page-1].replace('\n','')
            assert needle.lower() in t.lower(),(k,page,needle)
    return {k:{'sha256':PUBLISHERS[k]['sha256'],'doi':PUBLISHERS[k]['doi'],
               'pages_checked':PUBLISHERS[k]['pages'],'source_verification':'SHA256_AND_ORIGINAL_PDF_PAGE_TEXT_PASS'} for k in PUBLISHERS}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',default=None);ap.add_argument('--out',required=True);args=ap.parse_args()
 o={'project':'99a','version':'R45','type':'original_source_independent_arithmetic_recheck',
    'record_level_model_rerun':False,'new_human_review':False,'conditional_cases':independent_arithmetic()}
 if args.source_dir: o['original_pdf_checks']=source_gate(Path(args.source_dir))
 else:o['original_pdf_checks']='NOT_RUN_IN_ARITHMETIC_ONLY_MODE'
 Path(args.out).write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(json.dumps({'status':'PASS','cases':len(o['conditional_cases']),'source_PDF_checks':len(o['original_pdf_checks']) if isinstance(o['original_pdf_checks'],dict) else 0,
  'li_compatible_matrices':len(o['conditional_cases']['li']['compatible_matrices'])},ensure_ascii=False))
