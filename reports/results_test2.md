# v2 results: test2 split

### Router qwen3:4b: FC@5 (%) by checkpoint

| Condition | S1 (n=40) | S2 (n=60) | S3 (n=80) | S4 (n=100) | S5 (n=120) | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 85.0 | 41.7 | 55.0 | 61.0 | 55.8 | 59.7 | 70.7 | 54.0 / 65.0 | 16/488 |
| spp_haiku | 87.5 | 46.7 | 46.3 | 52.0 | 47.5 | 56.0 | 62.5 | 47.0 / 50.0 | 28/488 |
| spp_noexcl_haiku | 85.0 | 41.7 | 40.0 | 47.0 | 51.7 | 53.1 | 66.3 | 52.0 / 50.0 | 24/488 |
| spp_noexcl_haiku_short | 85.0 | 48.3 | 58.8 | 52.0 | 51.7 | 59.2 | 62.8 | 53.0 / 45.0 | 22/488 |
| spp_haiku_short | 85.0 | 43.3 | 56.3 | 50.0 | 52.5 | 57.4 | 65.1 | 53.0 / 50.0 | 20/488 |
| vanilla+r30tfidf | 82.5 | 78.3 | 75.0 | 70.0 | 69.2 | 75.0 | 83.6 | 67.0 / 80.0 | 5/488 |
| spp_haiku+r30tfidf | 90.0 | 78.3 | 72.5 | 70.0 | 71.7 | 76.5 | 83.3 | 67.0 / 95.0 | 6/488 |
| spp_noexcl_haiku_short+r30tfidf | 82.5 | 73.3 | 73.8 | 72.0 | 75.8 | 75.5 | 87.4 | 74.0 / 85.0 | 7/488 |
| spp_haiku_short+r30tfidf | 77.5 | 83.3 | 77.5 | 72.0 | 71.7 | 76.4 | 85.3 | 71.0 / 75.0 | 3/488 |

### Router qwen3:4b: interference, incoming-skill probes and S5 error forms

| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | other | top types |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 24 of 64 (of 100) | 41/88 | 24/88 | 2.57 | 75 | 13 | 33 | 29 | other 29, generic_crowding 23, duplicate_crowding 10 |
| spp_haiku | 25 of 59 (of 100) | 79/88 | 69/88 | 2.69 | 95 | 16 | 38 | 41 | other 41, duplicate_crowding 24, generic_crowding 14 |
| spp_noexcl_haiku | 19 of 56 (of 100) | 77/88 | 65/88 | 2.67 | 88 | 15 | 34 | 39 | other 39, duplicate_crowding 17, generic_crowding 17 |
| spp_noexcl_haiku_short | 23 of 63 (of 100) | 71/88 | 64/88 | 2.58 | 91 | 13 | 38 | 40 | other 40, generic_crowding 24, duplicate_crowding 14 |
| spp_haiku_short | 20 of 60 (of 100) | 73/88 | 66/88 | 2.73 | 86 | 14 | 32 | 40 | other 40, generic_crowding 22, duplicate_crowding 10 |
| vanilla+r30tfidf | 21 of 80 (of 100) | 58/88 | 43/88 | 1.77 | 46 | 23 | 10 | 13 | other 13, duplicate_crowding 10, similar 8 |
| spp_haiku+r30tfidf | 18 of 78 (of 100) | 85/88 | 79/88 | 2.35 | 44 | 28 | 8 | 8 | similar 17, similar_same_name 9, duplicate_crowding 8 |
| spp_noexcl_haiku_short+r30tfidf | 13 of 76 (of 100) | 80/88 | 76/88 | 1.90 | 34 | 17 | 6 | 11 | similar 15, other 11, duplicate_crowding 6 |
| spp_haiku_short+r30tfidf | 14 of 74 (of 100) | 84/88 | 75/88 | 1.99 | 40 | 21 | 9 | 10 | similar 12, other 10, duplicate_crowding 8 |

### Router qwen3:4b: share of queries whose required skills were all retrieved (top 30, %)

| Condition | S1 | S2 | S3 | S4 | S5 |
|---|---|---|---|---|---|
| vanilla+r30tfidf | 100.0 | 98.3 | 98.8 | 95.0 | 95.8 |
| spp_haiku+r30tfidf | 100.0 | 96.7 | 93.8 | 88.0 | 88.3 |
| spp_noexcl_haiku_short+r30tfidf | 100.0 | 98.3 | 93.8 | 93.0 | 91.7 |
| spp_haiku_short+r30tfidf | 100.0 | 98.3 | 93.8 | 92.0 | 90.8 |

### Router qwen3:4b: FC@5 at S5 by display-order seed (%)

| Condition | seed 0 | seed 1 | seed 2 | mean |
|---|---|---|---|---|
| vanilla | 55.8 | 49.2 | 44.2 | 49.7 |
| spp_noexcl_haiku | 51.7 | 48.3 | 42.5 | 47.5 |
| spp_noexcl_haiku_short | 51.7 | 56.7 | 42.5 | 50.3 |

### Router llama3.2:3b: FC@5 (%) by checkpoint

