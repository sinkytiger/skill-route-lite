# Results: test split

### Router qwen3:4b: FC@5 (%) by checkpoint

| Condition | S1 (n=40) | S2 (n=60) | S3 (n=80) | S4 (n=100) | S5 (n=120) | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 85.0 | 56.7 | 53.8 | 61.0 | 59.2 | 63.1 | 72.5 | 57.0 / 70.0 | 18/488 |
| bodydist_haiku | 72.5 | 48.3 | 48.8 | 55.0 | 58.3 | 56.6 | 71.5 | 57.0 / 65.0 | 27/488 |
| spp_haiku | 77.5 | 45.0 | 48.8 | 52.0 | 54.2 | 55.5 | 68.8 | 53.0 / 60.0 | 30/488 |
| spp_noexcl_haiku | 77.5 | 46.7 | 56.3 | 56.0 | 57.5 | 58.8 | 72.2 | 55.0 / 70.0 | 25/488 |
| spp_noname_haiku | 80.0 | 43.3 | 46.3 | 52.0 | 53.3 | 55.0 | 68.5 | 51.0 / 65.0 | 29/488 |
| spp_qwen3_4b | 82.5 | 58.3 | 63.8 | 62.0 | 65.0 | 66.3 | 76.5 | 64.0 / 70.0 | 26/488 |

### Router qwen3:4b: interference, incoming-skill probes and S5 error forms

| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | other | top types |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 27 of 69 (of 100) | 41/88 | 24/88 | 2.71 | 73 | 16 | 38 | 19 | generic_crowding 25, other 19, duplicate_crowding 13 |
| bodydist_haiku | 17 of 59 (of 100) | 78/88 | 68/88 | 2.53 | 77 | 25 | 19 | 33 | other 33, similar 13, duplicate_crowding 12 |
| spp_haiku | 18 of 57 (of 100) | 79/88 | 69/88 | 2.67 | 80 | 16 | 23 | 41 | other 41, generic_crowding 12, similar 11 |
| spp_noexcl_haiku | 18 of 62 (of 100) | 77/88 | 65/88 | 2.67 | 77 | 18 | 29 | 30 | other 30, generic_crowding 17, similar 13 |
| spp_noname_haiku | 20 of 58 (of 100) | 80/88 | 67/88 | 2.73 | 81 | 16 | 32 | 33 | other 33, generic_crowding 19, duplicate_crowding 13 |
| spp_qwen3_4b | 16 of 69 (of 100) | 68/88 | 58/88 | 2.28 | 63 | 13 | 19 | 31 | other 31, similar 10, duplicate_crowding 10 |

Exclusion pull (haiku, qwen3:4b): 308 (query, excluding skill) pairs over 90 queries; selected with exclusions 14, without 14.

### Router llama3.2:3b: FC@5 (%) by checkpoint

| Condition | S1 (n=40) | S2 (n=60) | S3 (n=80) | S4 (n=100) | S5 (n=120) | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 72.5 | 53.3 | 37.5 | 37.0 | 35.0 | 47.1 | 50.0 | 40.0 / 10.0 | 127/488 |
| bodydist_haiku | 77.5 | 50.0 | 31.3 | 30.0 | 20.8 | 41.9 | 36.0 | 22.0 / 15.0 | 165/488 |
| spp_haiku | 57.5 | 50.0 | 27.5 | 26.0 | 25.8 | 37.4 | 40.1 | 28.0 / 15.0 | 192/488 |
| spp_noexcl_haiku | 72.5 | 56.7 | 30.0 | 27.0 | 29.2 | 43.1 | 42.2 | 32.0 / 15.0 | 180/488 |
| spp_noname_haiku | 52.5 | 45.0 | 27.5 | 25.0 | 29.2 | 35.8 | 45.8 | 32.0 / 15.0 | 186/488 |
| spp_qwen3_4b | 72.5 | 58.3 | 38.8 | 31.0 | 29.2 | 46.0 | 44.6 | 31.0 / 20.0 | 169/488 |

