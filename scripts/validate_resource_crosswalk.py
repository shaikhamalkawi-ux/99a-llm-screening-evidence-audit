#!/usr/bin/env python3
"""Validate the R24 interpretive crosswalk against the R23 public 60-candidate gate.

Source-note coding is a disclosed author classification, not a fresh re-extraction of
49 publisher articles or evidence that missing outcomes are absent from sources.
"""
import collections
import csv
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
EXPECTED={
 'OBSERVED_ASSISTED_VS_UNASSISTED_TASK':1,
 'OBSERVED_ABSTRACT_REPRESENTATION_TASK':1,
 'OBSERVED_HUMAN_ONLY_WORKFLOWS':1,
 'OBSERVED_HUMAN_VS_MACHINE_RUNTIME':3,
 'CALENDAR_ELAPSED_VS_MACHINE_RUNTIME':2,
 'NO_ASSISTED_HUMAN_CONTRAST_DOCUMENTED_IN_R20_SOURCE_NOTE':41,
}
IDS={
 'OBSERVED_ASSISTED_VS_UNASSISTED_TASK':{'LIT-020'},
 'OBSERVED_ABSTRACT_REPRESENTATION_TASK':{'LIT-048'},
 'OBSERVED_HUMAN_ONLY_WORKFLOWS':{'LIT-009'},
 'OBSERVED_HUMAN_VS_MACHINE_RUNTIME':{'LIT-016','LIT-027','LIT-045'},
 'CALENDAR_ELAPSED_VS_MACHINE_RUNTIME':{'LIT-041','LIT-043'},
}

def records(file):
 with (DATA/file).open(encoding='utf-8-sig',newline='') as f:
  return list(csv.DictReader(f))

def verify():
 cross=records('source_claim_timing_crosswalk_49.csv')
 candidates=records('candidate_source_gates_60.csv')
 assert len(cross)==49 and len({r['candidate_id'] for r in cross})==49
 assert len(candidates)==60 and len({r['candidate_id'] for r in candidates})==60
 lookup={r['candidate_id']:r for r in candidates}
 for row in cross:
  ref=lookup[row['candidate_id']]
  assert ref['provisional_evidence_role'] in {'EMPIRICAL_PROVISIONAL','CONTEXT_PROVISIONAL'}
  assert ref['doi'].casefold()==row['doi'].casefold()
  assert ref['original_source_url']==row['original_evidence_url']
  assert row['r20_resource_note_label'].strip()
  assert row['source_trace_locator'].strip()
  assert row['claim_boundary'].strip()
 source_ids={r['candidate_id'] for r in candidates if r['provisional_evidence_role'] in {'EMPIRICAL_PROVISIONAL','CONTEXT_PROVISIONAL'}}
 assert {r['candidate_id'] for r in cross}==source_ids
 counts=collections.Counter(r['timing_contrast_code'] for r in cross)
 assert counts==EXPECTED,(counts,EXPECTED)
 for code,expected in IDS.items():
  actual={r['candidate_id'] for r in cross if r['timing_contrast_code']==code}
  assert actual==expected,(code,actual,expected)
 # These counts are frozen descriptive tags on R20 source notes, not
 # independent final eligibility decisions, trial counts or prevalence estimates.
 return {'ok':True,'source_notes_coded':len(cross),'source_roles':dict(collections.Counter(r['source_role'] for r in cross)),
         'resource_note_categories':dict(counts),'scope':'R20-frozen source notes; not completed review inclusion'}

if __name__=='__main__':print(json.dumps(verify(),indent=2,sort_keys=True))
