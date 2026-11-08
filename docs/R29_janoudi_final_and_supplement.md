# R29 — Janoudi (2025), final journal report plus associated files

**Source status:** Final *Value in Health* article, DOI `10.1016/j.jval.2025.09.008`, 28(11):1630–1636, verified from a 7-page publisher PDF. The exact uploaded file SHA-256 is in `data/R29_janoudi_final_publisher_and_supplement.csv`.

## Companion file identity

- `mmc1.docx`, SHA-256 in public metadata: **the scientific supplement**, with Appendix 1 (platform interface), Appendix 2 (eight review search strategies), Appendix 3 (review-specific eligibility criteria), and Appendix 4 (logistic model specification, odds ratios and validation).
- `mmc2.pdf`, SHA-256 in public metadata: **16-page disclosure-form packet**, not an additional empirical study or a numerical-results supplement.

Neither file is published in this repository; protected publisher article text, interface screenshots, and completed disclosure forms are not redistributed.

## Exact source-linked claims

- Eight Canada Drug Agency review settings; 3,796 citations; 287 adjudicated Includes. Journal Table 2: TP=284, FN=3, FP=167, TN=3,342. Published sensitivity 98.9%, specificity 95.2%, precision 63.0% (source's rounded display).
- A fitted logistic model predicts classification errors. Journal Table 3 and supplemental Appendix 4: C-index 0.86 (confidence only) and 0.98 (confidence plus decision). Supplemental odds ratio for Decision=Include is 329 (95% CI 103–1055), model-specific; does not establish independent prospective calibration across unrelated datasets.
- Table 4: 145 (3.8%) or 221 (5.8%) citations *hypothetically* routed to human screening on the basis of confidence and inclusion decision. Resulting reported precision under ideal correction 81.4% or 89.9%. **These are simulations assuming perfect correction of flagged errors, not actual rescreened person-minutes.** No net human labor saving is identified.
- The article declares Loon Inc funding and authors' employment/advisory relationships. This is a reported potential conflict for contextual interpretation, not proof of invalid results.
- The final article and the earlier preprint use the same eight reviews; they are linked versions of one research lineage, not independent benchmark evidence.

## Count boundary

Frozen 60 candidate identifiers. Original R20 source checks: 49. R28 verified three additional final publisher reports; R29 verified Janoudi. **Current 53 full original reports checked**, one final text hold (`LIT-003`, Li). This is *source-access* status only, not 53 final eligible studies or a comprehensive systematic-review flow.

Run `python scripts/validate_r29_overlay.py`; the verifier checks only entered values, arithmetic, and metadata. It does not rerun Loon Lens, recover the participant-level records, or test the assumption of perfect correction. No original experiment is invented.
