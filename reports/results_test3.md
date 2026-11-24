# v3 results: test3 split

### Router qwen3:4b: FC@5 (%) by checkpoint

| Condition | S1 (n=40) | S2 (n=60) | S3 (n=80) | S4 (n=100) | S5 (n=120) | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 75.0 | 46.7 | 51.3 | 50.0 | 50.0 | 54.6 | 67.5 | 50.0 / 50.0 | 13/488 |
| vanilla+r30tfidf | 72.5 | 86.7 | 75.0 | 69.0 | 71.7 | 75.0 | 85.0 | 67.0 / 95.0 | 4/488 |
| spp_haiku+r30tfidf | 80.0 | 81.7 | 70.0 | 69.0 | 70.0 | 74.1 | 83.3 | 69.0 / 75.0 | 3/488 |
| spp_haiku+r30tfidf@vanilla | 75.0 | 83.3 | 75.0 | 67.0 | 73.3 | 74.7 | 86.3 | 71.0 / 85.0 | 3/488 |
| spp_noexcl_haiku_short+r30tfidf@vanilla | 77.5 | 85.0 | 73.8 | 70.0 | 70.8 | 75.4 | 84.2 | 69.0 / 80.0 | 7/488 |

### Router qwen3:4b: interference, incoming-skill probes and S5 error forms

| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | other | top types |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 17 of 56 (of 100) | 41/88 | 24/88 | 2.64 | 83 | 24 | 37 | 22 | generic_crowding 25, other 22, duplicate_crowding 12 |
| vanilla+r30tfidf | 16 of 74 (of 100) | 58/88 | 43/88 | 1.88 | 37 | 23 | 7 | 7 | similar 9, description_inconsistency 9, other 7 |
| spp_haiku+r30tfidf | 12 of 72 (of 100) | 85/88 | 79/88 | 2.42 | 43 | 26 | 6 | 11 | similar 17, other 11, similar_same_name 7 |
| spp_haiku+r30tfidf@vanilla | 19 of 78 (of 100) | 74/88 | 70/88 | 1.68 | 32 | 15 | 2 | 15 | other 15, similar 10, description_inconsistency 4 |
| spp_noexcl_haiku_short+r30tfidf@vanilla | 17 of 77 (of 100) | 70/88 | 65/88 | 1.57 | 38 | 13 | 6 | 19 | other 19, similar 8, duplicate_crowding 6 |

### Router qwen3:4b: share of queries whose required skills were all retrieved (top 30, %)

| Condition | S1 | S2 | S3 | S4 | S5 |
|---|---|---|---|---|---|
| vanilla+r30tfidf | 100.0 | 100.0 | 97.5 | 94.0 | 95.0 |
| spp_haiku+r30tfidf | 100.0 | 96.7 | 88.8 | 85.0 | 90.0 |
| spp_haiku+r30tfidf@vanilla | 100.0 | 100.0 | 97.5 | 94.0 | 95.0 |
| spp_noexcl_haiku_short+r30tfidf@vanilla | 100.0 | 100.0 | 97.5 | 94.0 | 95.0 |

### Router qwen3:4b: FC@5 at S5 by seed (%; display order for the full list, candidate shuffle for top 30)

| Condition | seed 0 | seed 1 | seed 2 | mean |
|---|---|---|---|---|
| vanilla | 50.0 | 45.0 | 33.3 | 42.8 |
| vanilla+r30tfidf | 71.7 | 74.2 | 72.5 | 72.8 |
| spp_haiku+r30tfidf | 70.0 | 73.3 | 69.2 | 70.8 |
| spp_haiku+r30tfidf@vanilla | 73.3 | 72.5 | 78.3 | 74.7 |
| spp_noexcl_haiku_short+r30tfidf@vanilla | 70.8 | 72.5 | 79.2 | 74.2 |

### Router llama3.2:3b: FC@5 (%) by checkpoint

| Condition | S1 (n=40) | S2 (n=60) | S3 (n=80) | S4 (n=100) | S5 (n=120) | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |
|---|---|---|---|---|---|---|---|---|---|
| vanilla+r30tfidf | 75.0 | 68.3 | 63.8 | 60.0 | 55.0 | 64.4 | 72.9 | 55.0 / 55.0 | 49/488 |
| spp_haiku+r30tfidf | 72.5 | 70.0 | 56.3 | 54.0 | 62.5 | 63.1 | 80.1 | 61.0 / 70.0 | 71/488 |
| spp_haiku+r30tfidf@vanilla | 75.0 | 63.3 | 72.5 | 59.0 | 60.8 | 66.1 | 77.1 | 60.0 / 65.0 | 66/488 |
| spp_noexcl_haiku_short+r30tfidf@vanilla | 75.0 | 63.3 | 66.3 | 64.0 | 60.0 | 65.7 | 77.9 | 60.0 / 60.0 | 67/488 |

