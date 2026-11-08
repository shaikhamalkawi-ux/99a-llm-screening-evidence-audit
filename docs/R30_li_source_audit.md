# R30 — Li (2026) final publisher report source gate

## Identity and provenance

- DOI: `10.1016/j.ijmedinf.2025.106205`, *International Journal of Medical Informatics* 207 (2026), article 106205.
- Title: *AI-assisted literature screening: A hybrid approach using large language models and retrieval-augmented generation*.
- Author: Yiming Li et al. The publisher PDF is 11 pages, downloaded to the restricted user Drive. Its SHA-256 and exact publisher filename are recorded in `data/R30_li_final_publisher_article_1.csv`.
- The online-first date printed on page 1 is 24 November **2025**; the volume year is **2026**. Do not confuse the online article date with the future PubMed Central open-access release.

## Source-entered outcomes, not a new experiment

- The main labeled corpus contains **6,331** titles/abstracts: **113 positive** and **6,218 negative** expert labels (PDF pp. 2-3). The authors reuse a corpus from Du et al.; this is not 6,331 independent human trials.
- Three named LLMs and three prompt configurations were considered, along with preprocessing rules, a sentence-embedding baseline, and ensembles. The best rule+DeepSeek-R1 Prompt II individual setting is reported with **precision 0.34, recall 0.77, NPV 1.00 (displayed), g-mean 0.87** in the journal abstract. These are metrics against the corpus reference, not human-time measurements.
- The paper reports **workload reduction 94–98%** for some settings in Figs. 3–5 and their Results text (PDF pp. 5-8). It does not log a matched human team's full person-time, or the downstream review effort and rework. Treat this number as authors' screening workload/filtering metric, *not observed net staff-hour saving*. Do not substitute model throughput for reviewer labor.
- Recall 0.77 explicitly permits missed labeled relevant reports. A rounded NPV of 1.00 cannot be read as a zero-false-negative guarantee in an imbalanced data set with 1.8% positives.
- The 10-topic generalization test uses **327 labeled records** from a separate prior RefAI dataset (PDF p. 5 and Table 2), not 10 additional independent screening experiments. The paper reports overall DeepSeek-R1 F1 0.93 and accuracy 0.88 on that test; cross-task samples and metrics are not comparable without reference alignment.
- Rule-based filtering includes EHR-data cues and temporal extraction; the authors themselves warn that preprocessing may drop relevant papers (PDF p. 10). End-to-end evidence retention through all stages is not established merely by the output-classification score.
- The provided Prompt II text requests objective/dataset/model/results from the title/abstract (PDF pp. 4-5). The article calls this RAG; the displayed prompts alone do not establish retrieval of *additional externally indexed full texts* for every screening decision.

## Closed retrieval gate, still open scientific interpretation

The R20 60-ID access register remains frozen. The R28 source overlay admitted Zhang, Insuk and Cao, R29 Janoudi (plus its scientific supplement), and R30 this Li final article. Source checks now total **54**: 50 provisionally empirical and four contextual. The five former journal-version holds are all closed. Remaining 4 provisional scope exclusions, one abstract-only and one linked duplicate mean there are not 60 unique full empirical studies. The separate 21-investigation interpretive core is *unchanged*. Source access does not establish final study inclusion, a complete database search, or a pooled workload effect.

All values here were transcribed from the publisher PDF and verified for source identity. These tests validate consistency of **entered metadata and declared calculations**, not model re-execution. No third-party PDF is redistributed through GitHub or the Overleaf package.
