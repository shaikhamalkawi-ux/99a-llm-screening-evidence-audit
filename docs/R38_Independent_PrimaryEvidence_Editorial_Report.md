# Project 99a - R38 Independent Primary-Record Evidence Admission

**Date:** 10 November 2026  
**Current publication manuscript:** R37 remains unchanged.  
**Classification of this deliverable:** new, independent reanalysis of existing, primary, record-level human screening decisions. This is **not** a newly conducted human experiment, not a causal evaluation of LLM assistance, and not a revised submission-ready manuscript.

## Executive finding

The published, versioned primary dataset **Generative AI-Assisted Title and Abstract Screening** (Mendeley Data DOI [10.17632/4bgt2p5hrd.1](https://doi.org/10.17632/4bgt2p5hrd.1), license CC BY-NC 4.0), associated with **Vallamchetla et al. (2025)** ([10.1016/j.jbi.2025.104860](https://doi.org/10.1016/j.jbi.2025.104860)), was lawfully retrieved from the file/ZIP download links displayed on its public repository webpage. Its exact CSV source bytes were verified against the official ZIP. The CSV is 1,963,035 bytes, with SHA-256 `11e8cba6a21f936253e9a2c85d88b942efcdf5401b1e8b7bf5cbcedd0e851425`.

**All 1,003 study-screening records have an explicit reference decision and four individual human reviewer decisions**. The reference identifies 25 positive and 978 negative citations. The original aggregate screening outcomes are exactly reproducible, not inferred from rounded percentages. This is a materially stronger independent evidence layer than the previously published-count-only Janoudi (2025) counterfactual analysis used in R35-R37.

### Reconstructed observed reviewer confusion matrices

| Human reviewer | Study condition | TP | FP | FN | TN | Precision | Recall | Published total screening minutes |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| A1 | Assisted by LLM-generated PICOS | 25 | 1 | 0 | 977 | 96.15% | 100% | 116 |
| A2 | Without PICOS assistance | 22 | 7 | 3 | 971 | 75.86% | 88% | 463 |
| B1 | Assisted by LLM-generated PICOS | 25 | 1 | 0 | 977 | 96.15% | 100% | 90 |
| B2 | Without PICOS assistance | 23 | 3 | 2 | 975 | 88.46% | 92% | 370 |

These four rows agree with the original article's accuracy/sensitivity/specificity/F1 displays and its one/ten/one/five error counts. Published minutes are **per-reviewer task totals** in the article, not 1,003 individually timed citation observations. The four reviewers were distinct people, and differences in reviewer skill, interface and other factors cannot be separated as a causal assistance effect.

## New source-executed disagreement findings

Across 4,012 person-by-record decisions (1,003 records by four reviewers), 17 reference-discordant decisions occurred on **15 different records**: 14 records were wrong for one reviewer, and one negative record was falsely included by three reviewers. The **three false-negative exclusions by A2 and two by B2 occurred on five different reference-positive records**, with no overlap; the single false positive by A1 and the single false positive by B1 were also on different records.

These overlap statements were computed from **observed published individual decisions**, not from hypothetical error distributions, model outputs, or simulated review actions. They are not estimates of the field-wide frequency of human screening errors, because only 25 reference positives and one clinical topic appear in the dataset.

## A conditional replay using observed human labels

To test the previously theoretical concern that stricter human review may increase precision while sacrificing evidence retention, we performed a post-hoc **Include-only override replay**. We took the 26 decisions initially marked Include by assisted reviewer A1. We then used the **already recorded independent** A2 or B2 decision only to decide whether each of those 26 would remain included; original A1 Excludes could not be rescued.

| Analysis state | TP | FP | FN | Precision | Recall |
|:--|--:|--:|--:|--:|--:|
| Observed decisions of A1 (one stage) | 25 | 1 | 0 | 96.15% | 100% |
| Counterfactual A1 Include-only then A2 label override | 22 | 0 | 3 | 100% | 88% |
| Counterfactual A1 Include-only then B2 label override | 23 | 0 | 2 | 100% | 92% |

Therefore, on an **actually observed set of reviewer decision vectors**, correcting the false positive in A1's Include queue at the expense of three or two erroneously rejected true positives can yield apparently perfect precision while reducing reference recall. This is a concrete external **feasibility witness** for the direction of the R35-R37 mathematical concern; it is **not** evidence that such a sequence was carried out in the source experiment, and it does not validate a real deployed intervention. No correction probabilities or new person-minutes are inferred.

## Additional counterfactual policy diagnostics - not recommendations

- A1 AND B1 (both assisted): TP=25, FP=0, FN=0, TN=978 against the fixed source reference. The two observed false positives were disjoint. This is an optimistic **post-hoc fusion** outcome on the *same* screened corpus, not external validation, not a prescription to use AND, and not evidence that double reviewing is cost-free.
- A2 OR B2 (both unassisted): TP=25, FP=9, FN=0, TN=969. Because their five false-negative records were disjoint, including a record when *either* reviewer said Include recovers all 25 fixed-reference positives, but keeps nine negatives. This result is likewise an **unexecuted policy replay**; manual adjudication labor was not timed.
- A2 AND B2: TP=20, FP=1, FN=5, TN=977. The choice of fusion rule changes retention even with the same four source decision columns. Neither the full list of possible algorithms nor their general performance was tested.

## Second authenticated source archive: LEADS / Nature Communications

A separate official **Source Data** ZIP was acquired from the Nature Communications article [10.1038/s41467-025-62058-5](https://doi.org/10.1038/s41467-025-62058-5), with original ZIP SHA-256 `104fad1ea40e656405ba2ff30598de08a07ec3ac79bf7b9f5cdb4a4a728dee96`, byte count 4,847,017 and successful ZIP CRC. Its source workbook, SHA-256 `52e659bd88aa3c4ab7a9e37fd81ff47eab37115a5ade7c3c0f77a057c030be90`, contains Figure 5d source values (Expert+AI recall@10=0.81, time=72.1 seconds; Expert recall@10=0.78, time=91.1 seconds) and Figure 5h **extraction-task** topic/arm summaries. Of Figure 5h's 36 distinct topic/task keys, 28 have both arms and eight have only one; within the 28 paired averages, assistance has a shorter value in 17 and longer in 11. This source **does not supply a second participant-level title/abstract screening decision dataset** in those inspected sheets. It is therefore held as a source-provenance/context check, not promoted to independent evidence for the screening-replay claim, and the Figure 5h extraction-stage outcomes are not pooled with PICOS or used as a causal effect.

## Source identity, duplicate check and reproducibility

The PICOS file contains 1,003 unique title-and-DOI row pairs; a DOI-like field contains the string `nan` for 53 distinct bibliographic rows and is **not** interpreted as 53 repetitions of one investigation. Five paper titles repeat but have different years/DOIs or bibliographic records, so title-only de-duplication is inappropriate. Every one of the 1,003 rows has five nonmissing, valid binary decision labels. Source bytes match the official public ZIP entry exactly.

The published article and its scientific supplement had already been admitted to the existing 99a corpus. This delivery adds **new row-level reanalysis evidence**, not an extra independent source study in the historic 60/54/21/11 counts. An independent Python standard-library verifier and 26 source-dependent tests reproduce the matrices, overlap findings and replay policies. Source CSV must be independently downloaded from its DOI; it is not redistributed in the public code bundle. R38 remains a **source-acquisition and scientific-extension package**, not a finalized R38 revision of the full R37 manuscript.

## Editorial implication for 99a

**Decision: ADMIT as primary record-level source evidence, with constrained claims.** Add a short Methods/Results item to a subsequent integrated Article revision describing (i) original decision overlap and (ii) an explicitly counterfactual Include-only override replay, with all the caveats above. Avoid declaring the source team's outcome causal, labeling reconstructed actions as observed human follow-up, or describing 100% reference recall as a general guarantee. The strongest new contribution is a **fully reproducible external, source-anchored human-disagreement witness** connecting the paper's theoretical sensitivity findings to *real decisions*, not proof of a particular deployment policy's benefit or harm.

**Required article-level scholarly review:** confirm how the original dataset's reference was established, avoid pseudoreplication from 4,012 correlated ratings, consider whether a second independent record-level corpus is available, and integrate only result-linked material by replacing weaker repetitions rather than indiscriminately lengthening the already 30-page main paper. Do not open a cosmetic R39 version. Author metadata, rights, target article type and submission decision remain separate gates.

## Source links

- Mendeley primary versioned dataset: https://doi.org/10.17632/4bgt2p5hrd.1  
- Published reviewer experiment: https://doi.org/10.1016/j.jbi.2025.104860  
- Nature Communications LEADS source article and source-data link: https://www.nature.com/articles/s41467-025-62058-5  
- Existing R37 baseline GitHub code: https://github.com/shaikhamalkawi-ux/99a-llm-screening-evidence-audit/tree/r37-exact-display-compatibility
