# Project 99a — R45 targeted review closure (15 November 2026)

## Independent scientific readback
Five original publisher PDFs (Zhang, Insuk, Cao, Janoudi and Li) were re-opened from the project's existing private Google Drive sources. Their exact SHA-256 digests and source-page locators were checked. Independent arithmetic confirms all five **conditional** interpretations in the existing manuscript. This is not a second independent human assessor, not new source labels and not a rerun of the original LLM tools. See `R45_Original_Publisher_FiveCase_Evidence_Log.csv` and `reverify_five_source_cases.py`.

- **Zhang**: 959 (Abstract/Table 1) versus 936 (Methods), 61 includes. The printed 6.5% aligns with 936 to one decimal; original authors may refer to different stages. No corrected denominator is inferred.
- **Insuk**: 1,648 screened / 33 positives and original exclude counts yield junior (21,55,12,1560), ChatGPT (27,136,6,1479), Claude (27,85,6,1530) in TP,FP,FN,TN order. Standard FPRs ~0.0341, 0.0842, 0.0526 differ from printed 0.0378, 0.0884, 0.0574; Table 3 heading also says n=1684. Source-stage denominators are not reconciled, hence no accusation of publication error.
- **Cao**: a source-assumed 30-second/abstract reading time yields 83.33 **modelled** hours per 10,000 abstracts; 12,690 free full texts account for 7.56% of search citations and 59.16% of original finally included reports in the source's sample. The 59.16% ceiling is conditional on an unobserved rule that unavailable full texts are excluded, not measured retention.
- **Janoudi**: original 3,796-case matrix (284, 3, 167, 3,342) in TP,FN,FP,TN order. Simulated inclusion-only review of 145 or 221 flagged cases produces displayed 81.4% and 89.9% precision only at complete correction states (x,y)=(102,0) and (135,0) under the specified binary policy and one-decimal rounding. Original false negatives remain 3.
- **Li**: under the explicitly hypothetical common 6,331-record reference with 113 positives, printed P=.34/R=.77/NPV=1.00 to two decimals admits **seven** matrices, all TP=87/FN=26, with FP=166–172. Rounded NPV alone cannot certify zero false negatives.

## Three reviewer fixes implemented
1. **Independent five-source cross-check:** re-opened five exact source publisher PDFs and re-ran source-conditional arithmetic. Added one bounded evidence note in Supplementary Appendix I, not a new article result or new full-text eligibility count.
2. **Redundant prior-work table:** moved all original rows of former main Table 16 into Supplementary Appendix H as Table A10. The more reader-friendly early Table 1 remains in the main paper. The main Discussion now refers to Appendix H rather than repeating the table.
3. **Pagination and author/journal gate:** rewrote the source-sample/prevalence sentence into an intact statement before floating tables, added a table barrier, and recompiled all outputs. Final author order, affiliations, CRediT, corresponding email, data DOI/license, funding, conflicts, ethics and AI-use disclosure require real author approval; no values or addresses were invented.

## Locked boundaries
The 60/54/21/11 evidence layers remain distinct. The 1,003-record PICOS original reviewer data and source-positive counts, Janoudi/Li arithmetic gates and B0/B1 results remain unchanged. Fuzzy B2 stays HOLD. No prospective human review, measured net labor or causal effect was added. The five primary article PDFs remain in restricted storage only.

## Deliverable
R45 paper 31 pages, supplementary 19 pages; **50-page main-first-then-supplement PDF** is primary reading file. The integrated reference compilation is separate. Scientific claims unchanged; move/QA report and executable arithmetic verifier included with final author-review package.