### Router llama3.2:3b: interference, incoming-skill probes and S5 error forms

| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | other | top types |
|---|---|---|---|---|---|---|---|---|---|
| vanilla+r30tfidf | 25 of 70 (of 100) | 58/88 | 37/88 | 1.89 | 70 | 39 | 17 | 14 | similar 16, duplicate_crowding 14, other 14 |
| spp_haiku+r30tfidf | 12 of 60 (of 100) | 84/88 | 74/88 | 2.51 | 55 | 22 | 15 | 18 | other 18, similar 16, duplicate_crowding 14 |
| spp_haiku+r30tfidf@vanilla | 17 of 67 (of 100) | 76/88 | 62/88 | 1.66 | 61 | 24 | 17 | 20 | other 20, duplicate_crowding 17, similar 12 |
| spp_noexcl_haiku_short+r30tfidf@vanilla | 15 of 67 (of 100) | 76/88 | 60/88 | 1.70 | 59 | 24 | 13 | 22 | other 22, similar 13, duplicate_crowding 11 |

### Router llama3.2:3b: share of queries whose required skills were all retrieved (top 30, %)

| Condition | S1 | S2 | S3 | S4 | S5 |
|---|---|---|---|---|---|
| vanilla+r30tfidf | 100.0 | 100.0 | 97.5 | 94.0 | 95.0 |
| spp_haiku+r30tfidf | 100.0 | 96.7 | 88.8 | 85.0 | 90.0 |
| spp_haiku+r30tfidf@vanilla | 100.0 | 100.0 | 97.5 | 94.0 | 95.0 |
| spp_noexcl_haiku_short+r30tfidf@vanilla | 100.0 | 100.0 | 97.5 | 94.0 | 95.0 |

## v3 pre-registered decisions (docs/hypotheses_v3.md)

### qwen3:4b (primary)

**R1** the interference replicates on fresh queries
- Vanilla (full list) FC@5: S1 75.0% -> S5 50.0%; fall +25.0 pp [95% CI +10.8, +38.9].
- **R1 holds** (rule: fall >= 15 pp and interval above 0).

**N1** narrowing to 30 candidates raises Vanilla
- Vanilla top 30 (mean of 3 shuffles, 72.8%) minus Vanilla full list (mean of 3 orders, 42.8%), S5: +30.0 pp [95% CI +23.6, +36.7].
- **N1 holds** (rule: gain >= 10 pp and interval above 0).

**D1** with the same candidates, Skill++ metadata helps the router
- Same 30 candidates: Skill++ (Haiku) metadata shown (74.7%) minus original metadata shown (72.8%), S5, mean of 3 shuffles: +1.9 pp [95% CI -2.8, +6.4].
- **D1 not supported** (rule: interval above 0).

**D2** with the same candidates, short Skill++ without the clause helps the router
- Same 30 candidates: short Skill++ without the clause shown (74.2%) minus original metadata shown (72.8%), S5, mean of 3 shuffles: +1.4 pp [95% CI -3.3, +6.1].
- **D2 not supported** (rule: interval above 0).

**D3** retrieving on the original metadata beats retrieving on Skill++ metadata
- Skill++ shown, retrieved on original metadata (74.7%) minus retrieved on Skill++ metadata (70.8%), S5, mean of 3 shuffles: +3.9 pp [95% CI -1.4, +9.7].
- **D3 not supported** (rule: interval above 0).

**D4** Skill++ metadata loses required skills at retrieval (v2 finding)
- S5, all required skills among the 30: original metadata 114/120, Skill++ metadata 108/120; lost 6, gained 0, exact McNemar p = 0.0312.
- **D4 holds** (rule: more lost than gained, p < 0.05).

**D5** retrieving on the original metadata costs incoming-skill probes
- Incoming-skill probes hit@5 with Skill++ shown: retrieved on original metadata 74/88, on Skill++ metadata 85/88; lost 14, gained 3, exact McNemar p = 0.0127.
- **D5 holds** (rule: more lost than gained, p < 0.05).

### llama3.2:3b (secondary, no verdict counted)

**D1** with the same candidates, Skill++ metadata helps the router
- not run

**D2** with the same candidates, short Skill++ without the clause helps the router
- not run

**D3** retrieving on the original metadata beats retrieving on Skill++ metadata
- not run

**D4** Skill++ metadata loses required skills at retrieval (v2 finding)
- S5, all required skills among the 30: original metadata 114/120, Skill++ metadata 108/120; lost 6, gained 0, exact McNemar p = 0.0312.
- **D4 holds** (rule: more lost than gained, p < 0.05).

**D5** retrieving on the original metadata costs incoming-skill probes
- Incoming-skill probes hit@5 with Skill++ shown: retrieved on original metadata 76/88, on Skill++ metadata 84/88; lost 11, gained 3, exact McNemar p = 0.0574.
- **D5 not supported** (rule: more lost than gained, p < 0.05).

