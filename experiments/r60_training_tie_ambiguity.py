#!/usr/bin/env python3
"""Exact tie-set ambiguity in cross-review transfer, source-pinned R60.

All portfolios of k=1..3 saved run vectors are enumerated. Among those with
maximum retained *training* H positives and minimum *training* forwarded records,
compute the full RANGE of outcomes on the other review. No test labels are used
to select/tie-filter a portfolio. This is within-archive retrospective transport,
not new deployment evidence or an independently sampled trial.
"""
import csv, gzip, hashlib, io, itertools, json, math, urllib.request
from collections import Counter
from pathlib import Path
PIN='d911eafc5299aa3ca41a6aacf0167931c81fcbbc'
ROOT=f'https://raw.githubusercontent.com/matsuikentaro1/jev-title-abstract-screening/{PIN}/'
HASH={
'data/records.csv':'4287fa288b91e1e4d8b7d990f8df9bc4b3d954de86cfcf03623dc4d89b281dcb',
'data/predictions.csv.gz':'3ac88823815ed659bac2fb803a2b89334561b2ffd1fb80620e4f32f59fa5444c',
'data/runs.json':'1d8c2fc79610a0e8532dfb7df36044c6d7f7c2be769172fb2d1b8049720c8cc3',
'configuration/included_reports.json':'ed54c5f146c739872609334b96ca93d6b935186ed744ebc29b08efcde84f8db4'}
def source(p):
 req=urllib.request.Request(ROOT+p,headers={'User-Agent':'99a-r60-training-tie-exactness'})
 with urllib.request.urlopen(req,timeout=90) as f:b=f.read()
 assert hashlib.sha256(b).hexdigest()==HASH[p],p
 return gzip.decompress(b) if p.endswith('.gz') else b
def rows(p):return list(csv.DictReader(io.StringIO(source(p).decode('utf-8'))))
def main():
 records=rows('data/records.csv');predictions=rows('data/predictions.csv.gz');runs=json.loads(source('data/runs.json'))
 assert len(records)==4527 and len(predictions)==267093 and len(runs)==59
 finalreports=json.loads(source('configuration/included_reports.json'))
 indexes={r['record_id']:j for j,r in enumerate(records)}
 runnames=sorted(r['run_id'] for r in runs);runindex={r:i for i,r in enumerate(runnames)}
 masks=[0]*59;seen=Counter()
 for r in predictions:
  i=runindex[r['run_id']];j=indexes[r['record_id']];seen[(i,j)]+=1
  inc=(float(r['probability_retained'])>=.5) if r['probability_retained'] else (r['decision']=='I')
  if inc:masks[i]|=1<<j
 assert len(seen)==267093 and all(v==1 for v in seen.values())
 def select(predicate):return sum(1<<i for i,r in enumerate(records) if predicate(r))
 U={c:select(lambda r:r['dataset']==c) for c in ('takeshima','maruki')}
 H={c:select(lambda r:r['dataset']==c and r['reference_retained']=='1') for c in U}
 F={c:sum(1<<indexes[i] for e in finalreports if e['dataset']==c for i in e['record_ids']) for c in U}
 assert [(U[c].bit_count(),H[c].bit_count(),F[c].bit_count()) for c in U]==[(1381,26,12),(3146,87,11)]
 records_out=[]
 for k in (1,2,3):
  for training,test in (('takeshima','maruki'),('maruki','takeshima')):
   best_h=-1;best_w=10**9;equal=[];all_primary_ties=0
   # lexicographic: maximum training reference positives, then minimum training forwards.
   for combo in itertools.combinations(range(59),k):
    union=0
    for i in combo:union|=masks[i]
    nh=(union&H[training]).bit_count();nw=(union&U[training]).bit_count()
    if nh>best_h:
     best_h=nh;best_w=nw;equal=[(combo,union)];all_primary_ties=1
    elif nh==best_h:
     all_primary_ties+=1
     if nw<best_w:best_w=nw;equal=[(combo,union)]
     elif nw==best_w:equal.append((combo,union))
   assert equal
   evals=[{'heldout_h':(union&H[test]).bit_count(),'heldout_forwarded':(union&U[test]).bit_count(),'heldout_f':(union&F[test]).bit_count(),'combo':[runnames[i] for i in combo]} for combo,union in equal]
   min_h=min(e['heldout_h'] for e in evals);max_h=max(e['heldout_h'] for e in evals)
   min_w=min(e['heldout_forwarded'] for e in evals);max_w=max(e['heldout_forwarded'] for e in evals)
   min_f=min(e['heldout_f'] for e in evals);max_f=max(e['heldout_f'] for e in evals)
   low=min((e for e in evals if e['heldout_h']==min_h),key=lambda e:(e['heldout_forwarded'],e['combo']))
   high=min((e for e in evals if e['heldout_h']==max_h),key=lambda e:(e['heldout_forwarded'],e['combo']))
   row={'k':k,'training_review':training,'heldout_review':test,'candidate_portfolios':math.comb(59,k),'primary_max_reference_tied_portfolios':all_primary_ties,'post_tiebreak_equally_training_optimal_portfolios':len(equal),'train_max_h':best_h,'train_h_total':H[training].bit_count(),'train_min_forwarded_given_max_h':best_w,'heldout_h_total':H[test].bit_count(),'heldout_h_min':min_h,'heldout_h_max':max_h,'heldout_forwarded_min':min_w,'heldout_forwarded_max':max_w,'heldout_final_report_count':F[test].bit_count(),'heldout_final_report_id_min':min_f,'heldout_final_report_id_max':max_f,'example_min_h_witness':low,'example_max_h_witness':high,'heldout_h_distribution':dict(sorted(Counter(e['heldout_h'] for e in evals).items()))}
   assert len(evals)<=math.comb(59,k)
   records_out.append(row)
   print('TIE_ROW '+json.dumps(row,sort_keys=True))
 report={'source_commit':PIN,'source_sha256':HASH,'records':4527,'predictions':267093,'run_vectors':59,'selection_constraints':'train H positives and train forwarding only; no heldout labels in selection objective','warning':'Post hoc within a shared source with two reviews and repeated non-independent runs; outcomes are not new model execution, deployment, or human work','rows':records_out}
 Path('r60_training_tie_ambiguity.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print('TIE_PASS '+json.dumps({'rows':len(records_out),'source_verified':True,'max_combinations_per_k':math.comb(59,3)},sort_keys=True))
if __name__=='__main__':main()
