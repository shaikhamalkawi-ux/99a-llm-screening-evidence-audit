"""Source-only integer checks on Insuk et al. (2025), journal pp. 3 and 5.

Not a rerun of any LLM, and not a verdict of author error. The numerator
and denominator reconstruction is conditional on the printed Table 1
classification counts and the experienced-researcher reference.
"""
from pathlib import Path
from fractions import Fraction
import csv,json
P=Path(__file__).resolve().parents[1] / 'data' / 'insuk_2025_reported_title_screening.csv'
def audit():
    with P.open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
    assert len(rows)==3 and {r['screener'] for r in rows}=={'Junior reviewers','ChatGPT','Claude'}
    out=[]
    for r in rows:
        N=int(r['screened_n_body_table1'])
        H=int(r['table3_heading_n']);Rneg=int(r['reference_excluded_n']);PredNeg=int(r['screener_excluded_n'])
        assert N==1648 and H==1684 and Rneg==1615
        positive=N-Rneg
        rrec=float(r['reported_recall']); rprec=float(r['reported_precision'])
        poss=[tp for tp in range(positive+1) if abs(tp/positive-rrec)<.00006]
        assert len(poss)==1
        tp=poss[0];fn=positive-tp
        predpos=N-PredNeg
        fp=predpos-tp;tn=Rneg-fp
        assert min(tp,fn,fp,tn)>=0 and tp+fn+fp+tn==N
        measures={
            'accuracy':Fraction(tp+tn,N), 'recall':Fraction(tp,positive),
            'precision':Fraction(tp,tp+fp), 'npv':Fraction(tn,tn+fn),
            'fpr':Fraction(fp,fp+tn)}
        for k in ('accuracy','recall','precision','npv'):
            assert abs(float(measures[k])-float(r['reported_'+k]))<=.00011,(r['screener'],k)
        # Published FPR does not match the standard FP/(FP+TN) using the above source counts.
        assert abs(float(measures['fpr'])-float(r['reported_fpr']))>.001
        out.append({'screener':r['screener'],'source_total_body_table1':N,
                    'source_total_table3_heading':H,'TP':tp,'FN':fn,'FP':fp,'TN':tn,
                    'reconstructed_fpr':round(float(measures['fpr']),4),
                    'published_fpr':r['reported_fpr']})
    return {'ok':True,'source_doi':'10.1007/s10916-025-02246-4',
            'conditional_reconstruction':True,'no_proven_author_error':True,'results':out}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
