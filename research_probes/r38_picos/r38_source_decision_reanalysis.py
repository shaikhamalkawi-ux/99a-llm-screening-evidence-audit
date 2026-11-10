#!/usr/bin/env python3
"""Independent, source-locked reanalysis of Vallamchetla (2025) reviewer decisions.

Source dataset: 10.17632/4bgt2p5hrd.1, linked article 10.1016/j.jbi.2025.104860.
Record-level reviewer choices are OBSERVED, but consensus and sequential
include-only policies are COUNTERFACTUAL REPLAYS, not executed workflows.
No causal AI treatment effect or net human effort is identified.

The source CSV is intentionally EXCLUDED from public releases. Obtain it via
its official Mendeley page, follow the original CC BY-NC 4.0 license, and run:
  python r38_source_decision_reanalysis.py --source path/to/source.csv --out out/
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from collections import Counter
from itertools import combinations
from pathlib import Path

DATASET_DOI = '10.17632/4bgt2p5hrd.1'
ARTICLE_DOI = '10.1016/j.jbi.2025.104860'
SOURCE_SHA256 = '11e8cba6a21f936253e9a2c85d88b942efcdf5401b1e8b7bf5cbcedd0e851425'
SOURCE_SIZE = 1_963_035
COLS = ('Gold_std dataset', 'A1_reviewer', 'A2_reviewer', 'B1_reviewer', 'B2_reviewer')
REVIEWERS = ('A1', 'A2', 'B1', 'B2')


def metrics(y, pred):
    assert len(y)==len(pred) and len(y)>0
    c=Counter((a,b) for a,b in zip(y,pred))
    tp=c[(1,1)];fp=c[(0,1)];fn=c[(1,0)];tn=c[(0,0)]
    assert tp+fp+fn+tn==len(y)
    return {'tp':tp,'fp':fp,'fn':fn,'tn':tn,
            'precision':tp/(tp+fp) if tp+fp else None,
            'recall':tp/(tp+fn) if tp+fn else None,
            'specificity':tn/(tn+fp) if tn+fp else None,
            'accuracy':(tp+tn)/len(y),
            'f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None}


def parse_source(path):
    path=Path(path)
    source=path.read_bytes()
    sha=hashlib.sha256(source).hexdigest()
    if sha!=SOURCE_SHA256 or len(source)!=SOURCE_SIZE:
        raise ValueError(f'REJECT_SOURCE_IDENTITY: sha256={sha}, bytes={len(source)}')
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not set(COLS).issubset(reader.fieldnames or ()):
            raise ValueError(f'REJECT_MISSING_COLUMNS: {reader.fieldnames}')
        rows=list(reader)
    if len(rows)!=1003:
        raise ValueError(f'REJECT_N: {len(rows)}')
    labels={c:[] for c in COLS}
    for i,row in enumerate(rows):
        for c in COLS:
            v=row[c].strip()
            if v not in ('Include','Exclude'):
                raise ValueError(f'REJECT_LABEL at row {i+2}, field {c}')
            labels[c].append(1 if v=='Include' else 0)
    assert sum(labels['Gold_std dataset'])==25
    return labels,{'file_sha256':sha,'file_size_bytes':len(source),
                   'rows':len(rows),'header':reader.fieldnames}


def analyze(source):
    z,source_info=parse_source(source)
    y=z['Gold_std dataset'];d={r:z[r+'_reviewer'] for r in REVIEWERS}
    errors={r:{i for i,(actual,pred) in enumerate(zip(y,p)) if actual!=pred} for r,p in d.items()}
    false_neg={r:{i for i,(actual,pred) in enumerate(zip(y,p)) if actual and not pred} for r,p in d.items()}
    false_pos={r:{i for i,(actual,pred) in enumerate(zip(y,p)) if not actual and pred} for r,p in d.items()}
    original={r:metrics(y,v) for r,v in d.items()}
    expected={'A1':(25,1,0,977),'A2':(22,7,3,971),
              'B1':(25,1,0,977),'B2':(23,3,2,975)}
    for r,(tp,fp,fn,tn) in expected.items():
        assert (original[r]['tp'],original[r]['fp'],original[r]['fn'],original[r]['tn'])==(tp,fp,fn,tn)
    pairs=[]
    for a,b in combinations(REVIEWERS,2):
        pairs.append({'reviewer_a':a,'reviewer_b':b,
         'decision_disagreements':sum(u!=v for u,v in zip(d[a],d[b])),
         'both_wrong':len(errors[a]&errors[b]),
         'a_only_wrong':len(errors[a]-errors[b]),
         'b_only_wrong':len(errors[b]-errors[a]),
         'overlapping_reference_positive_misses':len(false_neg[a]&false_neg[b]),
         'overlapping_reference_negative_false_includes':len(false_pos[a]&false_pos[b])})
    def combined(a,b,operator):
        pred=[int(bool(u and v)) if operator=='AND' else int(bool(u or v)) for u,v in zip(d[a],d[b])]
        return dict({'first':a,'second':b,'rule':operator,'kind':'POST_HOC_CONSENSUS_REPLAY_NOT_EXECUTED'},**metrics(y,pred))
    consensus=[combined('A1','B1','AND'),combined('A1','B1','OR'),
               combined('A2','B2','AND'),combined('A2','B2','OR')]
    def include_only(base,checker):
        # Deterministically replay checker decisions only on Include decisions
        # originally made by base. Does not assert reviewers actually did this.
        pred=[int(bool(first and second)) for first,second in zip(d[base],d[checker])]
        n_flagged=sum(d[base]);wrong_new=sum(y[i] and d[base][i] and not d[checker][i] for i in range(len(y)))
        corrected_fp=sum(not y[i] and d[base][i] and not d[checker][i] for i in range(len(y)))
        return {'first_stage':base,'hypothetical_checker':checker,'flagged_includes':n_flagged,
                'corrected_false_includes_x':corrected_fp,
                'newly_missed_true_includes_y':wrong_new,
                'kind':'COUNTERFACTUAL_REPLAY_OF_OBSERVED_INDEPENDENT_LABELS_NOT_SEQUENTIAL_HUMAN_WORKFLOW',
                **metrics(y,pred)}
    override=[include_only(x,y0) for x in ('A1','B1') for y0 in ('A2','B2')]
    assert len(errors['A1']&errors['B1'])==0
    assert len(false_neg['A2']&false_neg['B2'])==0
    assert len(set.union(*errors.values()))==15
    assert sum(map(len,errors.values()))==17
    assert [(x['tp'],x['fp'],x['fn']) for x in consensus]==[(25,0,0),(25,2,0),(20,1,5),(25,9,0)]
    assert [(x['tp'],x['fp'],x['fn']) for x in override]==[(22,0,3),(23,0,2),(22,1,3),(23,1,2)]
    return {
        'status':'ADMITTED_PRIMARY_RECORD_LEVEL_REANALYSIS',
        'source_dataset_doi':DATASET_DOI,'article_doi':ARTICLE_DOI,
        'source_url':'https://data.mendeley.com/datasets/4bgt2p5hrd/1',
        'source_file_name':'Screening_articles and decisions.csv',
        'original_dataset_license':'CC BY-NC 4.0',
        'source':source_info,
        'reference_positives':sum(y),'reference_negatives':len(y)-sum(y),
        'directly_observed_reviewer_labels':True,
        'published_reviewer_times_minutes_not_per_record':{'A1':116,'A2':463,'B1':90,'B2':370},
        'reviewer_matrices':original,
        'error_overlap':{'sum_of_reviewer_error_events':17,
                         'distinct_records_with_at_least_one_error':len(set.union(*errors.values())),
                         'assisted_pair_fp_overlap':len(false_pos['A1']&false_pos['B1']),
                         'unassisted_pair_fn_overlap':len(false_neg['A2']&false_neg['B2'])},
        'reviewer_pair_disagreements':pairs,
        'counterfactual_consensus_policies':consensus,
        'counterfactual_include_only_override_policies':override,
        'limitations':[
          'One screened candidate set with 25 reference-included reports; not a representative sample of other systematic reviews.',
          'Reference labels were supplied by source authors, not independently re-adjudicated.',
          'Different people used assisted versus unassisted interfaces and could differ in skill; no causal AI effect is identified.',
          'The AND/OR and sequential override policies are post-hoc recombinations of recorded independent decisions, not actually observed team workflows.',
          'Published 90/116/370/463 minutes are reviewer-wide totals, not recorded verification or sequential consensus time.',
          'No original LLM model was rerun, no randomized intervention, no net labor savings or policy deployment validation.'
        ]
    }


def write_artifacts(data,folder):
    out=Path(folder);out.mkdir(parents=True,exist_ok=True)
    (out/'R38_Primary_Reviewer_Decision_Results.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    datasets=[('R38_Reviewer_Matrices.csv', [{'reviewer':r,**m} for r,m in data['reviewer_matrices'].items()]),
              ('R38_Pairwise_Reviewer_Disagreement.csv',data['reviewer_pair_disagreements']),
              ('R38_Hypothetical_Override_Policies.csv',data['counterfactual_include_only_override_policies']),
              ('R38_PostHoc_Consensus_Policies.csv',data['counterfactual_consensus_policies'])]
    for name, rows in datasets:
        with (out/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    ans=analyze(a.source);write_artifacts(ans,a.out)
    print(json.dumps({'status':ans['status'],'n':ans['source']['rows'],'positives':ans['reference_positives'],
                      'error_records':ans['error_overlap']['distinct_records_with_at_least_one_error'],
                      'override':[(r['first_stage'],r['hypothetical_checker'],r['tp'],r['fp'],r['fn']) for r in ans['counterfactual_include_only_override_policies']]}))
