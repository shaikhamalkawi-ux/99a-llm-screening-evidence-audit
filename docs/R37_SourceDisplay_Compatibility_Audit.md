# R37 — Exact rounded-display compatibility audit: two published sources

**Date:** 10 November 2026. **Interpretive status:** original source-conditional integer reanalysis; *not* an experimental model rerun, a human error observation, a Bayesian prior, an error probability, a claim that a source article is wrong, or a new universal rounding theory.

## Research question

Given only final-publisher aggregate counts and published metric display precision, how many integer outcome matrices remain possible under explicitly specified cohort and decision conditions? Can a printed metric uniquely constrain a source's simulated ideal correction, or conceal eligible records missed by a different screening configuration?

## Admitted source inputs

1. **Janoudi et al. (2025)**, *Value in Health* 28(11), 1630–1636, DOI <https://doi.org/10.1016/j.jval.2025.09.008>, Tables 2/4: baseline `(TP,FN,FP,TN)=(284,3,167,3342)`, `N=3796`, 145/221 flagged predicted Includes, ideal correctable FP=102/135, printed hypothetical post-review precisions **81.4%** and **89.9%** (one decimal). The scientific supplement and journal file were already inspected in R29. No predicted Excludes are revisited, reference labels held fixed; the two-axis override model is inherited unchanged from R35/R36.
2. **Li et al. (2026)**, *International Journal of Medical Informatics* 207, 106205, DOI <https://doi.org/10.1016/j.ijmedinf.2025.106205>, final article: 6,331 records; 113 expert-labeled positives and 6,218 negatives; named rule–DeepSeek-R1 Prompt II configuration displays precision 0.34, recall 0.77, NPV 1.00 (two decimals). Crucially, reconstruction is *conditional* on all three displays referring to the **same unweighted 6,331-record population**. This has not been demonstrated from source row-level data.

No current source row, reference count, dataset, study inclusion, or final reported result has been overwritten. R36 remains separately preserved.

## Exact display rule

For nonnegative value `v` printed to `d` decimals as `q`, assume usual nearest rounding and require `q-0.5×10⁻ᵈ ≤ v < q+0.5×10⁻ᵈ` (bounded to `[0,1]` for proportions, allowing `v=1`). For percentages, divide the interval endpoints by 100. All comparisons use exact Python `Fraction`, no floating-point gatekeeping.

### Janoudi: near-ceiling one-decimal precision is identifying **within the fixed grid**

For either simulated review queue, let `x` be corrected originally false Includes and `y` erroneously excluded originally true Includes, with `0≤x≤C` and `0≤y≤T`; the exact precision is `P(x,y)=(284−y)/(451−x−y)`. Since the uncorrected FP count remains positive in both grids, `P` increases with `x` and decreases with `y`. The ideal corner `(C,0)` uniquely maximizes it. Among all **other** possible integer states the maximum precision is `max(P(C−1,0), P(C,1))`.

| Flagged | `(C,T)` | Source display | Display interval (percent) | Ideal exact percent | Best alternative exact percent | Count compatible |
|---:|---:|---:|---:|---:|---:|---:|
| 145 | (102,43) | 81.4% | [81.35,81.45) | 81.375358% | 81.321839% | **1**: `(102,0)` |
| 221 | (135,86) | 89.9% | [89.85,89.95) | 89.873418% | 89.841270% | **1**: `(135,0)` |

Thus the published rounded **simulated** precision values require the perfect-repair corner **if and only if** the declared grid, cohort, metric definition and rounding convention apply. No live human reviewer was observed achieving either value. Neither output is an estimator of probability of perfect human correction.

### Li: an NPV displayed as 1.00 does **not** exclude false negatives

Under the conditional single-cohort interpretation, two-decimal bins are precision `[0.335,0.345)`, recall `[0.765,0.775)` and NPV `[0.995,1]`. Exhaustive integer enumeration permits exactly seven matrices, with `TP=87`, `FN=26`, `FP∈{166,167,168,169,170,171,172}` and `TN=6218−FP`. Their unrounded NPVs lie around 0.99572, all printed as 1.00. The seven matrices are **feasible reconstructions, not claimed actual experiment matrices**. Different evaluation subsets, weighting, metrics defined by averaging or alternate rounding rules would invalidate this reconstruction.

## Scientific interpretation and falsifiers

These contrasting results are a **source-linked application** of elementary integer feasibility, not a new rounding theorem. A high printed one-decimal precision is identifying under the tightly constrained Janoudi policy and close-to-boundary maximum, while two-decimal NPV can hide a nonzero false-negative count in Li's imbalanced corpus. The results show why source denominator, metric, rounding, reference standard, and policy must travel together with the claim. They do not show human fallibility occurred, repair the source publications, estimate net person-minutes, show deployment harm, or give a pooled statement about the screening literature.

Falsifiers: revise the result if original analyses used different cohort sizes, nonstandard rounding, average-of-review metrics rather than pooled counts, moved label boundaries, re-reviewed initial predicted Excludes, or used unequal record weights.

## Reproduction

Run `python scripts/check_r37_display_precision.py` and `python -m unittest discover -s tests -v` in the public source tree. The script writes `data/R37_DisplayCompatibility_Results.json` and `data/R37_DisplayCompatibility_Summary.csv`, with input transcription and limits in `data/R37_SourceDisplay_Inputs.json`. Use `scripts/validate_release.py` for all public-file hashes. Earlier R34/R35/R36 source inputs and outputs remain byte-identical except explicitly authorized metadata, manifest and CI edits, which do not affect historical scientific results.
