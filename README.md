# skill-route-lite

**Does rewriting only the new skills' names and descriptions (Skill++) keep a small local router on track as a
finance skill library grows?** A small, pre-registered check of
[Skill++ (arXiv:2611.00544)](https://arxiv.org/abs/2611.00544) on 157 synthetic financial-analysis skills, with
qwen3:4b and llama3.2:3b as routers and Claude Haiku 5.5 as the rewriter (and as a third router).

## Result in short

Primary router qwen3:4b (thinking off), 120 held-out test queries, library growing from 48 skills (S1) to 157 (S5).

- **Interference showed up.** With the original metadata (Vanilla), FC@5 (all required skills among the 5 picked)
  fell from 85.0% at S1 to 59.2% at S5: a fall of 25.8 pp (95% CI 11.7 to 38.9). Of the 40 queries released by S1,
  16 were routed correctly at S1 and wrongly at S5, 2 the other way (exact McNemar p = 0.0013). llama3.2:3b fell from
  72.5% to 35.0%.
- **Skill++ written by Claude Haiku 5.5 did not prevent it.** At S5 it scored 54.2%, 5.0 pp below Vanilla
  (95% CI -14.2 to +4.2). For llama3.2:3b it was 9.2 pp below Vanilla (95% CI -16.7 to -1.7).
- **Display order mattered as much as the rewrite.** Re-shuffling the skill list (two extra seeds) moved Vanilla
  at S5 between 45.8% and 59.2%, and the Skill++ minus Vanilla difference between -10.0 and +1.7 pp. Under order
  seed 1 the difference was -10.0 pp with an interval below 0 (95% CI -18.3 to -2.5, McNemar p = 0.023), so the H5
  verdict below depends on the display order.
- **What Skill++ did do: new skills became much easier to find for their own work.** Incoming skills were in the
  top 5 for their own probe request 79 of 88 times under Skill++ against 41 under Vanilla (38 gained, 0 lost), in
  the direction of the paper's plasticity result. Body-distilled rewrites did about as well (78 of 88), and the
  original incoming descriptions were short and mostly vague by design (mean 60 characters; 44 of the 65 "similar"
  skills), so this gain comes from replacing weak descriptions rather than from Skill++'s contrastive parts.
- **The writer may matter (exploratory).** Skill++ written by qwen3:4b itself scored 65.0% at S5, 10.8 pp above the
  Haiku-written version (95% CI 3.3 to 18.3, McNemar p = 0.011) and 5.8 pp above Vanilla (95% CI -2.5 to +14.2). This
  comparison was not pre-registered, it did not show with llama3.2:3b (+3.3 pp, 95% CI -3.3 to +10.0), and the
  qwen3:4b-written descriptions are also shorter (152 against 231 characters).
- **"Does not cover" clauses did not pull the router toward the excluding skill.** Over 308 (query, excluding
  skill) pairs, the excluding skill was picked 14 times with the clause and 14 times without it. Dropping the clauses
  did not change FC@5 significantly either: +3.3 pp (95% CI -5.0 to +11.7).
- **Claude Haiku 5.5 as the router had no interference to fix**: Vanilla 99.2% at S5, Skill++ 99.2%.

In this setting the router that suffered from a growing library (a 3-4B local model) did not benefit from Skill++
written by a stronger model, and the router that would read such rewrites well (Haiku 5.5) did not need them. The
paper reports gains for five API routers on a library of 731 skills; this study does not test that setting.

## Pre-registered decisions (qwen3:4b)

Hypotheses H1-H4 come from the project proposal, written before this study (not part of this repository). H5 and H6
were added after the dev split showed the opposite of the paper's direction, and H7 after dev showed a plasticity
gain. All seven were committed with frozen data digests (commit `1555eba`) before any test-split routing. Full text: [docs/hypotheses.md](docs/hypotheses.md). Statistics: paired bootstrap over test queries (10,000
resamples, seed 0) and exact McNemar.

| | Hypothesis | Rule | Result | Verdict |
|---|---|---|---|---|
| H1 | Vanilla FC@5 falls >= 15 pp from S1 to S5 | point >= 15 pp, CI above 0 | +25.8 pp [11.7, 38.9] | holds |
| H2 | Haiku-written Skill++ recovers >= half of that fall | share >= 0.5, S5 gain CI above 0 | gain -5.0 pp [-14.2, +4.2]; share -0.19 | not supported |
| H3 | qwen3:4b-written Skill++ gains <= half the Haiku-written gain | judged only if the Haiku gain is >= 5 pp with CI above 0 | Haiku gain -5.0 pp | not judged |
| H4 | Exclusion clauses pull the router toward the excluding skill | pick-rate difference CI above 0 | 4.5% vs 4.5%, +0.0 pp [-1.8, +1.8] | not supported |
| H5 | Haiku-written Skill++ lowers FC@5 at S5 | S5 difference CI below 0 | -5.0 pp [-14.2, +4.2] | not supported |
| H6 | Dropping the exclusion clause raises FC@5 at S5 | difference CI above 0 | +3.3 pp [-5.0, +11.7] | not supported |
| H7 | Skill++ makes incoming skills easier to select for their own probe | higher hit@5, McNemar p < 0.05 | 41/88 -> 79/88, p < 0.0001 | holds |

The same statistics for the secondary routers (no verdicts counted): llama3.2:3b - H1, H5 and H7 hold; H2, H4 and H6
do not; H3 is not judged. Claude Haiku 5.5 (run on Vanilla and Skill++ only) - H1 does not hold (fall 0.8 pp), H2 is
not judged, H5 does not hold, H7 holds (81/88 -> 88/88, p = 0.016).

## Results

FC@5 (%) on the 120 test queries, display order seed 0. Each checkpoint scores every query released so far
(40, 60, 80, 100, 120 queries); the library has 48, 76, 104, 131 and 157 skills.

**qwen3:4b**

| Condition | S1 | S2 | S3 | S4 | S5 | Mean S1-S5 | Recall@5 at S5 | Probe hit@5 |
|---|---|---|---|---|---|---|---|---|
| Vanilla | 85.0 | 56.7 | 53.8 | 61.0 | 59.2 | 63.1 | 72.5 | 41/88 |
| Body-distilled (Haiku) | 72.5 | 48.3 | 48.8 | 55.0 | 58.3 | 56.6 | 71.5 | 78/88 |
| Skill++ (Haiku) | 77.5 | 45.0 | 48.8 | 52.0 | 54.2 | 55.5 | 68.8 | 79/88 |
| Skill++ without exclusions (Haiku) | 77.5 | 46.7 | 56.3 | 56.0 | 57.5 | 58.8 | 72.2 | 77/88 |
| Skill++ with original names (Haiku) | 80.0 | 43.3 | 46.3 | 52.0 | 53.3 | 55.0 | 68.5 | 80/88 |
| Skill++ (written by qwen3:4b) | 82.5 | 58.3 | 63.8 | 62.0 | 65.0 | 66.3 | 76.5 | 68/88 |

**llama3.2:3b** (often repeats IDs: 127 to 192 of 488 replies per condition held fewer than 5 distinct IDs)

| Condition | S1 | S2 | S3 | S4 | S5 | Mean S1-S5 | Probe hit@5 |
|---|---|---|---|---|---|---|---|
| Vanilla | 72.5 | 53.3 | 37.5 | 37.0 | 35.0 | 47.1 | 28/88 |
| Body-distilled (Haiku) | 77.5 | 50.0 | 31.3 | 30.0 | 20.8 | 41.9 | 56/88 |
| Skill++ (Haiku) | 57.5 | 50.0 | 27.5 | 26.0 | 25.8 | 37.4 | 49/88 |
| Skill++ without exclusions (Haiku) | 72.5 | 56.7 | 30.0 | 27.0 | 29.2 | 43.1 | 52/88 |
| Skill++ with original names (Haiku) | 52.5 | 45.0 | 27.5 | 25.0 | 29.2 | 35.8 | 55/88 |
| Skill++ (written by qwen3:4b) | 72.5 | 58.3 | 38.8 | 31.0 | 29.2 | 46.0 | 48/88 |

**Claude Haiku 5.5 as the router**

| Condition | S1 | S2 | S3 | S4 | S5 | Probe hit@5 | Probe hit@1 |
|---|---|---|---|---|---|---|---|
| Vanilla | 100.0 | 100.0 | 100.0 | 98.0 | 99.2 | 81/88 | 54/88 |
| Skill++ (Haiku) | 100.0 | 100.0 | 100.0 | 100.0 | 99.2 | 88/88 | 88/88 |

**Display order** (qwen3:4b, S5, the same 120 queries)

| Order seed | Vanilla | Skill++ (Haiku) | Difference [95% CI] |
|---|---|---|---|
| 0 (pre-registered) | 59.2 | 54.2 | -5.0 [-14.2, +4.2] |
| 1 | 56.7 | 46.7 | -10.0 [-18.3, -2.5] |
| 2 | 45.8 | 47.5 | +1.7 [-7.5, +10.8] |

**Where the required skills went** (qwen3:4b, S5). Each required skill missing from the 5 picks gets one type, decided
by code from the generator's labels (the paper used model judges). *Substitution*: a picked incoming skill was
written to resemble the missing one. *Crowding*: no such skill was picked, but a generic helper or a look-alike of
another required skill of the query was. *Other*: none of these; the router picked skills unrelated to the missing
one. As in the paper's Table A3, "other" is counted apart from crowding.

| Condition | Missing skills | Substitution | Crowding (duplicate + generic) | Other |
|---|---|---|---|---|
| Vanilla | 73 | 16 | 38 (13 + 25) | 19 |
| Body-distilled (Haiku) | 77 | 25 | 19 (12 + 7) | 33 |
| Skill++ (Haiku) | 80 | 16 | 23 (11 + 12) | 41 |
| Skill++ (qwen3:4b) | 63 | 13 | 19 (10 + 9) | 31 |

The paper reports that Skill++ cut substitution from 46.0% to 6.5% of the Vanilla errors, crowding from 41.5% to
20.0% and others from 12.5% to 4.5%. Here Skill++ (Haiku) cut crowding from 38 to 23 missing skills (52% to 32% of the
Vanilla errors, a 39% cut against the paper's 52%), left substitution at 16 and more than doubled "other" (19 to 41).
The two "other" columns are not the same category: the paper's Others first takes possible substitutes found by its
judges, while "other" here is what is left when no look-alike or generic skill was picked.

Full tables, dev results and every statistic: [reports/results_test.md](reports/results_test.md),
[reports/results_dev.md](reports/results_dev.md). Every routing decision: `reports/routing_test.csv` and
`reports/routing_dev.csv`.

## Compared with the paper

| | Paper (Haiku 4.5 router, SRA-Bench) | Here (qwen3:4b router, synthetic finance skills) |
|---|---|---|
| Vanilla FC@5, first -> last checkpoint | 92.5% (S1) -> 36.4% (S9) | 85.0% (S1) -> 59.2% (S5) |
| Skill++ at the last checkpoint | 76.3% (+39.9 pp) | 54.2% (-5.0 pp) |
| Body-distilled at the last checkpoint | 44.4% | 58.3% |
| Incoming skills found for their own requests | rank 1: 56.9% vs 51.9% | hit@1: 69/88 vs 24/88; hit@5: 79/88 vs 41/88 |

The interference the paper describes is visible with small local routers, and incoming skills became much easier
to find after rewriting, as in the paper (though Body-distilled did as well here). The stability gain did not
reproduce in this setting: fewer crowding errors were offset by more picks unrelated to the query. Things that differ and could
explain it (none of them tested separately):

- **Description length.** Required skills keep their original descriptions (mean 128 characters). Haiku's Skill++
  descriptions of the incoming skills average 231 characters (181 without the clause), against 60 for the original
  incoming descriptions. The S5 skill list grows from about 4,200 to 8,500 prompt tokens, and replies with fewer than
  5 distinct IDs rose from 18 to 30 of 488 for qwen3:4b. The qwen3:4b-written rewrites are shorter (mean 152
  characters) and did better.
- **Router.** One call returning 5 IDs from a 3-4B model, instead of the paper's two-call harness (shortlist 10,
  rerank) on API models.
- **Library and queries.** 157 skills and 120 queries joined from phrasings, all written for this study, against 731
  web-collected skills and 198 real coding tasks.
- **Reference choice.** Similarity is character n-gram TF-IDF instead of MiniLM and Qwen3-Embedding. The nearest
  earlier skill was the one an incoming skill was written to resemble for 52 of 107 Haiku rewrites (51 for
  qwen3:4b), and that skill was among the three exclusion references for 76 of 107 (72).
- **Exclusion clauses are short here.** After the paper's rules (drop phrases that contain a reference's name head,
  trim to 298 characters), Haiku-written descriptions kept 0.79 phrases on average and 39 of 117 kept none.

