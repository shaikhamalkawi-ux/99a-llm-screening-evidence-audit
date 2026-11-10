# R36: Exact joint-target feasibility from Janoudi's simulated review queues

**Status (10 November 2026):** new *post-hoc mathematical source-linked reanalysis*, not a human study, human-error probability, predictive model, or inference about true reviewer skill. R35 remains an unmodified prior public release.

Original source: Janoudi et al., *Value in Health* 28(11):1630–1636 (2025), DOI https://doi.org/10.1016/j.jval.2025.09.008, printed Tables 2 and 4. Source baseline: (TP,FN,FP,TN) = (284,3,167,3342); N=3796. Reported simulated human-review queues contain (C,T)=(102,43) for 145 flagged Includes and (135,86) for 221 flagged Includes. This project does not access individual decisions, re-run the Loon Lens platform, or observe human correction.

Let x be corrected false Includes and y incorrectly excluded true Includes. Under a fixed reference, one-pass Include-to-Exclude overrides, and no action on predicted Excludes, the matrix becomes (284-y,3+y,167-x,3342+x) with 0<=x<=C and 0<=y<=T. Then P=(284-y)/(451-x-y), R=(284-y)/287. For any target p>0, r>=0, a pair is feasible if and only if

`0<=y<=min(T,floor(284-287r))` and `max(0,ceil(451 - 284/p + (1-p)y/p))<=x<=C`.

If the upper y bound is negative, no pair qualifies. The result follows by multiplication of positive denominators and integer rounding; it is not a novel estimator or original theory of precision-recall tradeoffs. Strict P improvement against the original classifier is equivalent to `284*x>167*y`, while exact preservation of its recall requires `y=0`.

## Verified results

| Source policy | P>=80%, R>=98% | P>=85%, R>=98% | P>=90%, R>=98% | Total policy-tagged count states |
|---|---:|---:|---:|---:|
| 145 flagged Includes | 19 | 0 | 0 | 4,532 |
| 221 flagged Includes | 118 | 55 | 0 | 11,832 |

At R>=98%, y can only equal 0, 1 or 2. For P>=80%, minimum x is 96, 97, 97 respectively. For P>=85%, in the larger policy minimum x is 117,118,118. The 16,364 total counts policy-tagged (policy,x,y) states. Since the 145-policy rectangle is a subset of the 221-policy rectangle, there are only 11,832 *distinct* untagged confusion matrices. These counts are **not frequencies, probabilities, success rates or confidence bounds**.

For a nested expansion from 145 to 221 flags, there are 33 extra false Includes and 43 extra true Includes. If all 145 shared records receive the same decisions under both policies and additional actions are (dx,dy), higher precision from the expansion is equivalent to `(284-y)*dx>(167-x)*dy`. For illustration, after perfect correction of the first queue, additionally repairing all 33 false Includes and wrongly reversing all 43 new true Includes raises precision from 81.3754% to 88.2784% while recall falls from 98.9547% to 83.9721%. This is hypothetical. In the extreme (x,y)=(135,86) within the 221-policy, precision=86.0870% and recall=68.9895%. It is not asserted probable or plausible.

## Reproduction and falsification

`python scripts/check_r36_joint_certificates.py` generates `data/R36_JointThreshold_Certificates.json` and `data/R36_JointTarget_Counts.csv`. It checks all attainable integer pairs by exact Fraction arithmetic against the closed-form target inequalities. `python -m unittest discover -s tests -v` includes R36 test cases. A new source reference, independently adjudicated participant decisions, actual time logs, rescue review of previously Excluded records, different cohort, or another policy could change or invalidate these exact source-specific statements. They cannot support net person-time claims or a claim that human review empirically reduces recall.
