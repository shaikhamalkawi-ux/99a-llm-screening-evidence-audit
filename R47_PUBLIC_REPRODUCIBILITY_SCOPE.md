# Project 99a — public reproducibility scope (R47 editorial consolidation, 20 November 2026)

This repository includes the frozen R35 baseline and public-safe R36, R39, R40, and R45 source-bound verification materials. **It is not a full raw-study archive.** It does not rerun original source authors' LLM tools, execute any new human-review experiment, or estimate causal net human time savings.

## Instructions and boundaries

- R36 joint-target arithmetic: `python scripts/check_r36_joint_certificates.py`; derived outcomes are mathematical possibilities under Janoudi's printed aggregate counts, **not observed reviewer errors or probabilities**.
- R39 record-level PICOS: obtain the separately licensed original source CSV from https://doi.org/10.17632/4bgt2p5hrd.1 (CC BY-NC 4.0) and run `python scripts/r39_picos_reanalysis.py --source path/to/source.csv --out path/to/output/`. The verifier checks an exact pinned source hash; the original CSV is **not redistributed**. AND/OR and include-only combinations remain counterfactual recombinations of four previously recorded independent decision vectors.
- R40 routing arithmetic: run `python scripts/verify_r40_policy_identity.py data/r40/heldout_per_review.csv /tmp/r40_results.json`. Data are derived per-review benchmark routing outputs, not raw abstract text or observed person-time. Zero automatic misses at nominal 95% human budget arise from **zero automatically excluded records**. Routing scenarios depend on 30 holdout review units; they are not 840 independent tests.
- R45 five-report source checker: `scripts/reverify_five_source_cases.py` requires the original five publisher PDFs in private storage for its full source-byte replay. Publisher PDFs are not included here. The public audit report gives source locators and explicit uncertainty.
- The criterion-level B2 fuzzy option remains HOLD / NOT CALIBRATED. A higher precision after an unexecuted decision intersection must not be described as a newly observed human workflow.

No author-approved public reuse license, repository DOI, ethics/funding disclosures, or journal acceptance is claimed. Public presence does not confer unlimited third-party redistribution rights. The editorial R47 manuscript package uses these public-safe materials and preserves earlier scientific results.
