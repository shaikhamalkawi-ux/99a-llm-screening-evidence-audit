# Project 99a — LLM screening: evidence and human-effort claim audit

**Public reproducibility material for a source-traceable critical review (development state: R22, 8 November 2026).**

The accompanying manuscript studies what a reported *workload saving* actually measures in LLM-assisted screening. This repository contains **bibliographic metadata, original-source links, interpretation rules, and executable consistency checks**. It does not provide third-party article PDFs or replicate the experiments in the original papers.

## Data scope and strict boundaries

- **60** frozen inherited candidate identifiers, not 60 eligible final studies.
- **49** original full reports checked at source level in R20: 45 provisional empirical and four provisional context reports. A source-access result is **not** an independent eligibility or scientific-admission result.
- **Five** final journal full-text gates unclosed (Li, Zhang, Insuk, Cao, Janoudi).
- **One** abstract-only item, **four** provisional scope exclusions, and **one** linked duplicate version in the 60-candidate count.
- The separately assembled **21-work interpretive core** includes two works outside the 60-candidate queue. Do not add 21 to 49.
- Independent second-human eligibility and extraction: **NOT PERFORMED**. Complete database search: **NOT PERFORMED**. Not PRISMA-compliant or an exhaustive systematic review.

## Contents

| Path | Purpose |
| --- | --- |
| `data/candidate_source_gates_60.csv` | Source-access and claim-boundary metadata, one row per frozen candidate |
| `data/selected_source_traceable_contrasts_9.csv` | Selected within-study contrasts; not independent pooling data |
| `data/claim_certificate_rules_7.csv` | Seven conservative interpretation gates, prose specification |
| `data/linked_publication_lineages_3.csv` | Preprint–journal and proceedings–journal dependence checks |
| `data/final_journal_fulltext_holds_5.csv` | Explicit remaining full journal report gates |
| `data/related_reviews_and_guidance_3.csv` | Closest reviews/prior methodological guidance |
| `scripts/claim_gates.py` | Executable rule engine **conditional on user-supplied evidence flags** |
| `scripts/validate_release.py` | Standard-library structural, count, provenance and embargo checks |
| `tests/test_claim_gates.py` | Unit tests and negative controls for rule engine |
| `docs/methodology.md` | Estimands, reproducibility boundaries, source rights |

## Reproduce verification (Python 3.9+; standard library only)

```bash
python scripts/validate_release.py
python -m unittest discover -s tests -v
```

Each row links to a publisher or author original source when available. A model's output or this audit is **not a second independent human reviewer**. An executable gate validates conditional *logic*, **not the truth or representativeness of manually sourced input facts**. No synthetic data, net staff-hour savings, pooled effect sizes, or independent model re-runs are claimed.

## Human time and retention

Given observed, matched baseline human time `M`, observed assisted human time `A0`, and unmeasured but nonnegative human verification, adjudication, recovery and maintenance time `U`, `net_human_saving = M - A0 - U <= M - A0`. If `U` is unbounded from above, net savings do not have a finite lower bound. If `M` or `A0` is not observed on comparable work, an *empirical* bound is not identified.

A recall number on a verified subset is not automatically an end-to-end complete-corpus sensitivity estimate. Related manuscripts using the same review IDs cannot be treated as independent benchmark populations.

## Source rights and release status

Bibliographic entries, DOI links and own audit scripts may be displayed publicly. **Third-party article files and full-text extracts are deliberately excluded** unless their exact redistribution rights are individually checked. This repository has **no confirmed re-use license yet**; please do not infer unrestricted permission from public visibility. Any code/data license and formal version DOI require author confirmation. No author names, ORCID identifiers, or institutional affiliations have been invented for the developing manuscript.

## Canonical source links

* Clark et al. (2025), review: https://doi.org/10.1017/rsm.2025.16
* Laignelot et al. (2026), review: https://doi.org/10.1016/j.jclinepi.2026.112221
* Farotimi et al. (2026), evaluation guidance: https://doi.org/10.1017/rsm.2025.10058
* Huotala et al. (2024), measured simplification experiment: https://doi.org/10.1145/3661167.3661172
* Full links for 60 candidates are in `data/candidate_source_gates_60.csv`.

**Status:** audit/development release only; not manuscript-submission approval.
