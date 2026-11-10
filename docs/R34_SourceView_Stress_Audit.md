# R34: Source-view claim stress audit, not model replication

**Date:** 10 November 2026. **Starting manuscript:** Project 99a R33. **Result:** Five new source-view constraint cases were derived from published displays; the historical 60-candidate project queue, 54 checked reports, 21-case interpretive core, and 11 new bibliographic discovery records are unchanged. The five cases are a selected set of journal fulltexts obtained in R28–R30, not a random sample of screening research. A public executable script tests exact arithmetic and explicit assumptions. It does not reproduce original model predictions or recover unseen inclusion labels.

## Reversal-first perspective

Instead of asking only whether a paper advertises *workload saving*, we ask **what observation could make a reader's stronger interpretation fail or become warranted**. Each source statement is separated from the post-hoc conditional calculation and from an unsupported claim upgrade. All cases keep the authors' original numbers intact.

| DOI | Published display | Testable consequence | Required caveat |
|---|---|---|---|
| 10.1016/j.ijmedinf.2025.106035 | Zhang MCI-Speech 61 included; 959 in abstract/Table 1; 936 in Methods; 6.5% reported | 61/959 = 6.4% vs 61/936 = 6.5% to one decimal | Different acquisition/test stages could account for the discrepancy; no author-error claim |
| 10.1007/s10916-025-02246-4 | Insuk total 1,648 vs Table 3 heading 1,684; printed ChatGPT FPR 0.0884 | Conditional standard FPR 136/1615 = 0.0842 from one common reference; other source metrics reconstruct to display precision | Exact denominator/coding may differ; cannot overwrite paper's value |
| 10.7326/ANNALS-24-02189 | Cao full texts available for 59.16% of final inclusions; assumed human 30 sec/abstract | Any **hypothetical policy discarding all unavailable fulltexts** can cover at most 59.16% of known original inclusions, before classifier errors. 10,000 abstracts at assumed 30 s each yields 83.33 modeled hours | NOT the source's deployed end-to-end recall; do not multiply access share by weighted 96.5% sensitivity or interpret modeled hours as observed |
| 10.1016/j.jval.2025.09.008 | Janoudi TP284 FN3 FP167 TN3342; 145/221 simulated Include-only corrections | Perfect repair eliminates 102/135 of 170 baseline errors; the 3 false negatives persist in both scenarios | Not executed review or staff minutes, and simulated error repair assumes perfect human adjudication |
| 10.1016/j.ijmedinf.2025.106205 | Li 6,331 records, 113 positive; named setting precision 0.34, recall 0.77, NPV 1.00 rounded | **IF** same full universe and nearest-hundredth display used: 7 feasible integer matrices; each has TP87 FN26, 253-259 predicted Includes, NPV 0.995718-0.995722 still displaying 1.00 | No publication of the underlying full matrix; different filter stages, averaging, or rounding invalidate the reconstruction; no net staff-time benefit identified |

## Material falsifiers

- **Zhang:** source-specific documented filtering between 959 and 936, or reproducible exact cohort definitions, could reconcile the percentages.
- **Insuk:** the original screener-by-reference confusion matrix and precise FPR code could explain the published denominator, so this is an open source-view discrepancy and not a proven error.
- **Cao:** a real second-stage route for unavailable fulltexts invalidates the *discard-only* hypothetical ceiling. The sample-coverage number does not itself estimate an implemented pipeline's net recall.
- **Janoudi:** directly observed, timed correction interventions, especially adjudication of predicted Excludes, would provide new evidence not offered by the reported perfect-repair scenario.
- **Li:** if post-filtered subsets differ among reported ratios, or a nonstandard aggregation is used, the integer-feasibility set no longer identifies the same information. The computed 95.91-96.00% not-predicted-Include fraction is *only* a possible queue fraction under the common-universe assumption, not the original paper's net staff-hour effect or an estimate for all its configurations.

## Reproducibility and scope

Run `python scripts/check_r34_source_constraints.py` and `python -m unittest discover -s tests -v` from the public package root. Read `data/R34_FiveSource_ConstraintInputs.json`, `data/R34_SourceView_ClaimLicenses_5.csv`, and the printed DOI/page references in the main manuscript's Appendix I. Source observations are stated at the aggregate display level and original third-party article binaries are deliberately not redistributed. No human review intervention was performed, no new eligible-study denominator is introduced, no cross-paper prevalence or confidence interval is estimated, and no first-invention claim is made for verification-aware workload or workflow-specific estimands (Lai, Nunnery, Madeyski and Barragán are acknowledged as prior art).

**Exact source-file matching:** `data/R34_OriginalPDF_SourceFingerprints_5.csv` records SHA-256 hashes, file sizes and DOI identities of five restricted publisher originals. All five hashes independently match their frozen R28, R29 and R30 source-admission metadata. This confirms byte identity of the files evaluated, not validity of unreported study results. The publisher PDFs are excluded from the public files.