### Router llama3.2:3b: interference, incoming-skill probes and S5 error forms

| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | other | top types |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 28 of 61 (of 100) | 28/88 | 21/88 | 2.53 | 126 | 27 | 66 | 33 | generic_crowding 47, other 33, duplicate_crowding 19 |
| bodydist_haiku | 39 of 60 (of 100) | 56/88 | 46/88 | 3.05 | 155 | 36 | 74 | 45 | other 45, duplicate_crowding 39, generic_crowding 35 |
| spp_haiku | 25 of 50 (of 100) | 49/88 | 40/88 | 2.50 | 148 | 22 | 58 | 68 | other 68, generic_crowding 38, duplicate_crowding 20 |
| spp_noexcl_haiku | 31 of 60 (of 100) | 52/88 | 40/88 | 2.79 | 145 | 18 | 89 | 38 | generic_crowding 65, other 38, duplicate_crowding 24 |
| spp_noname_haiku | 21 of 48 (of 100) | 55/88 | 44/88 | 2.40 | 136 | 28 | 58 | 50 | other 50, generic_crowding 37, duplicate_crowding 21 |
| spp_qwen3_4b | 33 of 57 (of 100) | 48/88 | 39/88 | 2.19 | 138 | 15 | 60 | 63 | other 63, generic_crowding 35, duplicate_crowding 25 |

Exclusion pull (haiku, llama3.2:3b): 308 (query, excluding skill) pairs over 90 queries; selected with exclusions 13, without 12.

### Router claude-haiku-5-5: FC@5 (%) by checkpoint

| Condition | S1 (n=40) | S2 (n=60) | S3 (n=80) | S4 (n=100) | S5 (n=120) | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 100.0 | 100.0 | 100.0 | 98.0 | 99.2 | 99.4 | 99.7 | 99.0 / 100.0 | 3/488 |
| spp_haiku | 100.0 | 100.0 | 100.0 | 100.0 | 99.2 | 99.8 | 99.7 | 99.0 / 100.0 | 1/488 |

### Router claude-haiku-5-5: interference, incoming-skill probes and S5 error forms

| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | other | top types |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 1 of 99 (of 100) | 81/88 | 54/88 | 2.66 | 1 | 1 | 0 | 0 | similar 1 |
| spp_haiku | 1 of 100 (of 100) | 88/88 | 88/88 | 1.99 | 1 | 1 | 0 | 0 | description_inconsistency 1 |


### Router qwen3:4b: display-order seeds at S5 (FC@5 %)

| Order seed | vanilla | spp_haiku | spp_haiku - vanilla [95% CI] |
|---|---|---|---|
| 0 | 59.2 | 54.2 | -5.0 [-14.2, +4.2] |
| 1 | 56.7 | 46.7 | -10.0 [-18.3, -2.5] |
| 2 | 45.8 | 47.5 | +1.7 [-7.5, +10.8] |

## Pre-registered decisions (docs/hypotheses.md)

### qwen3:4b (primary)

**H1** interference under Vanilla
- Vanilla FC@5: S1 85.0% -> S5 59.2%; fall +25.8 pp [95% CI +11.7, +38.9].
- Same 40 queries (released S0-S1) at S1 vs S5: correct only at S1 16, only at S5 2, McNemar p = 0.0013.
- Queries released S0-S4 correct at their first checkpoint: 69 of 100; wrong at S5: 27.
- **H1 holds** (rule: fall >= 15 pp and interval above 0).

**H2** Skill++ (Haiku-written) recovers the fall
- Skill++ (Haiku) minus Vanilla at S5: -5.0 pp [95% CI -14.2, +4.2]; McNemar 12/18, p = 0.3616.
- Share of the Vanilla S1->S5 fall (+25.8 pp) recovered at S5: -0.19.
- **H2 not supported** (rule: share >= 0.5 and interval above 0).

