# Methodological and source-rights protocol

## Units

- `person_minutes`: directly observed people working on the stated review task.
- `modeled_minutes`: arithmetic derived from assumed per-record rates.
- `decision_count`: number excluded, retained, or routed under a screening policy.
- `machine_runtime_minutes`: processing latency, not person effort.
- `simulated_human_checks`: hypothetical requested reviews under a policy; not executed time.
- `verification_reference`: declared human labels, adjudicated final includes, verified subset, or other source-specific standard.

## The seven claim gates

E01: matched human resource time observed, including later verification, before naming net staff-time saving.
E02: assumed labor rates disclose sensitivity, not observed benefit.
E03: a smaller screening queue is a decision-count result, with separate evidence retention.
E04: simulation of human-in-the-loop intervention does not produce observed human time.
E05: sensitivity on partially verified subsets cannot stand in for full-corpus sensitivity.
E06: shared cohort or versions do not add independent evaluation populations.
E07: do not label a bounded critical review as a systematic review without the complete search and methodology records required for that review type.

## Finite-universe retention bound (R25)

For one fixed candidate universe and screening stage, when eligibility is settled for every retained candidate and every excluded candidate except `u`, let `k` be verified eligible retained and `f` verified eligible incorrectly excluded. Unknown excluded positives `z` satisfy `0 <= z <= u`, so `k/(k+f+u) <= k/(k+f+z) <= k/(k+f)` if `k+f>0`. This is an elementary conditional sharp interval, **not** a confidence interval or a reported effect from any of the reviewed papers. It cannot be applied when matched adjudication counts and a closed candidate universe are absent. The source-specific record still controls claim admission. See `docs/retention_bounds.md`.

## Original work and source versions

Cao preprint and 2025 journal article: same research line, different published numbers. Janoudi preprint and 2025 article: same eight Canada Drug Agency reviews and 3796 citations, but 145/221 simulated checks described in final journal abstract. Zhang short proceedings and journal article share three cohort sizes (865, 959, 73); exact publication relationship not fully verified. Earlier reports are not substitutes for the five missing final full texts.

## Huotala arithmetic

Reported means original 85.95 seconds and simplified 76.26 seconds imply 9.69 seconds; narrative in source reports 9.39 seconds. Preserve both as a source discrepancy. Do not silently edit the source or treat either as review-level net saved staff hours.

## Scientific non-claims

This is not a registered or exhaustive systematic review; the 60 candidates do not define a universe of all LLM screening studies. The record flags reflect source-access assessment. The source-access classifications should not be interpreted as completed eligibility decisions; code checks validate structure and stated conditions, not the truth of all extracted claims. No cross-paper pooled effect is computed.

## Redistribution

No publisher article PDF, subscription copy, downloaded licensed text, personal information beyond published citation metadata, or unpublished private correspondence may be uploaded to the public repo without author/rightsholder authorization and applicable license. Use DOI links in place of article copies. This package makes no assertion about the license status of any individual source. The author must choose the final code/data license before making a formal archival release.

## R24 frozen source-note timing crosswalk

`data/source_claim_timing_crosswalk_49.csv` codes the 49 full-source access notes inherited from R20, and is validated by `scripts/validate_resource_crosswalk.py`. Exactly one note directly describes observed assisted vs unassisted human task minutes (LIT-020); a second is a different abstract-representation experiment (LIT-048). One note concerns human-only timing; three compare human time to machine runtime; two compare elapsed calendar span to runtime; and 41 did not document a matched assisted-human contrast in the *R20 source note*. Those 41 do not prove non-reporting in every full-text article or supplement. The two studies TrialMind and LEADS are outside the frozen 60 register and are not included in these 49 tags. None of the 49 is promoted to final included-study status.

The verification-aware workload metric (VAWR) had already been put forward by Lai et al. (2026), DOI `10.1017/rsm.2026.10114`. Our accounting inequality only gives a bound from measured human resource components and does not constitute a competing, newly estimated policy-dependent effectiveness metric.

## R27 source-version numeric certificates
The LEADS arXiv v1 preprint is not an additional investigation to its 2025 journal version. The preprint abstract reports 0.77 comparator recall and 22.6% task-time reduction; the journal article reports 0.78 and 20.8%. Printed journal mean seconds (580 to 449) yield a 22.6% ratio of means, which may not equal an average of task-wise percentages; no aggregation procedure is inferred. Huotala reported means yield 9.69 seconds while the source narrative states 9.39 seconds. The original source display and both values are preserved, not silently reconciled. See `docs/source_view_numeric_trace.md` and `data/source_view_numeric_trace_2.csv`.
