#!/usr/bin/env python3
"""Independently verify the saved-output agreement audit, using recordwise Boolean counts.
Third-party source outputs are fetched transiently, never distributed.
"""
import csv, gzip, hashlib, io, itertools, json, urllib.request
from collections import defaultdict
from pathlib import Path

ROOT='https://raw.githubusercontent.com/matsuikentaro1/jev-title-abstract-screening/d911eafc5299aa3ca41a6aacf0167931c81fcbbc/'
SHA={
 'data/records.csv':'4287fa288b91e1e4d8b7d990f8df9bc4b3d954de86cfcf03623dc4d89b281dcb',
 'data/predictions.csv.gz':'3ac88823815ed659bac2fb803a2b89334561b2ffd1fb80620e4f32f59fa5444c',
 'data/runs.json':'1d8c2fc79610a0e8532dfb7df36044c6d7f7c2be769172fb2d1b8049720c8cc3',
 'configuration/included_reports.json':'ed54c5f146c739872609334b96ca93d6b935186ed744ebc29b08efcde84f8db4'
}
def get(path):
 req=urllib.request.Request(ROOT+path,headers={'User-Agent':'99a-independent-verification/1.0'})
 with urllib.request.urlopen(req,timeout=90) as handle: raw=handle.read()
 assert hashlib.sha256(raw).hexdigest()==SHA[path]
 return gzip.decompress(raw) if path.endswith('.gz') else raw

def csvrows(name): return list(csv.DictReader(io.StringIO(get(name).decode('utf8'))))

def run():
 records=csvrows('data/records.csv')
 runs=json.loads(get('data/runs.json'))
 predictions=csvrows('data/predictions.csv.gz')
 included=json.loads(get('configuration/included_reports.json'))
 assertion=json.loads(Path('external_consensus_results.json').read_text())
 assert len(records)==4527 and len(predictions)==267093
 label={x['record_id']:int(x['reference_retained']) for x in records}
 dataset={x['record_id']:x['dataset'] for x in records}
 final_ids=set(x for entry in included for x in entry['record_ids'])
 group=defaultdict(list)
 for r in runs: group[r['condition']].append((int(r['rep']),r['run_id']))
 votes=defaultdict(dict)
 for p in predictions:
  v=(float(p['probability_retained'])>=.5) if p['probability_retained'] else p['decision']=='I'
  votes[p['record_id']][p['run_id']]=int(v)
 assert len(votes)==4527 and all(len(v)==59 for v in votes.values())
 def profile(keys,cohort):
  universe=[i for i in label if dataset[i]==cohort]
  blind=sum(label[i] for i in universe if sum(votes[i][k] for k in keys)==0)
  uncertain=sum(0<sum(votes[i][k] for k in keys)<len(keys) for i in universe)
  auto_neg=sum(sum(votes[i][k] for k in keys)==0 for i in universe)
  final_blind=sum(i in final_ids for i in universe if sum(votes[i][k] for k in keys)==0)
  return (blind,uncertain,auto_neg,final_blind)

 checks=0
 for entry in assertion['first_three_rows']:
  names=[p for _,p in sorted(group[entry['condition']])][:3]
  q=profile(names,entry['dataset'])
  expected=(entry['all_negative_reference_positives'],entry['human_review_disagreements'],entry['automatic_negative_records'],entry['source_final_included_all_negative'])
  assert q==expected,(entry['condition'],entry['dataset'],q,expected)
  checks+=1

 ensembles=[
  ('mixed_jev_choice_gpt5_default_gpt6_default',('choice-v4','gpt-5-mini-default','gpt-6-astra-default')),
  ('three_llm_configs_gpt5_minimal_default_gpt6',('gpt-5-mini-minimal','gpt-5-mini-default','gpt-6-astra-default'))
 ]
 new=[]
 for name,conditions in ensembles:
  all_choices=[[r for _,r in sorted(group[c])] for c in conditions]
  combos=list(itertools.product(*all_choices))
  for cohort in ('takeshima','maruki'):
   profiles=[profile(keys,cohort) for keys in combos]
   row={'ensemble':name,'cohort':cohort,'n_run_combinations':len(combos),
        'blindspot_reference_positive_first':profiles[0][0],
        'blindspot_reference_positive_min':min(x[0] for x in profiles),
        'blindspot_reference_positive_max':max(x[0] for x in profiles),
        'combinations_with_blindspot':sum(x[0]>0 for x in profiles),
        'human_disagreement_first':profiles[0][1],
        'human_disagreement_min':min(x[1] for x in profiles),
        'human_disagreement_max':max(x[1] for x in profiles),
        'final_included_blindspot_first':profiles[0][3],
        'final_included_blindspot_max':max(x[3] for x in profiles)}
   new.append(row)
   print('MIXED_ROW '+json.dumps(row,sort_keys=True))
 final_coverage=[]
 for condition in ('choice-v4','gpt-6-astra-default','gpt-5-mini-default','gpt-5-mini-minimal'):
  for repetition,run_id in sorted(group[condition]):
   missing_ids=sorted(i for i in final_ids if not votes[i][run_id])
   missing_reports=sum(all(not votes[i][run_id] for i in entry['record_ids']) for entry in included)
   c={'condition':condition,'repetition':repetition,'n_final_report_record_ids':len(final_ids),
      'n_missing_final_report_record_ids':len(missing_ids),
      'n_missing_reports':missing_reports,
      'missing_record_ids':missing_ids}
   final_coverage.append(c)
   print('COVERAGE_WITNESS '+json.dumps(c,sort_keys=True))
 result={'independent_boolean_verifications':checks,'distinct_screening_conditions':len(group),
         'source_checksum_verified':True,'cross_condition_rows':new, 'per_run_final_coverage':final_coverage,
         'source_stage':'Human-retained for full-text assessment, not full true-eligibility reference',
         'uncertainty_note':'Run combinations reuse the same model outputs and original records; range endpoints are not independent samples.'}
 Path('external_independent_verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('INDEPENDENT_VERIFY_PASS '+json.dumps({'rows':checks,'mixed_rows':len(new),'records':len(records),'predictions':len(predictions)}))

if __name__=='__main__':run()
