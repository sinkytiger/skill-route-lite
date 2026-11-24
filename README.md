# skill-route-lite

**Does rewriting only the new skills' names and descriptions (Skill++) keep a small local router on track as a
finance skill library grows?** A small, pre-registered check of
[Skill++ (arXiv:2611.00544)](https://arxiv.org/abs/2611.00544) on 157 synthetic financial-analysis skills, with
qwen3:4b and llama3.2:3b as routers and Claude Haiku 5.5 as the rewriter (and as a third router).

A second, separately pre-registered round on fresh queries ([v2](#v2-shorter-descriptions-and-candidate-narrowing))
tested shorter Skill++ descriptions and a retrieval step that shows the router 30 candidates instead of the whole
library. Narrowing the list helped the small router; shortening the descriptions did not show a clear effect either
way, and with narrowing Skill++ was still not clearly better than the original metadata. A third round
([v3](#v3-retrieve-on-the-original-text-route-on-skill)) showed the router the same 30 candidates with either the
original or the Skill++ metadata: narrowing again helped a lot (+30.0 pp), while Skill++ metadata did not clearly help
the router choose (+1.9 pp, interval including 0).

## Result in short (v1)

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

## Pre-registered decisions (v1, qwen3:4b)

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

## Results (v1)

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
explain it (none tested separately in v1; [v2](#v2-shorter-descriptions-and-candidate-narrowing) tests the first,
and for the second adds a step that narrows the list before the same one-call router; it does not test the paper's
two-call harness or API routers):

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

## v2: shorter descriptions and candidate narrowing

v1 left two explanations open: Haiku's Skill++ descriptions are long, and a 3-4B model reading the whole library in
one call may be the bottleneck. v2 tests both on 120 fresh test queries (`test2`), built with v1's recipe from 160
new phrasings, none repeating a v1 phrasing ([srl/catalog_v2.py](srl/catalog_v2.py), `data/queries_v2.json`; the
skills and company names are v1's, and some phrasings are close paraphrases of v1's). The queries were committed in
`3dd714d` and frozen by digest together with the hypotheses and rules in `e88776f`
([docs/hypotheses_v2.md](docs/hypotheses_v2.md), [tests/test_prereg_v2.py](tests/test_prereg_v2.py)), after a dev
run on v1's dev and test queries and before any `test2` routing. The library, the routers, the prompt and the
statistics are v1's.

- **Shorter descriptions.** Only Skill++'s differentiation call was redone with a shorter limit (asked for 110
  characters, accepted up to 130, 5 tries), keeping the same reference skills, exclusion phrases and names
  ([srl/rewrite_v2.py](srl/rewrite_v2.py), `data/rewrites/haiku_short.json`); 8 of 117 skills fell back to their
  original description. The 160-character total leaves almost no room for the "Does not cover" clause (0.1 phrases
  per skill), so the length comparison is between the two conditions without the clause: incoming descriptions of
  181 characters on average against 110 (all 117 incoming skills; [docs/hypotheses_v2.md](docs/hypotheses_v2.md)
  gives 113 for the short ones, the mean over the 109 that did not fall back).
- **Candidate narrowing.** Before the router call, the 30 skills whose "name. description" is most similar to the
  request by character n-gram TF-IDF are kept and shown in an order shuffled per request
  ([srl/retrieve.py](srl/retrieve.py), conditions ending in `+r30tfidf`). The router prompt is unchanged. At S5 the
  prompt shrinks from about 4,150 tokens (Vanilla) and 8,530 (Skill++) to about 1,090 and 1,800. TF-IDF and K = 30
  were chosen on dev: TF-IDF retrieved all required skills more often than nomic-embed-text, and of the two K tried
  (20 and 30) only 30 gave a Vanilla ceiling of at least 95% (97.4% against 93.6%).

### v2 result in short (qwen3:4b, test2)

- **Interference replicated on fresh queries.** Vanilla FC@5 fell from 85.0% at S1 to 55.8% at S5 (fall 29.2 pp,
  95% CI 15.5 to 41.9).
- **Narrowing the list helped the small router.** With 30 retrieved candidates Vanilla scored 69.2% at S5, 19.4 pp
  above the full list averaged over three display orders (49.7%; 95% CI +10.8 to +27.8). Against each order alone the
  gain was +13.3, +20.0 and +25.0 pp. The S1 to S5 fall was 13.3 pp with narrowing against 29.2 pp without, but the
  interval of the difference (+15.8 pp, 95% CI -0.1 to +32.1) reaches below 0, so the pre-registered V4 is not
  supported.
- **Shorter descriptions showed no clear effect.** Short minus long, without the clause, mean of three orders:
  +2.8 pp (95% CI -1.9 to +7.8); order by order 0.0, +8.3 and 0.0 pp. On dev (v1's 156 queries, order seed 0 only)
  it had been -5.8 pp (95% CI -12.8 to +0.6). The pre-registered "no gain" needed the upper bound below +5 pp, so it
  is not supported, and no gain was shown either.
- **With narrowing, Skill++ was not clearly better than Vanilla**: 71.7% against 69.2% at S5 (+2.5 pp, 95% CI -7.5
  to +12.5). One cost is clear (exploratory, not pre-registered): under Skill++ metadata the retriever missed a
  required skill more often. All required skills were among the 30 for 106 of 120 queries against 115 under Vanilla
  (9 queries lost, none gained, exact McNemar p = 0.004); Vanilla answered 5 of those 9 correctly. On the 106
  queries both retrieved fully, Skill++ was ahead, 86 against 78 correct (+7.5 pp, 95% CI -2.8 to +17.9, McNemar
  p = 0.22), a direction only; the two conditions also showed partly different candidates (16.2 of 30 shared on
  average, with 22.1 incoming skills among each 30 under Skill++ against 14.5 under Vanilla).
- **New skills stayed easy to find.** With narrowing, incoming skills were in the top 5 for their own probe 85 of
  88 times under Skill++ against 58 under Vanilla (27 gained, 0 lost). The full-list probe results (79 against 41)
  are not a new measurement: the S5 library, display order and probe prompts are v1's, and the replies were the
  same as in v1 for all 88 probes.
- **llama3.2:3b (secondary, no verdicts) showed the same pattern.** Vanilla fell from 67.5% at S1 to 31.7% at S5
  (fall 35.8 pp, 95% CI 20.4 to 50.8). With narrowing it scored 60.0% at S5, 28.3 pp above the full list (95% CI
  +20.0 to +36.7; llama3.2:3b ran one display order, so this compares seed 0 only). On the full list Skill++ was
  9.2 pp below Vanilla (95% CI -16.7 to -2.5); with narrowing the two were level (59.2% against 60.0%, -0.8 pp,
  95% CI -10.8 to +9.2).

| | Hypothesis (qwen3:4b, test2) | Rule | Result | Verdict |
|---|---|---|---|---|
| R1 | Vanilla (full list) falls >= 15 pp from S1 to S5 | point >= 15 pp, CI above 0 | +29.2 pp [15.5, 41.9] | holds |
| V1 | Shorter Skill++ descriptions give no gain (without the clause, S5, mean of 3 orders) | upper CI bound below +5 pp | +2.8 pp [-1.9, +7.8] | not supported |
| V2 | Narrowing to 30 candidates raises Vanilla at S5 (against the 3-order mean) | point >= 10 pp, CI above 0 | +19.4 pp [10.8, 27.8] | holds |
| V3 | With narrowing, Skill++ beats Vanilla at S5 | CI above 0 | +2.5 pp [-7.5, +12.5] | not supported |
| V4 | Narrowing halves the S1 to S5 fall | narrowed fall <= half the full-list fall, and CI of the difference above 0 | 13.3 against 29.2 pp; difference +15.8 pp [-0.1, +32.1] | not supported |

V4 met its first condition (13.3 <= 14.6) and missed the second by the interval's lower end.

FC@5 (%) on test2, qwen3:4b, display order seed 0 (the retrieval conditions shuffle the 30 candidates per request
with seed 0). "All required retrieved" is the share of the 120 queries whose required skills were all among the 30
at S5.

| Condition | S1 | S2 | S3 | S4 | S5 | S5, mean of 3 orders | Probe hit@5 | All required retrieved |
|---|---|---|---|---|---|---|---|---|
| **Full list** | | | | | | | | |
| Vanilla | 85.0 | 41.7 | 55.0 | 61.0 | 55.8 | 49.7 | 41/88 | |
| Skill++ (Haiku) | 87.5 | 46.7 | 46.3 | 52.0 | 47.5 | | 79/88 | |
| Skill++ without exclusions | 85.0 | 41.7 | 40.0 | 47.0 | 51.7 | 47.5 | 77/88 | |
| Skill++ without exclusions, short | 85.0 | 48.3 | 58.8 | 52.0 | 51.7 | 50.3 | 71/88 | |
| Skill++, short | 85.0 | 43.3 | 56.3 | 50.0 | 52.5 | | 73/88 | |
| **Top 30 retrieved** | | | | | | | | |
| Vanilla | 82.5 | 78.3 | 75.0 | 70.0 | 69.2 | | 58/88 | 95.8% |
| Skill++ (Haiku) | 90.0 | 78.3 | 72.5 | 70.0 | 71.7 | | 85/88 | 88.3% |
| Skill++ without exclusions, short | 82.5 | 73.3 | 73.8 | 72.0 | 75.8 | | 80/88 | 91.7% |
| Skill++, short | 77.5 | 83.3 | 77.5 | 72.0 | 71.7 | | 84/88 | 90.8% |

Display order again moved the full-list results: Vanilla at S5 was 55.8%, 49.2% and 44.2% under order seeds 0, 1
and 2. With narrowing, fewer required skills went missing at S5 (Vanilla: 75 to 46) and crowding fell from 33 to 10,
while substitution by a look-alike rose from 13 to 23; in 21 of those 23 the missing skill was itself among the 30
candidates, so the router saw both and picked the look-alike.

**llama3.2:3b** on test2 (display order seed 0). The retrieved candidates are the same as for qwen3:4b, since the
retriever does not depend on the router. As with qwen3:4b, the full-list probe replies are the same as in v1.

| Condition | S1 | S2 | S3 | S4 | S5 | Probe hit@5 | Replies with fewer than 5 distinct IDs |
|---|---|---|---|---|---|---|---|
| Vanilla, full list | 67.5 | 55.0 | 38.8 | 34.0 | 31.7 | 28/88 | 151/488 |
| Skill++ (Haiku), full list | 62.5 | 58.3 | 27.5 | 22.0 | 22.5 | 49/88 | 215/488 |
| Vanilla, top 30 retrieved | 80.0 | 61.7 | 65.0 | 64.0 | 60.0 | 58/88 | 56/488 |
| Skill++ (Haiku), top 30 retrieved | 77.5 | 60.0 | 66.3 | 67.0 | 59.2 | 84/88 | 80/488 |

**What v2 adds to v1.** In this setting cutting the list changed FC@5 far more than the tested shortening, which
also removed far fewer prompt tokens (at S5, narrowing cut the Vanilla prompt from about 4,150 to 1,090 tokens;
shortening cut the Skill++ prompt without the clause from about 7,380 to 5,880). Narrowing raised Vanilla at S5 from
49.7% (mean of three orders) to 69.2%, against 85.0% at S1. Within the narrowed list Skill++ may help the router
choose (the 106-query comparison points that way but its interval includes 0), but its rewritten descriptions made
the retriever miss required skills more often, and the net difference was +2.5 pp with an interval including 0.
The paper's routers are API models with a two-call harness; whether its retrieval baselines would change this was
not tested.

Tables and pre-registered decisions: [reports/results_test2.md](reports/results_test2.md). The exploratory figures
in this section (the llama3.2:3b differences, the 9 lost queries, the 106-query comparison, candidate overlap,
21 of 23, prompt sizes) were computed from the raw runs and are not in that file. Every routing decision:
`reports/routing_test2.csv` (v2 test, with the candidates count and whether all required skills were shown) and
`reports/routing_v2dev.csv` (the v2 dev runs on v1's queries).

## v3: retrieve on the original text, route on Skill++

In v2 the retriever and the router read the same metadata. Exploratory analysis there suggested two effects in
opposite directions: Skill++ metadata made the retriever miss required skills, while on the queries both conditions
retrieved fully the router did somewhat better with Skill++ (interval including 0). v3 separates the two on 120 fresh
test queries (`test3`, 160 new phrasings in [srl/catalog_v3.py](srl/catalog_v3.py); none repeats a v1 or v2
phrasing, and the largest character n-gram cosine with an earlier phrasing is 0.739). The hypotheses were committed
with frozen digests (commit `52d28d9`, [docs/hypotheses_v3.md](docs/hypotheses_v3.md),
[tests/test_prereg_v3.py](tests/test_prereg_v3.py)) after a dev run on v2's test2 queries and before any `test3`
routing. Library, routers, prompt, retriever (top 30, TF-IDF) and statistics are v2's.

- **Retrieval source.** A condition `X+r30tfidf@vanilla` retrieves the top 30 on the original metadata, getting the
  same candidates in the same per-request order as `vanilla+r30tfidf`, and shows the router condition X's metadata for
  those 30 ([srl/route.py](srl/route.py), `retrieval_source`). Compared with `vanilla+r30tfidf`, only what the router
  reads changes.
- **Three seeds at S5 (qwen3:4b).** Every qwen3:4b condition also ran at S5 with seeds 1 and 2 (display order for the
  full list, candidate shuffle for top 30), and the S5 FC@5 comparisons (N1, D1-D3) use each query's mean over the
  three seeds. S1-S4, the probes, R1, D4, D5 and llama3.2:3b use seed 0.

### v3 result in short (qwen3:4b, test3)

- **Narrowing again helped a lot.** At S5, Vanilla with 30 candidates scored 72.8% against 42.8% on the full list
  (both means of three seeds): +30.0 pp (95% CI +23.6 to +36.7). The full-list fall replicated (seed 0: 75.0% at S1 to 50.0%
  at S5, 25.0 pp, CI 10.8 to 38.9). With narrowing, Vanilla was 72.5% at S1 and 71.7% at S5 (seed 0; a fall of
  0.8 pp, CI -14.2 to +14.9; not pre-registered).
- **With the same candidates, Skill++ metadata did not clearly help the router.** 74.7% against 72.8% (+1.9 pp,
  95% CI -2.8 to +6.4); seed by seed +1.7, -1.7 and +5.8 pp. The short Skill++ without the clause, the best
  configuration on dev (+10.0 pp there, one seed), gave +1.4 pp (CI -3.3 to +6.1).
- **Separating retrieval from routing did not clearly beat v2's setup.** Skill++ shown, retrieved on the original
  metadata: 74.7%; retrieved on the Skill++ metadata: 70.8% (+3.9 pp, CI -1.4 to +9.7).
- **The retrieval loss replicated on fresh queries.** Under Skill++ metadata all required skills were among the 30
  for 108 of 120 queries, against 114 under the original metadata (6 lost, none gained, exact McNemar p = 0.031).
  Retrieval does not depend on the router.
- **Retrieving on the original metadata costs the new skills' own requests, but this was not tested afresh.**
  Probe hit@5 was 74/88 against 85/88 (14 lost, 3 gained, p = 0.013). The probes are v1's test probes, and with the
  same library, candidates and prompts the replies on test3 were the same as in the dev run for all 88 probes. D5
  holds by its rule but repeats the dev result; the pre-registration did not note this.
- llama3.2:3b (secondary, seed 0 only, no verdicts): Skill++ shown on Vanilla's candidates 60.8% against 55.0%
  (+5.8 pp, CI -1.7 to +13.3); Skill++ retrieved on its own metadata 62.5% (+7.5 pp over Vanilla, CI -1.7 to +16.7).

| | Hypothesis (qwen3:4b, test3) | Rule | Result | Verdict |
|---|---|---|---|---|
| R1 | Vanilla (full list) falls >= 15 pp from S1 to S5 | point >= 15 pp, CI above 0 | +25.0 pp [10.8, 38.9] | holds |
| N1 | Narrowing to 30 candidates raises Vanilla at S5 (three-seed means) | point >= 10 pp, CI above 0 | +30.0 pp [23.6, 36.7] | holds |
| D1 | Same candidates: Skill++ metadata shown beats original metadata shown | CI above 0 | +1.9 pp [-2.8, +6.4] | not supported |
| D2 | Same candidates: short Skill++ without the clause beats original (chosen on dev) | CI above 0 | +1.4 pp [-3.3, +6.1] | not supported |
| D3 | Skill++ shown: retrieving on original metadata beats retrieving on Skill++ metadata | CI above 0 | +3.9 pp [-1.4, +9.7] | not supported |
| D4 | Skill++ metadata loses required skills at retrieval | lost > gained, p < 0.05 | 6 lost, 0 gained, p = 0.031 | holds |
| D5 | Retrieving on original metadata costs incoming-skill probes | lost > gained, p < 0.05 | 14 lost, 3 gained, p = 0.013 | holds (same replies as dev) |

FC@5 (%) on test3, qwen3:4b, seed 0 for S1-S5. "All required retrieved" is the share of the 120 queries whose required
skills were all among the 30 at S5.

| Condition | S1 | S2 | S3 | S4 | S5 | S5, mean of 3 seeds | Probe hit@5 | All required retrieved |
|---|---|---|---|---|---|---|---|---|
| Vanilla, full list | 75.0 | 46.7 | 51.3 | 50.0 | 50.0 | 42.8 | 41/88 | |
| Vanilla, top 30 | 72.5 | 86.7 | 75.0 | 69.0 | 71.7 | 72.8 | 58/88 | 95.0% |
| Skill++ (Haiku), top 30 retrieved on Skill++ metadata | 80.0 | 81.7 | 70.0 | 69.0 | 70.0 | 70.8 | 85/88 | 90.0% |
| Skill++ (Haiku), top 30 retrieved on original metadata | 75.0 | 83.3 | 75.0 | 67.0 | 73.3 | 74.7 | 74/88 | 95.0% |
| Short Skill++ without the clause, retrieved on original metadata | 77.5 | 85.0 | 73.8 | 70.0 | 70.8 | 74.2 | 70/88 | 95.0% |

The probe column repeats earlier runs: on the full list the replies are v1's, and with narrowing they are those of
v2's test2 runs and the v3 dev runs (same prompts, temperature 0). Display order again moved the full list a lot:
Vanilla at S5 was 50.0%, 45.0% and 33.3% under seeds 0, 1 and 2, while with narrowing the three candidate shuffles
gave 71.7%, 74.2% and 72.5%.

**llama3.2:3b** on test3 (seed 0; the candidates are the same as for qwen3:4b):

| Condition | S1 | S2 | S3 | S4 | S5 | Probe hit@5 | Replies with fewer than 5 distinct IDs |
|---|---|---|---|---|---|---|---|
| Vanilla, top 30 | 75.0 | 68.3 | 63.8 | 60.0 | 55.0 | 58/88 | 49/488 |
| Skill++ (Haiku), retrieved on Skill++ metadata | 72.5 | 70.0 | 56.3 | 54.0 | 62.5 | 84/88 | 71/488 |
| Skill++ (Haiku), retrieved on original metadata | 75.0 | 63.3 | 72.5 | 59.0 | 60.8 | 76/88 | 66/488 |
| Short Skill++ without the clause, retrieved on original metadata | 75.0 | 63.3 | 66.3 | 64.0 | 60.0 | 76/88 | 67/488 |

As for qwen3:4b, the probe replies of the two rows retrieved on their own metadata repeat v2's test2 runs. The two rows
retrieved on the original metadata are new measurements (llama3.2:3b had no v3 dev run): 76/88 against 84/88 for
Skill++ retrieved on its own metadata (11 lost, 3 gained, exact McNemar p = 0.057), the same direction as D5 without
reaching p < 0.05.

**What v3 adds.** Once the list is narrowed to 30 candidates, the rewritten descriptions did not clearly help a 3-4B
router choose among the same candidates (+1.9 pp, interval -2.8 to +6.4), and the gains seen in the dev run on v2's
test2 queries (+5.8 and +10.0 pp, one seed) were not confirmed (+1.9 and +1.4 pp here).
Narrowing itself was again the largest effect measured (+30.0 pp). Where the retriever reads Skill++ metadata, it
misses required skills more often (replicated); where it reads the original metadata, it finds the new skills less
often for their own requests (seen on the same probes as dev). On these queries neither choice changed FC@5 clearly.

Tables and pre-registered decisions: [reports/results_test3.md](reports/results_test3.md). The per-seed and llama3.2:3b
differences and the narrowed Vanilla fall above were computed from the raw runs and are not in that file; it prints
"not run" for llama3.2:3b D1-D3 because those rules need three seeds and llama3.2:3b ran seed 0 only. Every routing decision:
`reports/routing_test3.csv` and `reports/routing_v3dev.csv` (the v3 dev runs on test2).

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
   Checked later against the Windows event log, all three spanned sleeps of the laptop (2026-11-20 17:00 to
   2026-11-21 08:53, 09:36 to 10:11 and 12:29 to 13:38); each returned a normal reply.
   Per-block median call times were 3.1-3.8 s for qwen3:4b, except one block at 8.3 s, and 2.5-2.9 s for llama3.2:3b.
4. An independent audit of this README (next section).
5. v2: length-controlled rewrites and the retrieval step built and tried on v1's dev and test queries (S5 only); the
   test2 queries (committed in `3dd714d`) were frozen by digest together with the rules in `e88776f`, before any
   test2 routing. test2 was routed by
   the same detached launcher from 2026-11-22 15:18. During the llama3.2:3b runs the launcher and the local Ollama
   server stopped at about 20:41, when the laptop went to sleep until 07:24 the next morning (Windows event log; the
   run logs show no error); the run resumed that morning from the saved block
   state (written every 5 requests), and the partly finished block continued from its 40 saved requests.
6. v3: the retrieval-source option built and a dev run on v2's test2 queries (S5, qwen3:4b, seed 0) started; the
   test3 queries were written while it ran; then the hypotheses, decision code and digests were committed (`52d28d9`)
   before any test3 routing. test3 was routed from 2026-11-23 16:22. One call (query w013, Vanilla top 30, S4)
   spanned a sleep of the laptop from 17:00 to 19:59 (Windows event log) and returned a normal reply after 10,749 s
   of wall-clock time. The run stopped at 21:16 when the laptop logged off and went to sleep (power source change,
   logoff, sleep), resumed on 2026-11-24 at 07:50 from the saved block state and finished at 11:54.

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
- llama3.2:3b often repeats IDs: replies with fewer than 5 distinct IDs were 127 to 192 of 488 per condition in v1,
  and on test2 151 and 215 on the full list, 56 and 80 with narrowing.
- Claude Haiku 5.5 was the rewriter instead of the paper's Gemini 3.5 Flash-Lite (with Gemini 3.6 Flash for retries
  and DeepSeek-V4-Flash for synthetic queries); here one model did all of it, with up to 3 tries. Haiku used default
  sampling, so a rerun of the rewrites would differ. The rewrites used here are committed.
- v2: the test2 phrasings were written after v1's results were known (before any test2 routing) and use the same
  skills; the retriever and K were chosen on v1's queries; test2 reuses v1's 88 test probes. The retrieval
  conditions were run with one candidate shuffle (seed 0), while the full-list Vanilla in V2 is the mean of three
  display orders. The 106-query comparison and the other unlabelled differences in the v2 section are exploratory.
- v2's retriever is character n-gram TF-IDF over names and descriptions; the paper's retrieval baselines were still
  not run.
- v3: the test3 phrasings were written after v2's results were known (before any test3 routing) and use the same
  skills and companies (233 uses of 160 phrasings, up to 2 each). The probes are v1's test probes again, so D5
  repeats the dev result rather than testing it. D2's configuration was chosen on dev, and D1 and D2 share one
  baseline with no multiplicity correction. llama3.2:3b ran one seed.

## Cost

Claude Haiku 5.5, all calls: $0.3431 under a $3 cap enforced in code. v1: $0.2244 (rewrites $0.0654, router dev
$0.0414, router test $0.1174, one smoke-test call $0.0002). v2: $0.1187 for the short rewrites over four runs (three
earlier runs that enforced 110 characters exactly fell back to the original description for 58 to 64 of 117 skills;
they are kept in `data/rewrites/archive/` and cost $0.1027, the final run $0.0160). v2 and v3 routing used only local models; v3 made no Claude calls. Prices: $0.10 / $0.50 per million input / output tokens; cache reads 0.1x
and cache writes 1.25x the input price.
Local models ran on a laptop RTX 2060 (6 GB).

## Reproduce

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m srl route --router qwen3:4b --split test --conds vanilla,spp_haiku,spp_noexcl_haiku,spp_noname_haiku,bodydist_haiku,spp_qwen3_4b
.venv\Scripts\python -m srl report --split test
.venv\Scripts\python -m srl route --router qwen3:4b --split test2 --conds vanilla,spp_haiku,vanilla+r30tfidf,spp_haiku+r30tfidf
.venv\Scripts\python -m srl.report_v2 test2
.venv\Scripts\python -m srl.export test2
.venv\Scripts\python -m srl route --router qwen3:4b --split test3 --conds vanilla+r30tfidf,spp_haiku+r30tfidf@vanilla
.venv\Scripts\python -m srl.report_v3 test3
.venv\Scripts\python -m srl.export test3
```

The full lists of v2 and v3 runs (conditions, seeds, llama3.2:3b) are in [docs/hypotheses_v2.md](docs/hypotheses_v2.md)
and [docs/hypotheses_v3.md](docs/hypotheses_v3.md) under "Fixed setup". `python -m srl.build_v3` rebuilds
`data/queries_v3.json`.

The committed rewrites in `data/rewrites/` are what the results use. To regenerate them:
`python -m srl rewrite --gen qwen3:4b` and `python -m srl rewrite --gen haiku` (needs `ANTHROPIC_API_KEY`; spend capped
by `SRL_BUDGET`, default $3). `python -m srl build` rebuilds `data/skills.json`, `queries.json` and `probes.json` from the catalog in
`srl/catalog_*.py`; `python -m srl.build_v2` rebuilds `data/queries_v2.json`, and `python -m srl.rewrite_v2` redoes
the short Haiku rewrites after the existing `data/rewrites/haiku_short.json` is moved aside (it resumes from that
file and skips skills already in it; needs the API key, as above).

## Files

| Path | What |
|---|---|
| `srl/catalog_required.py`, `srl/catalog_incoming.py` | The skills, phrasings and probes written for this study |
| `srl/build.py` | Sessions, display IDs, queries, probes -> `data/*.json` |
| `srl/rewrite.py` | Skill++ and Body-distilled |
| `srl/route.py` | The router call |
| `srl/metrics.py`, `srl/stats.py`, `srl/prereg.py`, `srl/report.py` | Scores, statistics, pre-registered decisions, tables |
| `srl/catalog_v2.py`, `srl/build_v2.py` | v2 phrasings -> `data/queries_v2.json` (test2) |
| `srl/rewrite_v2.py` | v2 length-controlled Skill++ -> `data/rewrites/haiku_short.json` |
| `srl/retrieve.py` | v2 candidate narrowing (TF-IDF; nomic-embed-text was compared on dev) |
| `srl/prereg_v2.py`, `srl/report_v2.py` | v2 pre-registered decisions and tables |
| `srl/catalog_v3.py`, `srl/build_v3.py` | v3 phrasings -> `data/queries_v3.json` (test3) |
| `srl/prereg_v3.py`, `srl/report_v3.py` | v3 pre-registered decisions and tables (the `@` retrieval source is in `srl/route.py`) |
| `srl/export.py` | Routing decisions -> `reports/routing_*.csv` |
| `srl/dashboard_data.py` | Data files for a v2/v3 results dashboard (`python -m srl.dashboard_data <out_dir>`, add `--v3` for test3), from the raw runs |
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

The v2 parts were audited the same way by an agent that had not written them, in two passes (the qwen3:4b part;
then llama3.2:3b, the generated report and CSV, and a re-read of the fixes). It recomputed 632 numbers (202 and
430; numbers in fixed sentences were checked again) and reviewed 55 claims. Of 18 findings, two were about numbers
(two spend figures truncated instead of rounded; candidate counts taken over all 120 queries in a sentence about
106) and 16 about statements, the largest being that the 106-query comparison was written as an effect and that
the full-list probe results repeat v1's replies exactly. Each finding was rechecked against the raw files before
the fix ([docs/claims_audit_v2.json](docs/claims_audit_v2.json)). Coverage: all 71 test2 blocks complete;
`routing_test2.csv` (7,064 rows) and `routing_v2dev.csv` (936 rows) match the raw runs.

The v3 parts were audited by another agent that had not written them. It recomputed 490 numbers (165 in the README,
303 cells of `reports/results_test3.md`, 22 in `docs/hypotheses_v3.md`) and compared `routing_test3.csv` (5,592 rows)
and `routing_v3dev.csv` (416 rows) field by field with the raw runs; no number was wrong. Of 38 claims, 10 had
problems: 8 were fixed in this README, one (the seeds sentence of the pre-registration) got a dated note in
`docs/hypotheses_v3.md`, and one (llama3.2:3b verdict lines in the report, already marked "no verdict counted")
needed no change. The largest was that the 10,749 s call spanned a sleep of the laptop. Its further note that v1's
15.9-hour, 36- and 69-minute calls and v2's 20:41 stop line up with sleeps in the Windows event log was checked
against the event log and the call times and added to the Process section
([docs/claims_audit_v3.json](docs/claims_audit_v3.json)). Coverage: all 55 test3 blocks complete.

Paper: Zhang et al., "Skill++: Towards Lifelong Agents via Routing-Aware Skill Refinement", arXiv:2611.00544. The
paper links no code repository; nothing from the paper's benchmark data is used here. Code: MIT License.
