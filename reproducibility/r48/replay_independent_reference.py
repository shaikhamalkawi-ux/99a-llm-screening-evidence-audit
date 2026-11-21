#!/usr/bin/env python3
"""99a: deterministic retrospective pair replay on frozen Mortensen source files.

Python 3.10+ standard library only. Original votes are read, never overwritten.
Expected confusion counts are rational item weights, not observed integer counts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from fractions import Fraction as F
from pathlib import Path
from urllib.request import urlopen

REVIEWS = ("Appendicitis", "DST", "Omega3", "ProtonBeam")
CONTROLS = {"Appendicitis": (1664, 242), "DST": (8071, 183),
            "Omega3": (5774, 310), "ProtonBeam": (4749, 243)}
NUMBER_QUESTION = {"Appendicitis": "Question2", "ProtonBeam": "Question4"}
NUMERIC = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", re.ASCII)
POLICIES = ("single", "AND", "OR", "ideal_disagreement_review")
MISSING_MODES = ("omit", "exclude", "retain")


def json_write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def verify_sources(source_dir, manifest, download=False):
    required = {f"{r}{s}" for r in REVIEWS for s in (".csv", "_processing.r")}
    seen = set()
    checked = []
    for item in manifest["files"]:
        name = Path(item["path"]).name
        if name not in required:
            continue
        path = source_dir / name
        if download and not path.exists():
            with urlopen(item["source_url"], timeout=60) as response:
                content = response.read()
            path.write_bytes(content)
        content = path.read_bytes()
        sha256 = hashlib.sha256(content).hexdigest()
        git_sha1 = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        assert len(content) == item["size"], f"Size mismatch: {name}"
        assert sha256 == item["sha256"], f"SHA256 mismatch: {name}"
        assert git_sha1 == item["sha"], f"Git blob mismatch: {name}"
        checked.append({"path": item["path"], "size": len(content), "sha256": sha256,
                        "git_blob_sha1": git_sha1, "verified": True})
        seen.add(name)
    assert seen == required, f"Missing manifest entries: {sorted(required - seen)}"
    return checked


def author_exclusions(script):
    match = re.search(r"WorkerId\s*%in%\s*c\(([^)]*)\)", script)
    assert match, "Frozen source script has no identifiable worker exclusion list"
    return set(re.findall(r'"([^"\n]+)"', match.group(1)))


def criterion(value, numeric=False):
    # Surrounding whitespace is immaterial. Internal characters are not repaired.
    value = value.strip()
    if not numeric:
        return {"Yes": 1, "CantTell": 1, "No": 0}.get(value)
    if value == "NoInfo":
        return 1
    if not NUMERIC.fullmatch(value):
        return None
    try:
        number = Decimal(value)
        return int(number >= 10) if number.is_finite() else None
    except InvalidOperation:
        return None


def worker_decision(row, review, question_names):
    answers = [criterion(row[q], q == NUMBER_QUESTION.get(review)) for q in question_names]
    if 0 in answers:
        return 0
    if all(answer == 1 for answer in answers):
        return 1
    return None


def source_cubes(source_dir, review):
    with (source_dir / f"{review}.csv").open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        question_names = [q for q in reader.fieldnames if q.startswith("Question")]
        raw = list(reader)
    ordinary = [r for r in raw if r.get("Honeypot", "0") == "0"]
    assert all(r.get("Honeypot", "0") in ("0", "1") for r in raw)
    blacklist = author_exclusions((source_dir / f"{review}_processing.r").read_text())
    refs = defaultdict(set)
    pmids = defaultdict(set)
    seen = set()
    for row in ordinary:
        assert row["Relevant"] in ("0", "1")
        refs[row["AbstractId"]].add(int(row["Relevant"]))
        pmids[row["AbstractId"]].add(row["PMID"])
        key = (row["AbstractId"], row["WorkerId"])
        assert key not in seen, f"Duplicate worker/item: {review} {key}"
        seen.add(key)
    assert all(len(v) == 1 for v in refs.values()), f"Inconsistent reference: {review}"
    assert all(len(v) == 1 for v in pmids.values()), f"Inconsistent PMID: {review}"
    original_n = len(refs)
    original_p = sum(next(iter(v)) for v in refs.values())
    assert (original_n, original_p) == CONTROLS[review], f"Paper control mismatch: {review}"
    audit = {"raw_rows": len(raw), "honeypot_rows_removed": len(raw) - len(ordinary),
             "ordinary_records": original_n, "ordinary_reference_positives": original_p,
             "duplicate_worker_item_rows": 0, "reference_conflicts": 0, "pmid_conflicts": 0,
             "source_blacklist_size": len(blacklist), "filters": {}}
    cubes = {}
    for filter_name in ("author_filter", "all_workers"):
        selected = [r for r in ordinary if filter_name == "all_workers" or r["WorkerId"] not in blacklist]
        groups = defaultdict(list)
        for row in selected:
            groups[row["AbstractId"]].append(worker_decision(row, review, question_names))
        counts = Counter()
        unknown_gold = Counter()
        valid_votes = 0
        for item, decisions in groups.items():
            y = next(iter(refs[item]))
            p = decisions.count(1)
            n = decisions.count(0)
            u = decisions.count(None)
            counts[(y, p, n, u)] += 1
            unknown_gold[y] += u
            valid_votes += p + n
        cubes[filter_name] = [dict(reference=y, include=p, exclude=n, unresolved=u, records=count)
                              for (y, p, n, u), count in sorted(counts.items())]
        audit["filters"][filter_name] = {
            "rows": len(selected), "workers": len({r["WorkerId"] for r in selected}),
            "records": len(groups), "records_removed": original_n - len(groups),
            "reference_positives": sum(next(iter(refs[i])) for i in groups),
            "source_blacklist_rows_removed": len(ordinary) - len(selected),
            "interpretable_votes": valid_votes,
            "unresolved_votes": sum(unknown_gold.values()),
            "unresolved_votes_by_reference": dict(unknown_gold),
            "votes_per_record": dict(sorted(Counter(len(v) for v in groups.values()).items())),
            "valid_votes_per_record": dict(sorted(Counter(sum(d is not None for d in v) for v in groups.values()).items()))
        }
    return cubes, audit


def rational(value):
    value = F(value)
    return {"exact": str(value), "value": float(value)}


def rate(numerator, denominator):
    return rational(F(numerator) / denominator) if denominator else None


def summarize(cube, missing_mode):
    matrices = {name: {k: F(0) for k in ("TP", "FP", "FN", "TN")} for name in POLICIES}
    disagreement = {0: F(0), 1: F(0)}
    cohort_n = cohort_p = pair_count = dropped_n = dropped_p = 0
    all_negative_positive = all_positive_negative = no_unknown_n = 0
    positive_with_negative_pair = negative_with_positive_pair = 0
    for row in cube:
        y, p, n, u, count = (row[k] for k in ("reference", "include", "exclude", "unresolved", "records"))
        original_u = u
        if missing_mode == "exclude":
            n += u
        elif missing_mode == "retain":
            p += u
        total = p + n
        if total < 2:
            dropped_n += count
            dropped_p += y * count
            continue
        pairs = math.comb(total, 2)
        both_positive = F(math.comb(p, 2), pairs)
        both_negative = F(math.comb(n, 2), pairs)
        differ = F(p * n, pairs)
        assert both_positive + both_negative + differ == 1
        predicted_positive = {
            "single": F(p, total), "AND": both_positive,
            "OR": 1 - both_negative,
            "ideal_disagreement_review": both_positive + y * differ
        }
        for policy, probability in predicted_positive.items():
            matrix = matrices[policy]
            matrix["TP" if y else "FP"] += count * probability
            matrix["FN" if y else "TN"] += count * (1 - probability)
        disagreement[y] += count * differ
        cohort_n += count
        cohort_p += y * count
        pair_count += count * pairs
        positive_with_negative_pair += count * int(y == 1 and n >= 2)
        negative_with_positive_pair += count * int(y == 0 and p >= 2)
        if original_u == 0:
            no_unknown_n += count
            all_negative_positive += count * int(y == 1 and p == 0)
            all_positive_negative += count * int(y == 0 and n == 0)
    output = {}
    for policy, matrix in matrices.items():
        tp, fp, fn, tn = (matrix[k] for k in ("TP", "FP", "FN", "TN"))
        assert tp + fn == cohort_p and fp + tn == cohort_n - cohort_p
        output[policy] = {
            "expected_counts": {k: rational(v) for k, v in matrix.items()},
            "recall": rate(tp, tp + fn), "precision": rate(tp, tp + fp),
            "specificity": rate(tn, tn + fp), "retained_fraction": rate(tp + fp, cohort_n)
        }
    # Structural identities verify routing arithmetic; the empirical counts are separate.
    assert matrices["AND"]["TP"] <= matrices["single"]["TP"] <= matrices["OR"]["TP"]
    assert matrices["ideal_disagreement_review"]["FN"] == matrices["OR"]["FN"]
    assert matrices["ideal_disagreement_review"]["FP"] == matrices["AND"]["FP"]
    return {
        "records": cohort_n, "reference_positives": cohort_p,
        "pair_combinations_not_independent_n": pair_count,
        "items_with_fewer_than_two_usable_votes": dropped_n,
        "positives_with_fewer_than_two_usable_votes": dropped_p,
        "disagreement_expected_records": rational(disagreement[0] + disagreement[1]),
        "disagreement_fraction": rate(disagreement[0] + disagreement[1], cohort_n),
        "disagreement_expected_reference_positive_records": rational(disagreement[1]),
        "disagreement_expected_reference_negative_records": rational(disagreement[0]),
        "observed_shared_error_diagnostics": {
            "reference_positive_items_with_at_least_one_false_excluding_pair": positive_with_negative_pair,
            "reference_negative_items_with_at_least_one_false_retaining_pair": negative_with_positive_pair,
            "items_without_unresolved_votes": no_unknown_n,
            "unanimous_false_exclusion_items_without_unresolved_votes": all_negative_positive,
            "unanimous_false_retention_items_without_unresolved_votes": all_positive_negative
        },
        "policies": output
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("source_manifest.json"))
    parser.add_argument("--download", action="store_true", help="Download missing pinned inputs from public source URLs")
    args = parser.parse_args()
    args.source_dir.mkdir(parents=True, exist_ok=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.manifest.read_text())
    verified = verify_sources(args.source_dir, manifest, args.download)
    cubes, audit, results = {}, {}, {}
    for review in REVIEWS:
        cubes[review], audit[review] = source_cubes(args.source_dir, review)
        results[review] = {
            "role": "pilot_descriptive_only" if review == "ProtonBeam" else "primary",
            "variants": {f"{filter_name}__unknown_{missing}": summarize(cube, missing)
                         for filter_name, cube in cubes[review].items() for missing in MISSING_MODES}
        }
    result = {"source_commit": manifest["commit"],
              "reference_stage": "title_abstract",
              "estimand": "equal item-weight expectation over all available distinct-worker unordered pairs",
              "counts_are": "exact rational expectations, not realized integer observations",
              "reviews": results}
    json_write(args.out_dir / "decision_cubes.json", cubes)
    json_write(args.out_dir / "source_integrity.json", {"verified_inputs": verified, "reviews": audit})
    json_write(args.out_dir / "results.json", result)
    for name, item in results.items():
        r = item["variants"]["author_filter__unknown_omit"]
        simple = {"review": name, "n": r["records"], "positives": r["reference_positives"],
                  "disagreement_pct": 100 * r["disagreement_fraction"]["value"],
                  "shared_error_diagnostics": r["observed_shared_error_diagnostics"]}
        simple["policies"] = {p: {"expected_counts": {k: v["exact"] for k, v in o["expected_counts"].items()},
                                  "recall_pct": 100 * o["recall"]["value"],
                                  "precision_pct": 100 * o["precision"]["value"]}
                              for p, o in r["policies"].items()}
        print(json.dumps(simple))


if __name__ == "__main__":
    main()
