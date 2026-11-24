#!/usr/bin/env python3
"""R60 independent sets-based verifier for exact portfolio and transfer diagnostics.

Independent algorithm from three primary bitmask implementations: uses literal
sets of source record identifiers and per-run Exclude sets. Checks exhaustive
k=1,2 impossibility, all R60 frontier witnesses, training-only selection and
all post-tiebreak equal-score groups. No raw source is re-published.
"""
import csv, gzip, hashlib, io, itertools, json, math, urllib.request
from collections import defaultdict, Counter
from pathlib import Path
URL='https://raw.githubusercontent.com/matsuikentaro1/jev-title-abstract-screening/d911eafc5299aa3ca41a6aacf0167931c81fcbbc/'
HASH={
'data/records.csv':'4287fa288b91e1e4d8b7d990f8df9bc4b3d954de86cfcf03623dc4d89b281dcb',
'data/predictions.csv.gz':'3ac88823815ed659bac2fb803a2b89334561b2ffd1fb80620e4f32f59fa5444c',
'data/runs.json':'1d8c2fc79610a0e8532dfb7df36044c6d7f7c2be769172fb2d1b8049720c8cc3',
'configuration/included_reports.json':'ed54c5f146c739872609334b96ca93d6b935186ed744ebc29b08efcde84f8db4'}
def load(path):
 req=urllib.request.Request(URL+path,headers={'User-Agent':'99a-independent-R60-scoped-audit'})
 with urllib.request.urlopen(req,timeout=90) as f:b=f.read()
 assert hashlib.sha256(b).hexdigest()==HASH[path]
 return gzip.decompress(b) if path.endswith('.gz') else b
def parse_csv(path):return list(csv.DictReader(io.StringIO(load(path).decode())))
def run():
 records=parse_csv('data/records.csv');predictions=parse_csv('data/predictions.csv.gz');runs=json.loads(load('data/runs.json'));final=json.loads(load('configuration/included_reports.json'))
 assert len(records)==4527 and len(predictions)==267093 and len(runs)==59
 reference={r['record_id'] for r in records if r['reference_retained']=='1'}
 all_ids={r['record_id'] for r in records}
 bytopic={d:{r['record_id'] for r in records if r['dataset']==d} for d in ('takeshima','maruki')}
 final_ids={x for ent in final for x in ent['record_ids']}
 assert len(reference)==113 and len(final_ids)==23 and final_ids<=reference
 runnames=sorted([r['run_id'] for r in runs]);retain=defaultdict(set);seen=defaultdict(set)
 for row in predictions:
  key=row['run_id'];record=row['record_id']
  assert record not in seen[key]
  seen[key].add(record)
  positive=(float(row['probability_retained'])>=0.5) if row['probability_retained'] else row['decision']=='I'
  if positive:retain[key].add(record)
 assert all(seen[r]==all_ids for r in runnames)
 full=set().union(*(retain[n] for n in runnames))
 assert len(reference-full)==1 and len(full)==1002
 def profile(combo,topic):
  selected=set().union(*(retain[n] for n in combo))
  ref=selected & reference & bytopic[topic]
  thru=selected & bytopic[topic]
  return len(ref),len(thru),len(selected&final_ids&bytopic[topic])
 cert=json.loads(Path('r60_oracle_frontier.json').read_text());assert len(cert['frontier'])==3
 for row in cert['frontier']:
  k=row['k'];max_h=-1;min_forward=10**9;best=[]
  for chosen in itertools.combinations(runnames,k):
   selected=set().union(*(retain[n] for n in chosen))
   h=len(selected&reference);forward=len(selected)
   if h>max_h:max_h=h;min_forward=forward;best=[chosen]
   elif h==max_h:
    if forward<min_forward:min_forward=forward;best=[chosen]
    elif forward==min_forward:best.append(chosen)
  assert max_h==row['maximum_human_reference_positives'],(k,max_h,row)
  assert min_forward==row['oracle_minimum_retained_given_maximum_reference_positives']
  assert tuple(row['oracle_witness_run_ids']) in best
  assert row['final_report_ids_in_oracle_witness']==23
  print('INDEPENDENT_ORACLE_ROW '+json.dumps({'k':k,'maximum_H':max_h,'min_forwarded_conditional_on_H':min_forward,'tied_optimizers':len(best)},sort_keys=True))
 assert cert['complete_112_minimum_k_if_le_4']==3
 transfer=json.loads(Path('r60_transfer_diagnostic.json').read_text());tie=json.loads(Path('r60_training_tie_ambiguity.json').read_text())
 assert len(transfer['transfer_rows'])==len(tie['rows'])==6
 validations=[]
 for tr,ta in zip(transfer['transfer_rows'],tie['rows']):
  k=tr['number_of_runs'];train=tr['selection_review'];test=tr['held_out_review']
  assert ta['k']==k and ta['training_review']==train and ta['heldout_review']==test
  best_h=-1;best_forward=10**9;best=[];primary=0
  for chosen in itertools.combinations(runnames,k):
   h,forward,_=profile(chosen,train)
   if h>best_h:best_h=h;best_forward=forward;best=[chosen];primary=1
   elif h==best_h:
    primary+=1
    if forward<best_forward:best_forward=forward;best=[chosen]
    elif forward==best_forward:best.append(chosen)
  assert best_h==ta['train_max_h'] and best_forward==ta['train_min_forwarded_given_max_h']
  assert primary==ta['primary_max_reference_tied_portfolios'] and len(best)==ta['post_tiebreak_equally_training_optimal_portfolios']
  outcomes=[profile(c,test) for c in best]
  assert min(e[0] for e in outcomes)==ta['heldout_h_min'] and max(e[0] for e in outcomes)==ta['heldout_h_max']
  assert min(e[1] for e in outcomes)==ta['heldout_forwarded_min'] and max(e[1] for e in outcomes)==ta['heldout_forwarded_max']
  assert min(e[2] for e in outcomes)==ta['heldout_final_report_id_min'] and max(e[2] for e in outcomes)==ta['heldout_final_report_id_max']
  assert tuple(tr['selected_run_ids']) in best
  h,w,f=profile(tr['selected_run_ids'],test)
  assert h==tr['heldout_retained_source_positives'] and w==tr['heldout_forwarded_records'] and f==tr['heldout_final_report_ids_retained']
  validations.append({'k':k,'train':train,'test':test,'training_ties':len(best),'test_H_range':[ta['heldout_h_min'],ta['heldout_h_max']]})
  print('INDEPENDENT_TRANSFER_ROW '+json.dumps(validations[-1],sort_keys=True))
 out={'status':'PASS','input_SHA_verified':True,'independent_set_based_combinatorial_checks':{'frontier_rows':3,'transfer_rows':6,'tie_rows':6},'oracle_best_k':3,'source_conditional_max_H':112,'global_59_union_forwarded':len(full),'crossreview_rows':validations,'scientific_caveat':'Model run groups and two review populations share source, all run portfolio choices are retrospective, no net human time or external independent cohort.'}
 Path('r60_independent_certificate.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('R60_INDEPENDENT_PASS '+json.dumps({'oracle_rows':3,'transfer_rows':6,'source_4527':True,'source_predictions':267093},sort_keys=True))
if __name__=='__main__':run()
