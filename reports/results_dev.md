# Results: dev split

### Router qwen3:4b: FC@5 (%) by checkpoint

| Condition | S1 (n=12) | S2 (n=18) | S3 (n=24) | S4 (n=30) | S5 (n=36) | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 100.0 | 77.8 | 58.3 | 56.7 | 61.1 | 70.8 | 73.1 | 56.7 / 83.3 | 2/149 |
| bodydist_haiku | 91.7 | 61.1 | 50.0 | 60.0 | 55.6 | 63.7 | 71.8 | 50.0 / 83.3 | 7/149 |
| spp_haiku | 91.7 | 55.6 | 62.5 | 63.3 | 47.2 | 64.1 | 63.0 | 46.7 / 50.0 | 14/149 |
| spp_noexcl_haiku | 100.0 | 66.7 | 54.2 | 56.7 | 61.1 | 67.7 | 76.4 | 63.3 / 50.0 | 9/149 |
| spp_noname_haiku | 83.3 | 61.1 | 62.5 | 63.3 | 47.2 | 63.5 | 63.4 | 46.7 / 50.0 | 13/149 |
| spp_qwen3_4b | 91.7 | 83.3 | 75.0 | 73.3 | 61.1 | 76.9 | 74.1 | 63.3 / 50.0 | 9/149 |

### Router qwen3:4b: interference, incoming-skill probes and S5 error forms

| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | other | top types |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 6 of 20 (of 30) | 13/29 | 8/29 | 2.33 | 20 | 7 | 7 | 6 | other 6, duplicate_crowding 6, description_inconsistency 3 |
| bodydist_haiku | 6 of 17 (of 30) | 23/29 | 22/29 | 2.50 | 24 | 8 | 8 | 8 | other 8, generic_crowding 5, similar 4 |
| spp_haiku | 6 of 18 (of 30) | 22/29 | 19/29 | 2.50 | 31 | 3 | 12 | 16 | other 16, generic_crowding 12, similar 3 |
| spp_noexcl_haiku | 5 of 19 (of 30) | 24/29 | 23/29 | 2.47 | 21 | 1 | 8 | 12 | other 12, generic_crowding 6, duplicate_crowding 2 |
| spp_noname_haiku | 7 of 18 (of 30) | 21/29 | 20/29 | 2.50 | 30 | 9 | 9 | 12 | other 12, duplicate_crowding 7, similar 6 |
| spp_qwen3_4b | 4 of 22 (of 30) | 20/29 | 16/29 | 2.14 | 23 | 5 | 5 | 13 | other 13, similar 4, generic_crowding 3 |

Exclusion pull (haiku, qwen3:4b): 108 (query, excluding skill) pairs over 33 queries; selected with exclusions 6, without 5.

### Router llama3.2:3b: FC@5 (%) by checkpoint

| Condition | S1 (n=12) | S2 (n=18) | S3 (n=24) | S4 (n=30) | S5 (n=36) | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 91.7 | 77.8 | 54.2 | 30.0 | 30.6 | 56.8 | 54.2 | 30.0 / 33.3 | 44/149 |
| bodydist_haiku | 83.3 | 61.1 | 45.8 | 26.7 | 19.4 | 47.3 | 38.0 | 16.7 / 33.3 | 54/149 |
| spp_haiku | 91.7 | 77.8 | 25.0 | 26.7 | 25.0 | 49.2 | 41.7 | 20.0 / 50.0 | 55/149 |
| spp_noexcl_haiku | 83.3 | 72.2 | 37.5 | 30.0 | 27.8 | 50.2 | 44.0 | 26.7 / 33.3 | 55/149 |
| spp_noname_haiku | 100.0 | 72.2 | 33.3 | 20.0 | 16.7 | 48.4 | 39.4 | 13.3 / 33.3 | 52/149 |
| spp_qwen3_4b | 100.0 | 83.3 | 54.2 | 43.3 | 25.0 | 61.2 | 46.8 | 23.3 / 33.3 | 48/149 |

### Router llama3.2:3b: interference, incoming-skill probes and S5 error forms

| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | other | top types |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 14 of 22 (of 30) | 13/29 | 11/29 | 2.56 | 36 | 15 | 15 | 6 | generic_crowding 8, similar_same_name 7, duplicate_crowding 7 |
| bodydist_haiku | 11 of 15 (of 30) | 17/29 | 10/29 | 2.81 | 48 | 16 | 19 | 13 | other 13, duplicate_crowding 10, generic_crowding 9 |
| spp_haiku | 12 of 17 (of 30) | 14/29 | 13/29 | 2.61 | 42 | 7 | 20 | 15 | other 15, generic_crowding 11, duplicate_crowding 9 |
| spp_noexcl_haiku | 8 of 15 (of 30) | 18/29 | 14/29 | 2.50 | 42 | 5 | 23 | 14 | generic_crowding 17, other 14, duplicate_crowding 6 |
| spp_noname_haiku | 16 of 19 (of 30) | 18/29 | 16/29 | 2.72 | 44 | 13 | 18 | 13 | other 13, duplicate_crowding 11, generic_crowding 7 |
| spp_qwen3_4b | 16 of 20 (of 30) | 15/29 | 10/29 | 2.75 | 39 | 9 | 22 | 8 | generic_crowding 15, other 8, duplicate_crowding 7 |

Exclusion pull (haiku, llama3.2:3b): 108 (query, excluding skill) pairs over 33 queries; selected with exclusions 4, without 4.

### Router claude-haiku-5-5: FC@5 (%) by checkpoint

| Condition | S1 (n=12) | S2 (n=18) | S3 (n=24) | S4 (n=30) | S5 (n=36) | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 / 100.0 | 1/149 |
| spp_haiku | 100.0 | 100.0 | 100.0 | 100.0 | 97.2 | 99.4 | 98.6 | 96.7 / 100.0 | 0/149 |

### Router claude-haiku-5-5: interference, incoming-skill probes and S5 error forms

| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | other | top types |
|---|---|---|---|---|---|---|---|---|---|
| vanilla | 0 of 30 (of 30) | 26/29 | 16/29 | 2.75 | 0 | 0 | 0 | 0 |  |
| spp_haiku | 1 of 30 (of 30) | 29/29 | 29/29 | 2.06 | 1 | 1 | 0 | 0 | similar_same_name 1 |