**H3** a qwen3:4b writer gains at most half as much
- Gain over Vanilla at S5: Haiku-written -5.0 pp [95% CI -14.2, +4.2]; qwen3:4b-written +5.8 pp [95% CI -2.5, +14.2] (McNemar p = 0.2295).
- Haiku-written minus qwen3:4b-written: -10.8 pp [95% CI -18.3, -3.3]; McNemar 5/18, p = 0.0106.
- **H3 not judged** (the Haiku-written gain is below 5 pp or its interval includes 0).

**H4** exclusion clauses pull the router toward the excluding skill
- 308 (query, incoming skill) pairs over 90 queries, where the skill's exclusion clause names work the query needs. Selected with the clause 14 (4.5%), without it 14 (4.5%).
- Difference +0.0 pp [95% CI -1.8, +1.8] (bootstrap over queries); pair-level McNemar 4/4, p = 1.0000.
- **H4 not supported (no difference shown)** (rule: with-clause minus without-clause pick rate, interval above 0).

**H5** (from dev) Skill++ (Haiku-written) lowers FC@5 at S5
- Skill++ (Haiku) minus Vanilla at S5: -5.0 pp [95% CI -14.2, +4.2]; McNemar 12/18, p = 0.3616.
- **H5 not supported** (rule: interval below 0).

**H6** (from dev) dropping the exclusion clause raises FC@5 at S5
- Skill++ without the exclusion clause minus full Skill++ (both Haiku-written) at S5: +3.3 pp [95% CI -5.0, +11.7]; McNemar 15/11, p = 0.5572.
- **H6 not supported** (rule: interval above 0).

**H7** (from dev) Skill++ makes incoming skills easier to select for their own requests
- Incoming-skill probes hit@5: Vanilla 41/88, Skill++ (Haiku) 79/88; only under Skill++ 38, only under Vanilla 0, McNemar p = 0.0000. hit@1: 24 vs 69.
- **H7 holds** (rule: higher under Skill++ and McNemar p < 0.05).

Secondary comparisons (no verdict)
- Skill++ minus Body-distilled (both Haiku-written) at S5: FC@5 -4.2 pp [95% CI -12.5, +4.2] (McNemar p = 0.4244); incoming skills selected +0.13 per query [95% CI -0.08, +0.35].
- Incoming skills among the 5 selected at S5: Vanilla 2.71, Skill++ (Haiku) 2.67 per query; difference -0.04 [95% CI -0.26, +0.17].
- Skill++ with original names minus full Skill++ at S5: -0.8 pp [95% CI -8.3, +6.7] (McNemar p = 1.0000).

### llama3.2:3b (secondary, no verdict counted)

**H1** interference under Vanilla
- Vanilla FC@5: S1 72.5% -> S5 35.0%; fall +37.5 pp [95% CI +21.9, +52.1].
- Same 40 queries (released S0-S1) at S1 vs S5: correct only at S1 17, only at S5 1, McNemar p = 0.0001.
- Queries released S0-S4 correct at their first checkpoint: 61 of 100; wrong at S5: 28.
- **H1 holds** (rule: fall >= 15 pp and interval above 0).

**H2** Skill++ (Haiku-written) recovers the fall
- Skill++ (Haiku) minus Vanilla at S5: -9.2 pp [95% CI -16.7, -1.7]; McNemar 6/17, p = 0.0347.
- Share of the Vanilla S1->S5 fall (+37.5 pp) recovered at S5: -0.24.
- **H2 not supported** (rule: share >= 0.5 and interval above 0).

**H3** a qwen3:4b writer gains at most half as much
- Gain over Vanilla at S5: Haiku-written -9.2 pp [95% CI -16.7, -1.7]; qwen3:4b-written -5.8 pp [95% CI -12.5, +0.8] (McNemar p = 0.1435).
- Haiku-written minus qwen3:4b-written: -3.3 pp [95% CI -10.0, +3.3]; McNemar 6/10, p = 0.4545.
- **H3 not judged** (the Haiku-written gain is below 5 pp or its interval includes 0).

