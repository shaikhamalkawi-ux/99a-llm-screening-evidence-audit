# R35 — An imperfect-human-override envelope for one published simulation

**Source:** Janoudi et al. (2025), *Value in Health* 28(11):1630–1636, DOI [10.1016/j.jval.2025.09.008](https://doi.org/10.1016/j.jval.2025.09.008). The original article's publisher PDF Table 2 (p. 1633) and Table 4 (p. 1634), plus its Methods (p. 1632), are the recorded inputs. The final journal report and its scientific supplement were retrieved in R29. The original publisher file is **not** redistributed in this public repository.

**Interpretation class:** New, *post hoc*, **deterministic mathematical stress test** based on the source's *printed aggregate numbers*, not a human-observed workflow, an experiment, an estimated human error rate, or a model replication. The source authors' simulation assumes perfect correction of flagged model errors. This R35 test investigates what claims survive if a human reviewer may correct a false Include or wrongly reject a true Include.

## Baseline and policies

Source-published baseline (TP, FN, FP, TN) = (284, 3, 167, 3342), total 3,796; adjudicated true Includes = 287.

* Low/Medium predicted Includes: 145 flagged; perfect repair yields FP=65 and FN=3. Therefore 102 false Includes can be correctly excluded and 43 originally correct Includes in the flagged set can be mistakenly overturned.
* Low/Medium/High predicted Includes: 221 flagged; perfect repair yields FP=32 and FN=3. Therefore 135 correctable false Includes and 86 originally correct Includes.

Under a **fixed reference and fixed source dataset**, the only model decisions changed are flagged predicted Includes, and every human action is either retaining Include or changing it to Exclude. Let `x` be correctly rejected false Includes and `y` be incorrectly rejected true Includes:

`(TP, FN, FP, TN) = (284-y, 3+y, 167-x, 3342+x)`.

Hence `Precision=(284-y)/(451-x-y)`, `Recall=(284-y)/287`, `Accuracy=(3626+x-y)/3796`. For policy-specific `0<=x<=C`, `0<=y<=T`, all integer combinations are attainable by decisions on distinct records; these are **possibilities**, not uniformly distributed or statistically inferred. The two state grids have 4,532 and 11,832 elements (16,364 in total), **not 16,364 observations**.

## Checks against the optimistic case

| Counterfactual state | TP | FN | FP | TN | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 284 | 3 | 167 | 3342 | 62.971% | 98.955% |
| 145 flagged, perfect correction (`x=102,y=0`) | 284 | 3 | 65 | 3444 | 81.375% | 98.955% |
| 145 flagged, all FP repaired but one TP wrongly rejected (`x=102,y=1`) | 283 | 4 | 65 | 3444 | 81.322% | 98.606% |
| 221 flagged, perfect correction (`x=135,y=0`) | 284 | 3 | 32 | 3477 | 89.873% | 98.955% |
| 221 flagged, all FP repaired but one TP wrongly rejected (`x=135,y=1`) | 283 | 4 | 32 | 3477 | 89.841% | 98.606% |

At **zero newly incorrect human overrides** (`y=0`), 96 false Includes need correct reversal to achieve precision at least 80% (96/102=94.1% of the smaller policy's possible corrections); 117 to achieve at least 85%, impossible in the smaller policy. Under the given fixed baseline neither policy achieves 90% even if all its flagged false Includes are correctly reversed. Keeping recall at least 98% requires `y<=2`. To keep **the original exact recall**, `y=0` is necessary because none of the model's baseline false negatives is visited under Include-only review.

## Interpretation and falsifiers

1. These bounds do **not** show that human screeners make mistakes, or the probability of any scenario. A blinded, executed review with decisions and time logs is required to estimate correction rates or net staff-minutes.
2. The source reference is fixed as printed; the exercise neither verifies independent human eligibility nor resolves adjudication error.
3. If reviewers also re-screen predicted Excludes, rescue originally false negatives, change other model actions, or use a different population, the formulas must be rebuilt. They cannot be transported unmodified.
4. Published precision/recovery values remain the authors' original reports. New R35 calculations are always labeled conditional and are not corrections, independent study observations or a proposed universal measurement standard.

## Reproduction

`python scripts/check_r35_imperfect_adjudication.py` produces the R35 JSON and scenario CSV. `python -m unittest discover -s tests -v` checks exact source counts, exhaustive grid sizes, the one-error adverse case, target thresholds, and source labeling. Python standard library only; no data or new participant observations are generated. The locked R20/R28–R34 source files remain unchanged.
