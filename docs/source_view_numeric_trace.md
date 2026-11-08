# R27 source-version and arithmetic checks (two *underlying* studies)

These are source-view **certificates**, not an independent experiment, a new effect estimator, or an additional pair of eligible studies. See `data/source_view_numeric_trace_2.csv` for exact views, DOI, locators and restrictions.

## LEADS
- Version-1 arXiv preprint (Jan 27, 2025), indexed as preprint at PMID **40735107**: recall 0.81 assisted vs. 0.77 comparator; 22.6% time reduction. https://pubmed.ncbi.nlm.nih.gov/40735107/
- Journal *Nature Communications* (Sep 24, 2025), DOI **10.1038/s41467-025-62058-5**: 0.81 vs. 0.78; 20.8% reported time reduction; printed mean task times 580 s and 449 s in the body text near Fig. 5d. https://www.nature.com/articles/s41467-025-62058-5
- `(580-449)/580*100 = 22.586...%`, displayed as 22.6% to one decimal. This ratio of displayed means differs from the published 20.8%. It may reflect aggregation convention or reporting-version changes. **We cannot identify which without the participant-level data and exact aggregation procedure. We neither overwrite the published 20.8% nor label it an established mistake.** The preprint and journal article are one research lineage, not two independent experiments.

## Huotala et al., EASE 2024
- Original author HTML contains printed Table 1 means of 85.95 s (original) and 76.26 s (simplified), giving 9.69 s, while the narrative gives 9.39 s. https://arxiv.org/html/2404.15667
- Preserve both reported quantities as a source arithmetic discrepancy. The abstract representation experiment is different from assisted vs. unassisted screening and does not measure whole-review net labor.

## Reproduce without external dependencies

`python scripts/validate_source_view_numeric_trace.py` and `python -m unittest discover -s tests -v`. The frozen input values are copied from the specified source displays and mechanically checked, rather than certified through access to private participant-level data. Public visibility alone does not grant redistribution rights to third-party source PDFs.