**H4** exclusion clauses pull the router toward the excluding skill
- 308 (query, incoming skill) pairs over 90 queries, where the skill's exclusion clause names work the query needs. Selected with the clause 13 (4.2%), without it 12 (3.9%).
- Difference +0.3 pp [95% CI -2.2, +3.0] (bootstrap over queries); pair-level McNemar 9/8, p = 1.0000.
- **H4 not supported (no difference shown)** (rule: with-clause minus without-clause pick rate, interval above 0).

**H5** (from dev) Skill++ (Haiku-written) lowers FC@5 at S5
- Skill++ (Haiku) minus Vanilla at S5: -9.2 pp [95% CI -16.7, -1.7]; McNemar 6/17, p = 0.0347.
- **H5 holds** (rule: interval below 0).

**H6** (from dev) dropping the exclusion clause raises FC@5 at S5
- Skill++ without the exclusion clause minus full Skill++ (both Haiku-written) at S5: +3.3 pp [95% CI -2.5, +10.0]; McNemar 9/5, p = 0.4240.
- **H6 not supported** (rule: interval above 0).

**H7** (from dev) Skill++ makes incoming skills easier to select for their own requests
- Incoming-skill probes hit@5: Vanilla 28/88, Skill++ (Haiku) 49/88; only under Skill++ 30, only under Vanilla 9, McNemar p = 0.0011. hit@1: 21 vs 40.
- **H7 holds** (rule: higher under Skill++ and McNemar p < 0.05).

Secondary comparisons (no verdict)
- Skill++ minus Body-distilled (both Haiku-written) at S5: FC@5 +5.0 pp [95% CI -0.8, +10.8] (McNemar p = 0.1796); incoming skills selected -0.55 per query [95% CI -0.80, -0.30].
- Incoming skills among the 5 selected at S5: Vanilla 2.53, Skill++ (Haiku) 2.50 per query; difference -0.03 [95% CI -0.30, +0.23].
- Skill++ with original names minus full Skill++ at S5: +3.3 pp [95% CI -0.8, +8.3] (McNemar p = 0.2891).

### claude-haiku-5-5 (secondary, no verdict counted)

**H1** interference under Vanilla
- Vanilla FC@5: S1 100.0% -> S5 99.2%; fall +0.8 pp [95% CI +0.0, +2.5].
- Same 40 queries (released S0-S1) at S1 vs S5: correct only at S1 1, only at S5 0, McNemar p = 1.0000.
- Queries released S0-S4 correct at their first checkpoint: 99 of 100; wrong at S5: 1.
- **H1 not supported** (rule: fall >= 15 pp and interval above 0).

**H2** Skill++ (Haiku-written) recovers the fall
- Skill++ (Haiku) minus Vanilla at S5: +0.0 pp [95% CI -2.5, +2.5]; McNemar 1/1, p = 1.0000.
- Share of the Vanilla S1->S5 fall (+0.8 pp) recovered at S5: 0.00.
- **H2 not judged** (Vanilla fell less than 5 pp).

**H5** (from dev) Skill++ (Haiku-written) lowers FC@5 at S5
- Skill++ (Haiku) minus Vanilla at S5: +0.0 pp [95% CI -2.5, +2.5]; McNemar 1/1, p = 1.0000.
- **H5 not supported** (rule: interval below 0).

**H7** (from dev) Skill++ makes incoming skills easier to select for their own requests
- Incoming-skill probes hit@5: Vanilla 81/88, Skill++ (Haiku) 88/88; only under Skill++ 7, only under Vanilla 0, McNemar p = 0.0156. hit@1: 54 vs 88.
- **H7 holds** (rule: higher under Skill++ and McNemar p < 0.05).

Secondary comparisons (no verdict)
- Incoming skills among the 5 selected at S5: Vanilla 2.66, Skill++ (Haiku) 1.99 per query; difference -0.67 [95% CI -0.83, -0.50].

