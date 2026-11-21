# Project 99a — public evidence and reproduction scope (22 November 2026)

## What this public repository supports

Project 99a examines how published claims about LLM-assisted screening relate to the recorded screening task, the unit of human effort, review policy, and retention relative to a named reference. The latest author-review manuscript baseline is **R56 EP1**, prepared for possible submission to *Publications*. It has **not** been accepted or submitted by this GitHub update. The manuscript author list, declarations, and any final repository DOI remain subject to author review.

The repository retains its earlier public-source modules (R28–R47). This update adds two missing source-bound research components that are used in the manuscript:

1. [`../data/R51_2021_2026_Targeted_Citation_Register.csv`](../data/R51_2021_2026_Targeted_Citation_Register.csv) and [`R51_Citation_Search_and_Admission.md`](R51_Citation_Search_and_Admission.md): a **purposively selected** contextual register of 15 relevant publications from 2021–2026. Not a full systematic search, included-study denominator, or redistributed third-party paper collection. Links point to the original publisher or DOI record.
2. [`../reproducibility/r48/`](../reproducibility/r48/): an independent-reference retrospective **human-only crowdworker** decision replay from three review topics originally studied by Mortensen et al. (2017). It contains the authors' Python code, derived anonymized decision cubes, exact results, source hashes and an independent-computation verifier. It contains **no original worker-level rows, copied publisher PDFs or private review records**.

## Reproduce the newly published aggregate checks

Python 3.10+ standard library suffices for the R48 aggregate cross-implementation audit. From the repository root, use:

```bash
python -m unittest discover -s tests -p 'test_r48_public_outputs.py' -v
python -m unittest discover -s tests -p 'test_r51_context_register.py' -v
```

To re-run the original-source R48 analysis rather than verify the released anonymous aggregate, download the corresponding source files from the pinned URLs in `reproducibility/r48/source_manifest.json`, confirm the hashes, and follow `reproducibility/r48/README.txt`. This third-party acquisition is a separate action; those raw files are intentionally absent.

Older tests remain:

```bash
python scripts/validate_release.py
python -m unittest discover -s tests -v
```

A GitHub Actions workflow checks the public manifest, earlier checks, the new R48 released outputs and R51 register. Passing these tests demonstrates deterministic code/file consistency on the published inputs. It does **not** certify original study eligibility, prospective LLM performance, independent human adjudication, or measured net human-person time savings.

## Distinct study populations and source restrictions

- PICOS: the source's 1,003 titles/abstracts and four previously recorded reviewer vectors are reproducible after separately acquiring the original Mendeley dataset, DOI [10.17632/4bgt2p5hrd.1](https://doi.org/10.17632/4bgt2p5hrd.1), published under CC BY-NC 4.0. Source rows are not mirrored here.
- Mortensen crowd data: 15,509 title/abstract records from **three topics of one human-only crowdworker study** and earlier expert labels. The frozen source repository and hash records are linked under `reproducibility/r48/`.
- R40 routing holds out 30 review units and reports separate conditional allocation outcomes; no observed net staff time is supplied.
- Third-party full-text research papers stay with their publishers. Consult the DOI and original-source links in the source registries. There is no blanket redistribution license for those PDFs.

## Manuscript and deposit status

The R56 EP1 manuscript PDF and LaTeX sources remain an **author-review submission package** outside this public repository pending authorship, preprint/public-disclosure, funding, conflict-of-interest, ethics and licensing sign-off. The public repository should be cited by its immutable Git commit; no Zenodo DOI, journal paper DOI, or final author citation metadata is asserted.

For provenance, see the existing `PUBLICATION_METADATA_PENDING.md` and `R47_PUBLIC_REPRODUCIBILITY_SCOPE.md`. Historical source-access statuses must be read with their dated overlays; the older R20 retrieval holds are historical, not current.