More detail: [docs/paper_notes.md](docs/paper_notes.md).

## What was built

**Skills.** 157 synthetic skills for financial analysis in a Korean-market setting (English text), written one by one
for this study with Claude Code (not generated from templates).
40 *required* skills are the ones evaluation queries need (trailing P/E, P/B, EV/EBITDA, WACC, dividend yield, rights
offerings, convertible bonds, margins, interest coverage, free cash flow, moving averages, beta, rebalancing, bond
YTM, 5% stake reports, foreign flows, peer tables, FX translation, DART statements, earnings surprise and others).
117 *incoming* skills arrive later and no query needs them. Every skill has a name, a short description (what the
router reads) and a body (what a rewriter reads). Incoming skills come in six kinds, labelled in the data:

| Kind | n | Example |
|---|---|---|
| similar (other work in the same area; description vague or specific) | 65 | `forward-pe` (consensus EPS) next to `trailing-pe` (reported EPS) |
| same name (another market, source or scope) | 21 | a second `trailing-pe` for US stocks from 10-Q diluted EPS |
| name only (shares a word, different work) | 6 | `margin-balance-monitor` (retail margin loans) next to `operating-margin-trend` |
| overclaiming (description promises the target's work; body does less) | 10 | `roe-analyzer` claims a DuPont breakdown, computes one ROE figure |
| broad toolkit (claims a whole area; body is an overview) | 5 | `valuation-multiples-toolkit` |
| generic helper | 10 | `finance-analysis-assistant` |

**Growth.** S0 installs 20 required skills; each of S1-S5 installs 4 new required skills and then 22-24 incoming
skills, giving 20, 48, 76, 104, 131 and 157 skills. Within a session the required skills come first, then the
incoming skills in a seeded order. Each addition is one Skill++ step that sees all earlier skills.

**Queries.** Each session releases 20 test and 6 dev queries, built by joining one to three phrasings of
required skills (four test and two dev phrasings per skill, never shared) with a company name. From S1 on, 12 of the
20 test queries need one of the session's new skills. Each incoming skill also has one probe request of its own
(88 test, 29 dev), to check that a rewrite does not hide it from its own work.

**Routers.** qwen3:4b (thinking off) and llama3.2:3b through Ollama, context 10,240 tokens; Claude Haiku 5.5 on two
conditions with prompt caching. One call reads every installed skill as `ID | name | first 300 characters of the
description`, then the request, and is asked for 5 IDs. For the local models a JSON schema requires exactly 5 items
from the installed IDs (temperature 0, seed 0); the schema cannot forbid repeats, so some replies hold fewer than 5
distinct IDs. Claude's structured outputs do not take a length limit; its first 5 distinct IDs are used. The display
order is shuffled once per checkpoint and is the same in every condition.

**Conditions.** Only incoming skills change; required skills keep their original metadata, as in the paper's main
study. `vanilla`; `bodydist_haiku` (description rewritten from the skill's own body); `spp_haiku` (Skill++);
`spp_noexcl_haiku` (without the "Does not cover" clause); `spp_noname_haiku` (with the original name);
`spp_qwen3_4b` (Skill++ with qwen3:4b as the writer).

**Skill++ as implemented** ([srl/rewrite.py](srl/rewrite.py), after Sec. 3.2 and Appendix A of the paper). For each
incoming skill, in addition order, using the original records of earlier skills (the TF-IDF weights behind every
similarity are fitted once on all 157 skills' original texts and the writer's synthetic queries):
1. The reference is the earlier skill most similar by name and description.
2. The writer produces a description of at most 220 characters from the incoming skill's body. It leads with what the
   reference lacks and never names it (3 tries; otherwise the original description is kept).
3. Three earlier skills, ranked by the paper's fused rank of three similarities (two use up to 8 synthetic queries
   per skill, one compares names and descriptions), each get a short "Does not cover" phrase. Phrases containing a
   reference's name head are dropped and the clause is trimmed from the end to 298 characters.
4. If the incoming name contains the head of an earlier name, the writer proposes a qualified name, kept if it has
   4-60 characters. Haiku gave all 58 conflicting skills a new name; qwen3:4b returned the original name for 14 of
   the 58 (the paper's rule checks only the length, so those count as accepted).

Each writer also wrote its own synthetic queries. They rank exclusion references and are part of the TF-IDF fit;
the router never sees them. The closest one to any evaluation query or probe
has a character n-gram cosine of 0.80 (Haiku) and 0.87 (qwen3:4b); two per writer are at 0.8 or above
([reports/overlap_check.json](reports/overlap_check.json)).

## Process

1. Dev split first: 36 queries and 29 probes; qwen3:4b and llama3.2:3b on all six conditions, Claude Haiku 5.5 on
   Vanilla and Skill++. Four of the llama3.2:3b dev conditions finished just after the pre-registration commit.
2. Hypotheses, decision rules and data digests committed before any test routing
   ([docs/hypotheses.md](docs/hypotheses.md), [tests/test_prereg.py](tests/test_prereg.py), commit `1555eba`).
   No data, rewrite or prompt changed after the dev results; H5-H7, their decision code and one descriptive metric
   (incoming skills among the 5 picks) were added after dev. Nothing frozen changed after the commit. Later code
   changes only touch reporting: half-up rounding of table cells, the display-order table, and "other" errors shown
   apart from crowding.
3. Test split routed by a detached launcher that ran without restarting. One qwen3:4b call (query t042, Skill++
   written by qwen3:4b, S3) took 15.9 hours overnight before it returned; two other calls took 36 and 69 minutes.
   Per-block median call times were 3.1-3.8 s for qwen3:4b, except one block at 8.3 s, and 2.5-2.9 s for llama3.2:3b.
4. An independent audit of this README (next section).

## Limitations

- Synthetic skills and queries, written with Claude Code in the same work as the pipeline. Rewrites never saw
  evaluation queries, and nothing was tuned on test queries, but the skill set reflects one view of what is confusable.
- 120 test queries. Differences of about 5 pp are inside the noise, and display order alone moved Vanilla at S5 by
  13.3 pp (55 to 71 of 120 queries).
- The bootstrap treats queries as independent, but test queries reuse phrasings (232 uses of 160 phrasings, up to 4
  times each), so the intervals may be somewhat narrow.
- One router call instead of the paper's two; none of the paper's retrieval baselines (R&R, CC-Pages) were run;
  library 157 skills, not 731.
- H5-H7 were written after the dev run, so they are confirmatory only for the test split.
- Error types come from the generator's labels, not from judges; "other" is a catch-all.
- llama3.2:3b often repeats IDs (127 to 192 of 488 replies per condition held fewer than 5 distinct IDs).
- Claude Haiku 5.5 was the rewriter instead of the paper's Gemini 3.5 Flash-Lite (with Gemini 3.6 Flash for retries
  and DeepSeek-V4-Flash for synthetic queries); here one model did all of it, with up to 3 tries. Haiku used default
  sampling, so a rerun of the rewrites would differ. The rewrites used here are committed.

## Cost

Claude Haiku 5.5, all calls: $0.2244 (rewrites $0.0654, router dev $0.0414, router test $0.1174, one smoke-test call
$0.0002), under a $3 cap enforced in code. Prices: $0.10 / $0.50 per million input / output tokens; cache reads 0.1x
and cache writes 1.25x the input price.
Local models ran on a laptop RTX 2060 (6 GB).

## Reproduce

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m srl route --router qwen3:4b --split test --conds vanilla,spp_haiku,spp_noexcl_haiku,spp_noname_haiku,bodydist_haiku,spp_qwen3_4b
.venv\Scripts\python -m srl report --split test
```

The committed rewrites in `data/rewrites/` are what the results use. To regenerate them:
`python -m srl rewrite --gen qwen3:4b` and `python -m srl rewrite --gen haiku` (needs `ANTHROPIC_API_KEY`; spend capped
by `SRL_BUDGET`, default $3). `python -m srl build` rebuilds `data/*.json` from the catalog in `srl/catalog_*.py`.

## Files

| Path | What |
|---|---|
| `srl/catalog_required.py`, `srl/catalog_incoming.py` | The skills, phrasings and probes written for this study |
| `srl/build.py` | Sessions, display IDs, queries, probes -> `data/*.json` |
| `srl/rewrite.py` | Skill++ and Body-distilled |
| `srl/route.py` | The router call |
| `srl/metrics.py`, `srl/stats.py`, `srl/prereg.py`, `srl/report.py` | Scores, statistics, pre-registered decisions, tables |
| `data/rewrites/` | Haiku- and qwen3:4b-written rewrites, with every call's usage |
| `reports/` | Result tables, routing decisions (CSV), overlap check |
| `runs/route/` | Raw router replies with token counts and timings (needed by `srl report`) |
| `docs/` | Hypotheses and paper notes |

## Audit

Before publication, an agent that had not written this README checked it against the raw run files, the data, the
code, the git history and the paper's text. It recomputed 344 numbers with its own scripts and reviewed 65 claims.
Two numbers were wrong (a 13.4 pp that is 13.3 pp, and table cells rounded inconsistently) and 22 statements were
corrected or qualified, the largest being that "other" errors had been counted as crowding in a comparison with the
paper. Each finding was rechecked against the raw files before the fix. Coverage: all 144 run blocks complete, the CSVs
match the raw runs (7,312 test and 2,086 dev rows).

Paper: Zhang et al., "Skill++: Towards Lifelong Agents via Routing-Aware Skill Refinement", arXiv:2611.00544. The
paper links no code repository; nothing from the paper's benchmark data is used here. Code: MIT License.
