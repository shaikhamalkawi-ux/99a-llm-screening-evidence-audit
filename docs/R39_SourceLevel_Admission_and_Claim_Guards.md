# Project 99a — R39 primary reviewer-decision evidence admission

**Source:** Vallamchetla et al. (2025), *Journal of Biomedical Informatics* DOI `10.1016/j.jbi.2025.104860`, Mendeley Data Version 1 DOI `10.17632/4bgt2p5hrd.1` (published 5 March 2025). This was already one of the 21 interpreted investigations: it does **not** increase counts of candidate records, source-checked reports, selected independent studies, or November discovery records (60/54/21/11 remain separate and unchanged).

**Direct evidence:** exactly 1,003 citation rows; original source reference 25 Include and 978 Exclude; one source-provided decision for each of 4 human reviewers on each row. The original CSV is 1,963,035 bytes and has SHA-256 `11e8cba6a21f936253e9a2c85d88b942efcdf5401b1e8b7bf5cbcedd0e851425`. Two reviewers A1/B1 used PICOS summaries and two A2/B2 did not; all four are distinct individuals. The source labels are accepted as reported, not independently re-adjudicated.

**Observed source-relative counts:** A1 (TP=25, FP=1, FN=0, TN=977); A2 (22,7,3,971); B1 (25,1,0,977); B2 (23,3,2,975). Across the 4 decision vectors, 17 reference-discordant decisions affect only 15 citation rows. The 5 reference-positive misses of A2 and B2 are on disjoint citations, and the 2 false positives of A1 and B1 are also on disjoint citations. Four reviewers do not constitute four independent cohorts; do not calculate a pooled field-wide human error rate.

**Derived counterfactuals (not executed):** A1 Include-only AND A2 decisions gives TP=22,FP=0,FN=3,TN=978; A1 AND B2 gives TP=23,FP=0,FN=2,TN=978. Accordingly precision can reach 100% while recall falls from 100% (A1 alone) to 88% or 92% *in a deterministic replay of already observed independent decisions*. These were never sequential human adjudications; no actual second-stage reviewer minute, correction probability, or policy efficacy is measured. A1 AND B1 also happens to yield perfect reference agreement on this corpus, but has no external or prospective validation.

**Timing and attribution:** The published source reports A1=116, B1=90, A2=463, B2=370 minutes for their original assignments. Reviewer identity, experience, interface, and assignment are not separable into a causal AI effect; these task totals cannot be assigned to simulated consensus/override workflows and cannot be called net project labor savings.

**Rights:** the Mendeley dataset is CC BY-NC 4.0. The source CSV includes article abstracts/PICOS summaries and is not redistributed in this public package. Acquire the lawful source file from DOI `10.17632/4bgt2p5hrd.1` and run the source-dependent verifier. Only derived count summaries, the code and source metadata are public.

**Exact reproduction:**

```bash
python scripts/r39_picos_reanalysis.py --source '/PATH/Screening_articles and decisions.csv' --out /tmp/r39_derived
R39_SOURCE_FILE='/PATH/Screening_articles and decisions.csv' python -m unittest discover -s tests_source_dependent -v
python scripts/validate_release.py
python -m unittest discover -s tests -v
```

The source-specific rerun returned 26/26 PASS and all five derived output files were byte-identical to the prior R38 delivered results. See `data/r38_source_reanalysis/` for SHA-checked aggregate outputs. No original LLM rerun, randomized trial, full-text re-adjudication or new prospective observation is claimed.

**Admission:** KEEP as independent primary record-level reanalysis of **an already counted source**, with observed-label and counterfactual distinctions mandatory. LEADS Figure 5h source data are extraction-task summaries and not admitted as an independent title/abstract screening reviewer-decision dataset.
