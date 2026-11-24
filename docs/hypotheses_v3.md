# Pre-registration v3: retrieve on one text, route on another

Written after v2's results and after a v3 dev run, before any routing on the v3 test split. The v3 queries, the
decision code and the retrieval-source rule are frozen by `tests/test_prereg_v3.py`; the commit that adds this file
precedes every `test3` run.

## Why a v3

v2 (`docs/hypotheses_v2.md`, commit `e88776f`) found that narrowing the list to 30 TF-IDF candidates raised a small
router a lot (qwen3:4b: +19.4 pp at S5), while Skill++ was still not clearly better than the original metadata once
the list was narrowed (+2.5 pp, 95% CI -7.5 to +12.5). Exploratory analysis pointed at two effects in opposite
directions: under Skill++ metadata the retriever lost required skills (106 against 115 of 120 queries fully
retrieved; 9 lost, none gained), while on the queries both retrieved fully the router did somewhat better with Skill++
(86 against 78, interval including 0). In v2 the retriever and the router read the same text, so the two effects could
not be separated.

## What is new

- **Fresh test split `test3`.** 120 queries built with v1's and v2's recipe from 160 new phrasings
  (`srl/catalog_v3.py`, `data/queries_v3.json`, seed 20261123). None repeats a v1 or v2 phrasing, and none has a
  character n-gram cosine of 0.75 or more with any earlier phrasing (largest 0.739). Skills, companies and probes
  are v1's; v2's test2 queries are v3's dev material.
- **Retrieval source.** A condition `X+r30tfidf@vanilla` retrieves the top 30 on the original metadata, exactly as
  `vanilla+r30tfidf` does (same candidates, same per-request shuffle), and shows the router condition X's metadata
  for those 30 (`srl/route.py`, `retrieval_source`). The comparison with `vanilla+r30tfidf` therefore changes only
  what the router reads. Without `@`, as in v2, the retriever reads what the router reads.
- **Three seeds for narrowed conditions.** v2 ran each narrowed condition with one candidate shuffle. In v3 every
  condition runs at S5 with seeds 0, 1 and 2 (display order for the full list, candidate shuffle for top 30), and the
  FC@5 comparisons use each query's mean over the three.

## Dev observations (v2's test2, S5, qwen3:4b, seed 0)

- Skill++ (Haiku) shown on the Vanilla candidates (`spp_haiku+r30tfidf@vanilla`): 75.0% against 69.2% for
  `vanilla+r30tfidf` (+5.8 pp, 95% CI -2.5 to +14.2) and 71.7% for `spp_haiku+r30tfidf` (+3.3 pp, -5.8 to +13.3).
- Short Skill++ without the clause shown on the same candidates (`spp_noexcl_haiku_short+r30tfidf@vanilla`): 79.2%
  (+10.0 pp over Vanilla top 30, 95% CI +2.5 to +17.5). This is the best dev configuration and is added as D2, which
  is therefore chosen on dev.
- Incoming-skill probes hit@5 fall when retrieval reads the original metadata: 74/88 against 85/88 for
  `spp_haiku+r30tfidf` (14 lost, 3 gained, p = 0.013): the original descriptions of incoming skills are short and
  mostly vague, so the retriever finds them less often for their own requests.
- Nothing in v1's or v2's data, rewrites, prompts or rules was changed. The retriever code (`srl/retrieve.py`) is
  unchanged; `srl/route.py` gained only the `@` retrieval source.

## Fixed setup

Library, routers, prompt, K = 5 picks, temperature 0, retrieval (top 30, character n-gram TF-IDF) and statistics as in
v2. Primary router qwen3:4b; llama3.2:3b secondary (same statistics, no verdicts). Conditions on `test3`:

- qwen3:4b, S1-S5 with probes at S5, seed 0, and S5 without probes at seeds 1 and 2: `vanilla`,
  `vanilla+r30tfidf`, `spp_haiku+r30tfidf`, `spp_haiku+r30tfidf@vanilla`, `spp_noexcl_haiku_short+r30tfidf@vanilla`;
- llama3.2:3b, S1-S5 with probes at S5, seed 0: the four narrowed conditions.

Paired bootstrap over the 120 test3 queries (10,000 resamples, seed 0), 95% percentile intervals; exact McNemar.
Two hypotheses (D1, D2) test the same baseline; no multiplicity correction is applied, and both are reported.

## Hypotheses (primary router qwen3:4b, split test3)

**R1 - the interference replicates.** Under `vanilla` (full list, seed 0) FC@5 falls by at least 15 pp from S1 to
S5, interval above 0.

**N1 - narrowing helps (v2's V2 again).** FC@5 at S5 of `vanilla+r30tfidf` minus `vanilla`, each the per-query mean
over three seeds, is at least 10 pp with the interval above 0.

**D1 - with the same candidates, Skill++ metadata helps the router.** FC@5 at S5 of `spp_haiku+r30tfidf@vanilla` minus
`vanilla+r30tfidf` (three-seed means): interval above 0.

**D2 - with the same candidates, short Skill++ without the clause helps the router (chosen on dev).** FC@5 at S5 of
`spp_noexcl_haiku_short+r30tfidf@vanilla` minus `vanilla+r30tfidf` (three-seed means): interval above 0.

**D3 - retrieving on the original metadata beats retrieving on Skill++ metadata.** FC@5 at S5 of
`spp_haiku+r30tfidf@vanilla` minus `spp_haiku+r30tfidf` (three-seed means): interval above 0.

**D4 - Skill++ metadata loses required skills at retrieval (v2 finding).** At S5, queries whose required skills are all
among the 30 under the original metadata but not under the Skill++ metadata outnumber the reverse, exact McNemar
p < 0.05.

**D5 - retrieving on the original metadata costs incoming-skill probes.** Probe hit@5 at S5 (seed 0) of
`spp_haiku+r30tfidf@vanilla` against `spp_haiku+r30tfidf`: more probes lost than gained, exact McNemar p < 0.05.

Reported without verdicts: all FC@5 tables, retrieval ceilings, probes, error forms, the seed table, llama3.2:3b.

## Note added after the test3 run (2026-11-24)

"In v3 every condition runs at S5 with seeds 0, 1 and 2" under "What is new" holds for qwen3:4b only; as "Fixed
setup" says, llama3.2:3b ran seed 0 only, so its D1-D3 are printed as "not run" in reports/results_test3.md. The
probes are v1's test probes, as stated above; with the same library, candidates and prompts their replies on test3
were identical to the dev run, so D5 on test3 repeats the dev result. No rule, setting or digest was changed.
