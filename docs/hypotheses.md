# Pre-registration: hypotheses and decision rules

Written after the dev split and before any test-split routing. Data, rewrites, prompts and decision code are frozen
by digests in `tests/test_prereg.py`; the commit that adds this file precedes every test run.

## Question

As a library of finance-analysis skills grows with similar skills, does a small local router (qwen3:4b, thinking
off) lose required skills it used to find, and does rewriting only the incoming skills' names and descriptions
(Skill++, arXiv:2611.00544) prevent it? Does the answer depend on who writes the rewrite (Claude Haiku 5.5 versus
qwen3:4b), and do the "Does not cover" clauses help or hurt a small router?

## Fixed setup

- Library: 40 required + 117 incoming skills; S0 20 skills, then 48, 76, 104, 131, 157 at S1-S5.
- Test split: 120 queries (20 per session, 1-3 required skills each); 88 incoming-skill probes.
- Router: one call, the whole skill list (ID | name | first 300 characters of the description) followed by the
  request, JSON schema with the installed IDs, K = 5, temperature 0, seed 0, display order seed 0 (shuffled once per
  checkpoint, same in every condition).
- Conditions (only incoming skills differ): `vanilla`, `spp_haiku`, `spp_noexcl_haiku`, `spp_noname_haiku`,
  `bodydist_haiku`, `spp_qwen3_4b`.
- Primary router: qwen3:4b. Secondary routers (reported with the same statistics, no verdicts): llama3.2:3b, and
  Claude Haiku 5.5 on `vanilla` and `spp_haiku`.
- Statistics: FC@5 at checkpoint c over all queries released at S0..Sc. Paired bootstrap over test queries,
  10,000 resamples, seed 0, 95% percentile intervals; exact two-sided McNemar on paired FC@5.

## Hypotheses and decision rules (primary router qwen3:4b)

**H1 - interference.** Under `vanilla`, FC@5 falls by at least 15 pp from S1 to S5.
Statistic: FC@5(S1) - FC@5(S5), bootstrap over the 120 test queries (each resample recomputes both rates).
Holds if the point estimate is >= 15 pp and the 95% interval lies above 0. Reported alongside: the 40 queries
released by S1 scored at S1 versus S5 (exact McNemar), and how many queries released S0-S4 that were correct at
their first checkpoint fail at S5.

**H2 - Skill++ (Haiku-written) prevents at least half of the fall.**
Share = [FC@5(spp_haiku, S5) - FC@5(vanilla, S5)] / [FC@5(vanilla, S1) - FC@5(vanilla, S5)].
Holds if share >= 0.5 and the paired S5 difference spp_haiku - vanilla has a 95% interval above 0.
Not judged if the Vanilla fall is below 5 pp.

**H3 - a small writer gains at most half as much.** Gain = FC@5(condition, S5) - FC@5(vanilla, S5).
Holds if gain(spp_qwen3_4b) <= 0.5 x gain(spp_haiku). Judged only if gain(spp_haiku) >= 5 pp with a 95% interval
above 0.

**H4 - exclusion clauses pull the small router toward the excluding skill.**
Pairs: (test query q, incoming skill D) where D's Haiku-written Skill++ description keeps an exclusion phrase
written for a skill that q requires. Pull rate = share of pairs where D is among the 5 selected IDs at S5.
Holds if pull(spp_haiku) - pull(spp_noexcl_haiku) has a 95% interval above 0 (bootstrap over queries, pairs
clustered by query). If the interval lies below 0, the result is reported as the clause pushing the router away
(the paper's intended effect).

## Hypotheses added after the dev split (same router, same statistics)

The dev run (below) contradicted the paper's direction for qwen3:4b, so three directional hypotheses taken from
dev are tested on the held-out test queries:

**H5 - Skill++ (Haiku-written) lowers FC@5 at S5.** Holds if the paired 95% interval of
FC@5(spp_haiku, S5) - FC@5(vanilla, S5) lies below 0.

**H6 - the exclusion clause is what costs FC@5.** Holds if the paired 95% interval of
FC@5(spp_noexcl_haiku, S5) - FC@5(spp_haiku, S5) lies above 0.

**H7 - Skill++ makes incoming skills easier to select for their own work (plasticity, as in the paper).** On the 88
test probes at S5, hit@5 is higher under spp_haiku than under vanilla and the exact McNemar p < 0.05.

## Reported without verdicts

FC@5 by checkpoint and its S1-S5 mean; Recall@5; stability (queries released before S5) and plasticity (queries
released at S5) at S5; incoming-skill probes hit@5 and hit@1 for every condition; S5 error forms typed by code; the
no-name and Body-distilled conditions (Skill++ minus Body-distilled is the paper's main rewriting baseline); incoming
skills among the 5 selected; display-order seeds 1 and 2 for `vanilla` and `spp_haiku` at S5 (qwen3:4b); the rate
of replies with fewer than 5 distinct IDs; the overlap check between synthetic and evaluation queries; Claude spend.

No result on the test split will change the data, rewrites, prompts or rules. If a run fails, it is resumed with the
same inputs; if a condition cannot be completed, it is reported as missing.

## Dev split observations that shaped this file

36 dev queries and 29 dev probes, all six conditions, qwen3:4b, llama3.2:3b and Claude Haiku 5.5 (two conditions).

- qwen3:4b, Vanilla: FC@5 100.0 / 77.8 / 58.3 / 56.7 / 61.1% at S1-S5; 6 of the 20 queries released S0-S4 that were
  correct at their first checkpoint failed at S5. This kept H1 as proposed.
- qwen3:4b at S5: Skill++ (Haiku) 47.2%, Skill++ without exclusions 61.1%, Skill++ with original names 47.2%,
  Body-distilled (Haiku) 55.6%, Skill++ written by qwen3:4b 61.1% (S1-S5 mean 76.9% against Vanilla 70.8%).
  The full Skill++ was 13.9 pp below Vanilla (paired 95% CI -27.8 to 0.0) -> H5, H6.
- Rewrites made incoming skills far easier to select for their own probes: hit@5 13/29 (Vanilla) against 22/29
  (Skill++ Haiku), McNemar p = 0.035 -> H7.
- The H4 pull measure showed no difference on dev (108 pairs: 6 picks with the clause, 5 without).
- Errors under Skill++ moved from substitution to crowding and to picks unrelated to the query, and replies with
  fewer than 5 distinct IDs rose from 2/149 to 14/149. Haiku-written descriptions are long (mean 231 characters with
  the clause, 181 without, against 60 for the original incoming descriptions and 128 for the required skills); the S5
  skill list grows from about 4,200 to 8,500 prompt tokens.
- Claude Haiku 5.5 as the router was at the ceiling on dev (Vanilla 100% at every checkpoint; Skill++ 97.2% at S5),
  so it is kept as a secondary anchor only.
- llama3.2:3b (secondary): Vanilla 91.7 / 77.8 / 54.2 / 30.0 / 30.6% at S1-S5; Skill++ (Haiku) 91.7 / 77.8 / 25.0 /
  26.7 / 25.0%. Its other four dev conditions finished after this file was committed and did not shape it.
- Nothing in the data, rewrites or prompts was changed after the dev results. One dev-time decision came before any
  routing: the reference similarity stayed character n-gram TF-IDF after a comparison with nomic-embed-text (see
  docs/paper_notes.md).
