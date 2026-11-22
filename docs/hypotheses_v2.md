# Pre-registration v2: description length and candidate narrowing

Written after v1's results and after a v2 dev run, before any routing on the v2 test split. The v2 queries, the
length-controlled rewrites, the retrieval settings and the decision rules are frozen by `tests/test_prereg_v2.py`;
the commit that adds this file precedes every `test2` run.

## Why a v2

v1 (`docs/hypotheses.md`, commit `1555eba`) found interference with a small local router (qwen3:4b: FC@5 85.0% at
S1 -> 59.2% at S5) that Haiku-written Skill++ did not prevent (-5.0 pp at S5). Two explanations were left open:
the rewritten descriptions are long (mean 231 characters against 128 for the required skills), and a 3-4B model
reading 157 skills at once may be the bottleneck. v2 tests both on queries nobody has seen results for.

## What is new

- **Fresh test split `test2`.** 120 queries (20 per session, same recipe as v1) built from 160 new phrasings
  (4 per required skill, `srl/catalog_v2.py`), none shared with v1 (`data/queries_v2.json`). v1's dev and test
  queries were v2's dev material. Probes: v1's 88 test probes are reused (descriptive only).
- **Length control.** `data/rewrites/haiku_short.json` redoes only Skill++'s differentiation call with a shorter limit
  (asked 110 characters, accepted up to 130; total with the clause 160), keeping the same reference skill, exclusion
  phrases and names. 8 of 117 skills fell back to the original description. Because the 160-character total leaves
  almost no room for the clause (0.1 phrases on average), the clean length comparison is between the two conditions
  without the clause: `spp_noexcl_haiku` (mean 181 characters) and `spp_noexcl_haiku_short` (mean 113).
- **Candidate narrowing.** Before the router call, the 30 skills whose metadata ("name. first 300 characters of the
  description", under the condition) is most similar to the request by character n-gram TF-IDF are kept and shown in
  an order shuffled per request (`srl/retrieve.py`, conditions with suffix `+r30tfidf`). The router prompt is
  unchanged.

## Dev observations that set the choices (v1 dev + test queries, 156, S5, qwen3:4b)

- Retriever: TF-IDF retrieved all required skills of a query more often than nomic-embed-text (S5, Vanilla metadata:
  94% against 79% at K = 20; 97% against 87% at K = 30), so TF-IDF was chosen.
- K: the smallest K tried whose Vanilla ceiling reached 95% was 30 (97.4%; 93.6% at K = 20). FC@5 was similar at
  both (Vanilla 75.6% and 75.0%; Skill++ 78.2% and 76.9%).
- Length: shorter descriptions did not help: `spp_noexcl_haiku_short` 52.6% against `spp_noexcl_haiku` 58.3%
  (-5.8 pp, 95% CI -12.8 to +0.6) -> V1 is written as "no gain".
- Retrieval: Vanilla rose from 59.6% to 75.0% with K = 20 (+15.4 pp, 95% CI +6.4 to +24.4) -> V2. With retrieval,
  Skill++ was 1.9 to 2.6 pp above Vanilla with intervals including 0 -> V3 keeps the paper's direction.
- Nothing in v1's data, rewrites, prompts or rules was changed.

## Fixed setup

Library, routers, prompt, K = 5 picks, temperature 0 and statistics as in v1. Primary router qwen3:4b; llama3.2:3b
secondary (same statistics, no verdicts). Conditions on `test2`:

- full list, S1-S5 with probes at S5, display order seed 0: `vanilla`, `spp_haiku`, `spp_noexcl_haiku`,
  `spp_noexcl_haiku_short`, `spp_haiku_short`; display order seeds 1 and 2 at S5 for `vanilla`, `spp_noexcl_haiku`,
  `spp_noexcl_haiku_short`;
- with retrieval (top 30, TF-IDF), S1-S5 with probes: `vanilla+r30tfidf`, `spp_haiku+r30tfidf`,
  `spp_noexcl_haiku_short+r30tfidf`, `spp_haiku_short+r30tfidf`;
- llama3.2:3b: `vanilla`, `spp_haiku`, `vanilla+r30tfidf`, `spp_haiku+r30tfidf`.

Full-list comparisons at S5 use each query's FC@5 averaged over the three display orders. Paired bootstrap over the
120 test2 queries (10,000 resamples, seed 0), 95% percentile intervals; exact McNemar on seed-0 outcomes.

## Hypotheses (primary router qwen3:4b, split test2)

**R1 - v1's interference replicates.** Under `vanilla` (full list) FC@5 falls by at least 15 pp from S1 to S5,
interval above 0.

**V1 - shorter descriptions give no gain.** FC@5 at S5 of `spp_noexcl_haiku_short` minus `spp_noexcl_haiku`
(per-query means over 3 orders): the upper bound of the 95% interval is below +5 pp.

**V2 - narrowing helps the small router.** FC@5 at S5 of `vanilla+r30tfidf` minus `vanilla` (full list, mean over 3
orders) is at least 10 pp with the interval above 0.

**V3 - with narrowing, Skill++ beats Vanilla (the paper's direction).** FC@5 at S5 of `spp_haiku+r30tfidf` minus
`vanilla+r30tfidf`, interval above 0.

**V4 - narrowing shrinks the interference.** The S1->S5 fall of `vanilla+r30tfidf` is at most half the full-list fall
and the interval of (full-list fall minus narrowed fall) lies above 0. Judged only if R1 holds.

Reported without verdicts: all FC@5 tables, retrieval ceilings (share of queries whose required skills were all
retrieved), probes hit@5/hit@1, error forms, `spp_haiku_short` conditions, llama3.2:3b, the seed table.
