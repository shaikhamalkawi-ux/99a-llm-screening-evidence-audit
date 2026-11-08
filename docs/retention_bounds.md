# Finite-universe evidence-retention bounds (R25)

This is an elementary **logical partial-identification bound**, not a new effect estimator or a confidence interval. It does **not** certify the reference-standard quality of any original study. No numerical count from a paper is inserted without exact population and source support.

Within one fixed screening stage and fully enumerated candidate set, suppose eligibility has been settled for all retained records and all but `u` excluded records. Let `k` be the number of retained records confirmed eligible, `f` the confirmed eligible records incorrectly excluded, and `u` the number of excluded candidates with unresolved eligibility. Let `z` denote the unknown number of eligible records among `u`, so `0 <= z <= u`. If `k+f>0`,

`R_full(z) = k/(k+f+z)` and `k/(k+f+u) <= R_full <= k/(k+f)`.

**Sharpness:** since `R_full(z)` is nonincreasing in `z`, the two endpoints are attained by all unresolved exclusions being eligible or none being eligible. This applies only under the stated finite-universe and adjudication assumptions.

Important boundary conditions:
- If retained-record eligibility is unverified, the formula does not apply without revising the unknown sets.
- If the candidate pool, review stage, or label reference differs across the numerator, denominator or count `u`, the formula does not apply.
- If `k+f = 0`, the reported verified-reference recall denominator is zero and a recall interval is not defined by this rule.
- The bound is not a sampling confidence interval, does not resolve misclassified adjudicated labels, and does not prove that any screening system achieved the upper endpoint.
- If unverified records have unknown upper count, the bound cannot be calculated.
- These conditions are kept distinct from verification-adjusted *workload* modeling as described by Lai et al. (2026), DOI 10.1017/rsm.2026.10114.

Reproduce software logic using `python -m unittest discover -s tests -v`. All numeric cases in unit tests are artificial arithmetic controls; **they are not study results**.
