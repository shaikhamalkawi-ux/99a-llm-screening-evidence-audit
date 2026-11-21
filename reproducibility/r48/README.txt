99a — Final separate-reference human screening test
Analysis date: 20 November 2026. Manuscript baseline: R47 (unchanged).

PURPOSE
Reanalyze recorded crowdworker eligibility answers against the original experts'
separate title/abstract reference, and measure shared errors that a hypothetical
review of pair disagreements cannot correct. Findings are in findings.json;
review-specific exact expected matrices and sensitivities are in results.json.
These files record a secondary computational reanalysis, not a new human trial.

SOURCE
Mortensen et al. (2017), An exploration of crowdsourcing citation screening for
systematic reviews. Research Synthesis Methods. DOI: 10.1002/jrsm.1252.
https://pmc.ncbi.nlm.nih.gov/articles/PMC5589498/
https://github.com/bwallace/crowd-sourced-ebm
Frozen commit: 297806d9f7db602b1f0c1f046d61a46293a42b53.
Every original download was matched by byte count, Git blob SHA1 and SHA256.
The package does not redistribute third-party raw responses or original code.
source_manifest.json gives pinned URLs and hashes for all inspected source files.

PRIMARY SCOPE
Appendicitis, DST and Omega3: 15,509 records, 735 title/abstract reference
positives, 75,308 interpretable derived worker decisions. Remove honeypots and
each review's own original blocked-worker list. Omit 18 unresolved decisions;
all records still have at least two usable distinct workers. Also evaluate
unresolved decisions as all 0/all 1 and include excluded workers as sensitivities.
ProtonBeam is an explicitly separate pilot/descriptive analysis with a selected
paired subset. Full-text endpoints are not analyzed; see source_issues.json.

Each record receives total weight 1. Every unordered pair of its observed valid
workers is weighted equally. This averages possible pairs within the observed
worker pool; it does not simulate a newly observed fixed two-reviewer team.
All 146,231 primary pair combinations share records and workers, so they are not
146,231 independent observations. No pair-based p-values or confidence intervals
are reported. Exact fractions denote expected record counts, not fractional
observed people or records. Pooled totals are descriptive convenience-sample sums.

The plan was written after source/schema inspection and before root performance
computation. It was not preregistered or blinded to the published article.
Original analysis_plan.json SHA256:
9eace48c85bf5ecb607896ebec88da7f8ba54c91903770ff338f13071c210aae

REPRODUCE (Python3.10+ standard library, from this extracted directory)
1. Obtain the original main CSV and processing R for each of the four reviews.
   The first command can download missing pinned files if the host permits it:

   python replay_independent_reference.py --source-dir sources --out-dir reproduced --download

   If source files were acquired separately, omit --download and use their directory.
   Files are accepted only after their byte count and both hashes match the manifest.

2. Run the separately written independent parser:

   python independent_audit.py --source-dir sources --out-dir independent-output

3. Compare exact matrices, rates, cohort counts and disagreement controls, and
   verify pair probabilities by literal enumeration:

   python verify_replay.py --results-dir reproduced --independent independent-output/independent_mortensen_audit_results.json

The independent parser was written without reading/importing the root parser.
All primary comparisons and the three requested sensitivity variants matched
exactly. Independent here means computational implementation, not human review.
The delivered verification.json matches the delivered independent_results.json.
An optional --item-details flag on independent_audit.py exports source-linked
item details locally; these are omitted by default and from this package.

KEY INTERPRETATION
There are 77 reference-positive records rejected by every accepted observed
worker, and 31 reference-negative records retained by every such worker, with no
unresolved votes on those records. These are actual integer item counts, distinct
from expected error counts of a randomly selected pair. Shared pair errors remain
even if every disagreement is corrected perfectly using the fixed reference.

Crowd instructions were simplified and broader than the original expert criteria.
Title/abstract reference-positive means retained at that screening stage; it is
not synonymous with final inclusion. Crowdworkers are not trained systematic-
review experts. No new blinded expert adjudication, executed human correction,
LLM result, causal person-time saving, or prospective workflow safety is established.
The original paper aggregates by question across workers; this reanalysis first
forms each worker's criterion conjunction, then applies pairwise policies.
The known nesting of AND/OR sets is not a new scientific result. The measured
quantities are source-specific error magnitudes and shared errors under the
separate reference. Final paper/appendix admission is an editorial decision.

CONTENTS
analysis_plan.json: analysis choices fixed before root metric computation.
replay_independent_reference.py: source-checked primary implementation.
independent_audit.py: independent parser, with portable input/output arguments.
verify_replay.py: exact implementation comparison and literal pair enumeration.
source_manifest.json: frozen original URLs, sizes and content hashes.
source_integrity.json: main-source identity, cohort and preprocessing checks.
source_issues.json: reference-stage discrepancies and applicability boundaries.
decision_cubes.json: anonymous aggregate sufficient statistics, no worker IDs.
results.json: exact review-specific expected matrices and sensitivities.
independent_results.json: independent aggregate verification output.
verification.json: executed exact comparison results.
findings.json: main findings and descriptive pooled values.
SHA256SUMS.json: hashes for every delivered file other than this manifest itself.
