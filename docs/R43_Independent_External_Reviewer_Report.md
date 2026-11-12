# Project 99a — R43 independent reviewer assessment (12 November 2026)

**Decision: ACCEPT as a focused literature-coverage closure, not as new empirical validation.** The newest R42 manuscript now compares directly with (i) Ringeval et al. 2026 (ECIS conference, official abstract), (ii) Akaraci et al. 2026 (Systematic Reviews six-tool SWAR, official published article), and (iii) Liu et al. 2026 (J Eval Clin Pract four-LLM evaluation, publisher/PubMed metadata). Each source was verified against publisher metadata. There is no fabricated DOI for the conference paper.

## What was added

- Two concise numeric rows to the early **Table 1**. Ringeval: 5,808 records; manual 1,018 minutes and 28 final reports; ASReview 746 records / 92 minutes / 28 of 28; Covidence 505 / 53 minutes / 5 of 28. Akaraci: six tools, none exceeding 50% early recall by the first 25% screened in the source umbrella-review study.
- A paragraph in the Introduction connects Liu's four-model, 3,550 title-and-abstract and 233 full-text observations (reported screening recall 0.83–0.91; precision 0.27–0.40) to the distinct 99a source-anchored human-screening analysis.
- A short Discussion paragraph explains why these evaluation targets cannot be compared as a universal tool ranking.
- Three bibliographic entries with publisher-verified identities and two confirmed DOIs; Ringeval has an official proceeding URL but no verified DOI.

## Our numeric contrasts, kept separated from external results

- Source-review register **54 full reports among 60 candidates**, 21 overlapping selected close readings, 11 discovery-only records, no PRISMA-complete selection claim.
- PICOS primary source: **1,003 records**, 25 fixed source positives, 17 reviewer–reference discordances on 15 records. An unexecuted include-only intersection can change precision from 96.15% to 100% and recall from 100% to 88%; no causal human-time effect.
- Held-out retrospective routing: eight SYNERGY review units (315 positives) and 22 Chan review units (598 positives); at 50% nominal human budget B0/B1 exclusions **67/49** and **74/81**, respectively; at 90% **0/2** and **4/6**; at >=95% zero exclusion because every record is either sent to review or provisionally included. This is a policy identity, not a model sensitivity achievement.

## Claim boundaries / Keep-Hold-Remove

**KEEP** source-specific comparisons, task/stage distinctions, and review budgets. **HOLD** any causal net time-saving inference, direct comparison of external algorithms with B0/B1, full-corpus review prevalence, fuzzy B2 performance, and claims that any three works were newly included in the original 54-source audit. **REMOVE** any phrasing suggesting first discovery of the workload-vs-benefit problem or a universal tool winner (none introduced).

### Verification results

- R42 original supplement `.tex` is **byte-identical** in R43, and R43 supplementary PDF is the same R42 PDF.
- The existing **main table and display-equation environments** are unchanged in number; Table 1 gains two source-identified rows. Prior scientific results remain unchanged.
- Clean LaTeX compilation succeeded for `main.tex` (34 pages) and `main_integrated.tex` (49 pages); supplementary PDF has 18 pages. Combined reader PDF is **52 pages**, manuscript first (1–34), supplement directly after (35–52); text extraction agrees for every source page.
- All three new references appear in generated bibliography; no undefined citations/references, no overfull boxes, no Type 3 fonts. Earlier inherited apacite warnings concerning `others` are not introduced by these citations and remain documented as editorial warnings.

### Clean-source reproduction

The delivered R43 main, inherited supplementary PDF and integrated source PDF were reproduced from a clean extraction of the Overleaf ZIP with **zero changed text pages** across 34, 18 and 49 pages respectively. The inherited MDPI class typesets a dynamic Version date on the supplementary first page; forcing `SOURCE_DATE_EPOCH=1794355200` and `FORCE_SOURCE_DATE=1` reproduced the archived 11 November 2026 footer. Without the deterministic date setting, only that footer date differs; no scientific text or numeric result changes.

## Open author/journal gates

Author names/order, affiliation, corresponding author, funding, ethics/consent wording, conflicting interests, journal portal configuration and repository DOI/licence await author approval. This package is not evidence of journal acceptance or a registered PRISMA systematic review.

### Sources

- Ringeval et al. (2026): https://aisel.aisnet.org/ecis2026/litrev/litrev/11/
- Akaraci et al. (2026): https://doi.org/10.1186/s13643-026-03313-8
- Liu et al. (2026): https://doi.org/10.1111/jep.70596
