"""Validate the public R48 derived evidence without original crowdworker rows."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'reproducibility' / 'r48'

class R48PublicOutputs(unittest.TestCase):
    def test_manifest_matches_frozen_source_archive(self):
        manifest = json.loads((DATA / 'SHA256SUMS.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest), 13)
        for name, sha in manifest.items():
            with self.subTest(name=name):
                content = (DATA / name).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), sha)

    def test_aggregate_cross_implementation_enumeration(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            for name in ('results.json','independent_results.json','decision_cubes.json'):
                (p / name).write_bytes((DATA / name).read_bytes())
            run = subprocess.run([sys.executable, str(DATA / 'verify_replay.py'),
                                  '--results-dir', str(p), '--independent', str(p / 'independent_results.json')],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode,0,msg=run.stderr or run.stdout)
            v = json.loads((p / 'verification.json').read_text(encoding='utf-8'))
            frozen = json.loads((DATA / 'verification.json').read_text(encoding='utf-8'))
            self.assertEqual(v, frozen)
            self.assertEqual(v['checks'], {'expected_confusion_cells': 192, 'rates': 144,
                                           'cohort_and_unanimity_controls': 60,
                                           'disagreement_controls':36, 'enumerated_cubes':79})

    def test_source_bound_headline_not_reinterpreted(self):
        f = json.loads((DATA / 'findings.json').read_text(encoding='utf-8'))
        self.assertEqual(f['source_studies'],1)
        self.assertEqual(f['review_datasets'],3)
        self.assertEqual(f['records'],15509)
        self.assertEqual(f['TA_reference_positives'],735)
        self.assertEqual(f['unanimous_false_exclusion_items'],77)
        self.assertEqual(f['unanimous_false_retention_items'],31)
        self.assertAlmostEqual(f['pooled_descriptive_only']['ideal_disagreement_review']['recall_pct'],74.79818594104309)

if __name__ == '__main__': unittest.main()
