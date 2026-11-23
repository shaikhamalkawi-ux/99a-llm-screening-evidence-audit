# Research-only source-pinned external consensus gate

The script in this branch tests post-hoc agreement-only screening policies on the publicly saved, human-reference-labeled model outputs of Matsui and Takaesu (2026, *Information*, DOI 10.3390/info17111160). It measures all-negative agreement misses and the volume of records requiring disagreement review under a fixed source reference. It does not rerun models, observe human adjudication, or estimate person-time.

Inputs are downloaded ephemerally in GitHub Actions from pinned upstream commit `d911eafc5299aa3ca41a6aacf0167931c81fcbbc` and checked bytewise against published SHA-256 values. Third-party predictions are never committed to this repository. This branch is an **evidence gate only**, not an admitted extension of paper 99a. R56 EP6 remains scientifically unchanged.
