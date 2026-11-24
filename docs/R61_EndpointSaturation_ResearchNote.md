# 99a R61 - Source-Specific Endpoint-Saturation Research Note
Date: 2026-11-24
Status: EXPLORATORY ORIGINAL EMPIRICAL CONTRAST / NOT A DEPLOYABLE SCREENING POLICY
Parent baseline: R60, frozen and unchanged
Research branch: research/99a-r61-originality

## Claim being tested
Does perfect coverage of a narrow published final-report-linked endpoint distinguish
archived three-run screening portfolios that vary in coverage of the original
human-retain-for-full-text endpoint?

The two source reference sets are nested but answer different questions.
H: 113 records retained by human reviewers for full-text assessment.
F: 23 report-linked record IDs in the source's final-inclusion crosswalk.
F is not a complete adjudication of all excluded source records, and H
does not independently establish clinical eligibility.

## Source lock and calculation
Upstream: Matsui and Takaesu (2026), Information 17(11), 1160.
Original repository commit: d911eafc5299aa3ca41a6aacf0167931c81fcbbc.
Input: 4527 records, 59 runs, 267093 predictions, two reviews, eight
archived configurations; source-pinned SHA256 fingerprints are checked
in the executable scripts (reused from the R60 frozen implementation).
Jev probabilities use the source archived 0.50 cutoff.
All C(59,3)=32509 subsets are enumerated without model retraining.

## Exact newly computed observations
- 32505/32509 (99.9876957150%) triples cover F=23.
- 243/32509 (0.7474853118%) triples cover H=112, the highest attainable
  coverage of 113 source human-retained IDs in these fixed decisions.
- 32262/32505 (99.2524227042%) F-complete triples cover fewer than 112 H.
- Among F-complete triples, H ranges from 95 to 112.
- The smallest forward queue among F-complete triples is 256 records, H=103.
- The H-maximizing hindsight oracle with smallest queue is H=112, 483 forwarded.
  Only two triples simultaneously achieve H=112 and <=483 forwarded.
- The label-blind greedy maximum-new-Includes heuristic obtains H=112 and F=23,
  but forwards 644 records. The inverse-frequency heuristic forwards 630.
  Both methods inspect all 59 original decisions, so they are not tested
  savings in model execution cost or a prospective deployment policy.

Composition-restricted source tests:
- Three different source configurations: 20377 triples; all F=23; only
  234 attain H=112; H ranges from 104 to 112.
- Exactly one Jev run (50 choices), one GPT-5 mini (6) and one GPT-6 Astra (3):
  900 triples; all F=23; 117 attain H=112; H ranges from 105 to 112.
  These are three different model families, but their recorded source corpus
  is the same and they must not be treated as 900 independent experiments.

## Mechanism, independent check and mathematical audit
F vote-support: 19/23 IDs are Included by every one of the 59 runs and
four have at least 40 Include votes. H vote-support: 60/113 are Included by
all runs; 43 by 40-58 runs; ten by fewer than 40, including one by zero.
The expected number of retrieved reference IDs for a uniformly chosen
three-run subset is the elementary counting identity
sum(i in R) [1 - C(59-v_i,3) / C(59,3)].
Its exact computed values are 22.999815435725488 for F and
109.12599587806451 for H, matching the exhaustive family.

A separately coded set-union verifier checks all 32509 joint (F,H)
counts, witness workload extrema and the composition-restricted families.
The source-dependent GitHub Actions workflow reports PASS and uploads
ONLY aggregate derived JSON, not the original record-level model outputs.

## Literature and originality boundary
Chan et al. (2025), Research Synthesis Methods, DOI 10.1017/rsm.2025.1,
already provided three-stage screening labels. Hilkenmeier et al. (2026),
Systematic Reviews, DOI 10.1186/s13643-026-03228-4, already studied
full model agreement. Chang and Zhang (2026), arXiv:2611.12705, already
established important limitations of inference from agreement and
selective judgment. Matsui and Takaesu (2026), DOI 10.3390/info17111160,
supplied the original saved model decisions and described complete
final-report retention for certain constituent runs.

R61 DOES NOT claim a new set-cover theorem, a new screening algorithm,
a novel principle that reference stages differ, an unbiased estimate of
true recall or new independently sampled model runs.
The bounded original contribution is an exactly counted, source-pinned
counterexample to treating perfect final-report-ID coverage as a
discriminating evaluation endpoint across a declared portfolio family.

## Decision and limitations
Recommended for a brief Results contribution plus a transparent
Supplementary Methods table in the R61 author-review manuscript.
Not sufficient alone to claim an externally generalizable method or
a safe automation policy. Repeated-run dependence, reference accuracy,
threshold choice, transport, and missing direct human time remain limits.
A second source with paired pre-full-text and final-report labels plus
multiple source-available model decisions is needed before promoting the
result to a wider generalization claim.
