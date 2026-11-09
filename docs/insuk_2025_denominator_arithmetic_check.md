# Insuk et al. (2025) — conditional printed-count consistency check

**Source:** *Journal of Medical Systems* 49:110, DOI `10.1007/s10916-025-02246-4`; original journal PDF, pp. 3, 4–5. This is an **authored source-view audit**, not model replication or a published erratum.

The Results prose and Table 1 report **1,648** title/abstract records, with an experienced researcher excluding 1,615. This implies 33 reference inclusions. Figure 1 also displays 1,648 screened. The heading of Table 3 instead states **n=1,684**. Under the assumption that Table 1 and Table 3 refer to the same corpus and experienced-researcher reference, the Table 1 screener-specific exclusion counts and Table 3 sensitivity uniquely reconstruct the integer confusion matrices:

| Screener | TP | FN | FP | TN | Conventional FPR=FP/(FP+TN) | Printed Table 3 FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Junior researchers | 21 | 12 | 55 | 1560 | 0.0341 | 0.0378 |
| ChatGPT | 27 | 6 | 136 | 1479 | 0.0842 | 0.0884 |
| Claude | 27 | 6 | 85 | 1530 | 0.0526 | 0.0574 |

The reconstructed accuracy, recall, precision and NPV match Table 3 to displayed precision or within 0.00011. The FPR column does not match the standard denominator implied by these count data. Alternative denominators or data-processing stages cannot be excluded without the authors' original analysis; **do not declare a confirmed publication error or change the original results**.

Reproduce using `python scripts/check_insuk_2025.py` and `python -m unittest discover -s tests -v`. Original copyrighted publisher PDF is excluded from public code release. This diagnostic is a source-level arithmetic check only, and it does not alter study selection, time saved, or overall review outcomes.