| Condition | S1 (n=40) | S2 (n=60) | S3 (n=80) | S4 (n=100) | S5 (n=120) | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 67.5 | 55.0 | 38.8 | 34.0 | 31.7 | 45.4 | 51.5 | 34.0 / 20.0 | 151/488 |
| spp_haiku | 62.5 | 58.3 | 27.5 | 22.0 | 22.5 | 38.6 | 37.2 | 22.0 / 25.0 | 215/488 |
| vanilla+r30tfidf | 80.0 | 61.7 | 65.0 | 64.0 | 60.0 | 66.1 | 74.9 | 62.0 / 50.0 | 56/488 |
| spp_haiku+r30tfidf | 77.5 | 60.0 | 66.3 | 67.0 | 59.2 | 66.0 | 75.1 | 56.0 / 75.0 | 80/488 |

### Router llama3.2:3b: interference, incoming-skill probes and S5 error forms

| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | other | top types |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 22 of 53 (of 100) | 28/88 | 21/88 | 2.56 | 125 | 24 | 80 | 21 | generic_crowding 58, duplicate_crowding 22, other 21 |
| spp_haiku | 29 of 46 (of 100) | 49/88 | 40/88 | 2.58 | 160 | 29 | 74 | 57 | other 57, generic_crowding 42, duplicate_crowding 32 |
| vanilla+r30tfidf | 19 of 74 (of 100) | 58/88 | 37/88 | 1.77 | 69 | 35 | 8 | 26 | other 26, similar 14, description_inconsistency 11 |
| spp_haiku+r30tfidf | 21 of 69 (of 100) | 84/88 | 74/88 | 2.41 | 68 | 31 | 24 | 13 | similar 20, duplicate_crowding 16, other 13 |

### Router llama3.2:3b: share of queries whose required skills were all retrieved (top 30, %)

| Condition | S1 | S2 | S3 | S4 | S5 |
|---|---|---|---|---|---|
| vanilla+r30tfidf | 100.0 | 98.3 | 98.8 | 95.0 | 95.8 |
| spp_haiku+r30tfidf | 100.0 | 96.7 | 93.8 | 88.0 | 88.3 |

## v2 pre-registered decisions (docs/hypotheses_v2.md)

### qwen3:4b (primary)

**R1** v1's interference replicates on fresh queries
- Vanilla (full list) FC@5: S1 85.0% -> S5 55.8%; fall +29.2 pp [95% CI +15.5, +41.9].
- **R1 holds** (rule: fall >= 15 pp and interval above 0).

**V1** shorter Skill++ descriptions give no gain
- Skill++ without the clause, short (mean 50.3%) minus long (mean 47.5%), S5, averaged over 3 display orders: +2.8 pp [95% CI -1.9, +7.8]; McNemar (seed 0) 15/15, p = 1.0000.
- **V1 not supported** (rule: upper bound of the interval below +5 pp).

**V2** narrowing to 30 retrieved candidates raises Vanilla
- Vanilla with retrieval (69.2%) minus Vanilla on the full list (mean of 3 orders, 49.7%), S5: +19.4 pp [95% CI +10.8, +27.8]; McNemar (seed 0) 30/14, p = 0.0226.
- **V2 holds** (rule: gain >= 10 pp and interval above 0).

**V3** with retrieval, Skill++ beats Vanilla
- With retrieval, Skill++ (Haiku) 71.7% minus Vanilla 69.2% at S5: +2.5 pp [95% CI -7.5, +12.5]; McNemar (seed 0) 20/17, p = 0.7428.
- **V3 not supported** (rule: interval above 0).

**V4** retrieval shrinks the S1->S5 fall
- S1->S5 fall of Vanilla: full list +29.2 pp [95% CI +15.5, +41.9]; with retrieval +13.3 pp [95% CI -0.5, +26.6]; difference +15.8 pp [95% CI -0.1, +32.1].
- **V4 not supported** (rule: fall with retrieval <= half the full-list fall, and the difference's interval above 0).

### llama3.2:3b (secondary, no verdict counted)

**R1** v1's interference replicates on fresh queries
- Vanilla (full list) FC@5: S1 67.5% -> S5 31.7%; fall +35.8 pp [95% CI +20.4, +50.8].
- **R1 holds** (rule: fall >= 15 pp and interval above 0).

**V1** shorter Skill++ descriptions give no gain
- not run

**V2** narrowing to 30 retrieved candidates raises Vanilla
- not run

**V3** with retrieval, Skill++ beats Vanilla
- With retrieval, Skill++ (Haiku) 59.2% minus Vanilla 60.0% at S5: -0.8 pp [95% CI -10.8, +9.2]; McNemar (seed 0) 19/20, p = 1.0000.
- **V3 not supported** (rule: interval above 0).

**V4** retrieval shrinks the S1->S5 fall
- S1->S5 fall of Vanilla: full list +35.8 pp [95% CI +20.4, +50.8]; with retrieval +20.0 pp [95% CI +6.7, +32.9]; difference +15.8 pp [95% CI -0.6, +31.7].
- **V4 not supported** (rule: fall with retrieval <= half the full-list fall, and the difference's interval above 0).

