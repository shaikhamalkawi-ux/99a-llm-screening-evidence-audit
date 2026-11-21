#!/usr/bin/env python3
"""Compare two separately parsed implementations and enumerate pair arithmetic.

The independent implementation must be run first. This verifier accepts both the
original and portable independent JSON outputs. It never changes the source data.
"""
import argparse
import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--independent", type=Path, required=True)
    args = parser.parse_args()
    own = json.loads((args.results_dir / "results.json").read_text())
    cubes = json.loads((args.results_dir / "decision_cubes.json").read_text())
    other = json.loads(args.independent.read_text())
    variant_map = {"primary": "author_filter__unknown_omit",
                   "unknown_as_0": "author_filter__unknown_exclude",
                   "unknown_as_1": "author_filter__unknown_retain",
                   "no_blacklist": "all_workers__unknown_omit"}
    policy_map = {"single": "single", "AND": "AND", "OR": "OR",
                  "perfect_reference_correction_on_disagreement": "ideal_disagreement_review"}
    counts = {"expected_confusion_cells": 0, "rates": 0, "cohort_and_unanimity_controls": 0,
              "disagreement_controls": 0, "enumerated_cubes": 0}
    for independent_name, root_name in variant_map.items():
        for external in other["variants"][independent_name]["reviews"]:
            name = external["review"]
            root = own["reviews"][name]["variants"][root_name]
            for root_key, external_key in (("records", "eligible_records"),
                                          ("reference_positives", "gold_positive"),
                                          ("pair_combinations_not_independent_n", "raw_unordered_pair_count")):
                assert root[root_key] == external[external_key], (name, root_name, root_key)
                counts["cohort_and_unanimity_controls"] += 1
            for root_key, external_key in (("unanimous_false_exclusion_items_without_unresolved_votes", "FN_count"),
                                          ("unanimous_false_retention_items_without_unresolved_votes", "FP_count")):
                assert root["observed_shared_error_diagnostics"][root_key] == external["unanimous_with_no_unknown"][external_key]
                counts["cohort_and_unanimity_controls"] += 1
            for root_key, external_key in (("disagreement_expected_records", "all"),
                                          ("disagreement_expected_reference_positive_records", "gold_positive"),
                                          ("disagreement_expected_reference_negative_records", "gold_negative")):
                assert F(root[root_key]["exact"]) == F(external["disagreement_mass"][external_key]["fraction"])
                counts["disagreement_controls"] += 1
            for external_policy, root_policy in policy_map.items():
                for cell in ("TP", "FP", "FN", "TN"):
                    assert F(root["policies"][root_policy]["expected_counts"][cell]["exact"]) == F(external["matrices"][external_policy][cell]["fraction"])
                    counts["expected_confusion_cells"] += 1
                for metric in ("recall", "precision", "specificity"):
                    assert F(root["policies"][root_policy][metric]["exact"]) == F(external["metrics"][external_policy][metric]["fraction"])
                    counts["rates"] += 1
    # A separate literal enumeration validates the combinatorial expectation.
    # Repeated rows in a cube are original records; repeated pairs are not new n.
    for name in ("Appendicitis", "DST", "Omega3"):
        matrices = {p: {c: F(0) for c in ("TP", "FP", "FN", "TN")} for p in policy_map.values()}
        for row in cubes[name]["author_filter"]:
            votes = [1] * row["include"] + [0] * row["exclude"]
            if len(votes) < 2:
                continue
            pairs = list(itertools.combinations(votes, 2))
            y = row["reference"]
            for a, b in pairs:
                decisions = {"single": F(a + b, 2), "AND": a & b, "OR": a | b,
                             "ideal_disagreement_review": y if a != b else a}
                for policy, prediction in decisions.items():
                    weight = F(row["records"], len(pairs))
                    matrices[policy]["TP" if y else "FP"] += weight * prediction
                    matrices[policy]["FN" if y else "TN"] += weight * (1 - prediction)
            counts["enumerated_cubes"] += 1
        for policy, matrix in matrices.items():
            expected = own["reviews"][name]["variants"]["author_filter__unknown_omit"]["policies"][policy]["expected_counts"]
            assert all(value == F(expected[cell]["exact"]) for cell, value in matrix.items())
    result = {"status": "all_exact_comparisons_passed", "checks": counts,
              "independent_output_sha256": hashlib.sha256(args.independent.read_bytes()).hexdigest(),
              "independent_means": "Two separately written computational parsers, not independent human adjudication",
              "remaining_limits": ["Fixed original expert title/abstract reference",
                                    "Hypothetical pair selection and disagreement correction",
                                    "Three convenience-sampled reviews from one crowd study",
                                    "No causal person-time or LLM-effect estimate"]}
    (args.results_dir / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
