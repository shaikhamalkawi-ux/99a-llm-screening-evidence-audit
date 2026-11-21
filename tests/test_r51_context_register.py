"""Verify the bounded R51 literature-context register without external retrieval."""
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'data' / 'R51_2021_2026_Targeted_Citation_Register.csv'
class ContextRegister(unittest.TestCase):
    def test_frozen_context_keys(self):
        with REGISTRY.open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows),15)
        self.assertEqual(len({r['key'] for r in rows}),15)
        self.assertTrue(all(2021 <= int(r['year']) <= 2026 for r in rows))
        self.assertTrue(all(r['doi'] and r['source'].startswith('https://') for r in rows))
        self.assertIn('vandeschoot2021',{r['key'] for r in rows})
        self.assertIn('babaei2026',{r['key'] for r in rows})

if __name__=='__main__': unittest.main()
