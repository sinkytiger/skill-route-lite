# Paper notes: Skill++ (arXiv:2611.00544) and where this study differs

Read on 2026-11-20 from the arXiv HTML (https://arxiv.org/html/2611.00544): main text, Appendix A (implementation),
B (setup, baselines) and C (results per research question, error types, robustness). Figures were not viewed; their
numbers were taken from the tables and text.

## What the paper does

- **Problem.** Lifelong skill routing: skills arrive in batches, a frozen LLM router picks skills from names and
  descriptions only, and only the metadata of each incoming skill may change. New, similar skills displace earlier
  ones ("routing interference"): **substitution** (a similar incoming skill is picked instead of the required one)
  and **crowding** (incoming skills fill the few slots).
- **Skill++.** For each incoming skill, using only earlier skills' original records (no queries, labels or routing
  results): (1) *description differentiation* against the most similar earlier skill (MiniLM on name + description),
  at most 220 characters, only capabilities in the body, never naming the reference; (2) *scope exclusions*: three
  earlier skills ranked by a fused rank of three similarities built on synthetic queries (Qwen3-Embedding-4B and
  MiniLM), one short phrase each, appended after "Does not cover", trimmed from the end to 298 characters; (3) *name
  clarification* when the new name contains the head (first segment, > 3 characters) of an earlier name; the
  proposal is kept if it has 4-60 characters. Generator: Gemini 3.5 Flash-Lite (fallback Gemini 3.6 Flash);
  synthetic queries by DeepSeek-V4-Flash.
- **Setup.** SRA-Bench BigCodeBench queries (198, each needing 3-5 skills), ten sessions S0-S9, library 27 -> 731.
  Incoming skills are similar to a required skill (MiniLM cosine 0.35-0.95), confusable (a model ranks them top-2
  of 4 for a required skill's query) and not substitutes (GPT-5.5 never judges they can replace it). Required skills
  keep their original metadata; only incoming skills are refined.
- **Router.** Claude Haiku 4.5, two calls (shortlist 10, rerank), K = 5, reads the first 300 characters of each
  description; four other routers (GPT-5.4-mini, GPT-5.6 Luna/Sol, Qwen3.7-Flash) and Codex CLI.
- **Metrics.** FC@5 (all required skills in the top 5, primary), Recall@5; paired bootstrap over queries, 10,000
  resamples. Errors at S9 typed by model judges into seven types and two forms.
- **Headline numbers (Haiku 4.5 router, Table A1).** FC@5 Vanilla 92.5% (S1) -> 36.4% (S9); Skill++ 97.5% ->
  76.3%; Body-distilled 44.4% at S9. Without differentiation / exclusions / name clarification at S9: 56.6 / 64.6 /
  61.6%. Substitution falls from 46.0% to 6.5% of Vanilla errors and crowding from 41.5% to 20.0%. Incoming skills
  rank first on their own synthetic queries 56.9% (Skill++) vs 51.9% (Vanilla). Across five routers the S9 gain
  averages 23.1 pp; it is largest where Vanilla is weakest.

## Differences in this study

| | Paper | Here |
|---|---|---|
| Domain, skills | Web-collected coding skills (SRA-Bench), 731 at S9 | Hand-written synthetic finance-analysis skills (Korean market context, English text), 157 at S5 |
| Sessions | S0-S9, checkpoints S1-S9 | S0-S5, checkpoints S1-S5 |
| Incoming skills | Selected by three checks (similar, confusable, not a substitute) | Written to be similar but not substitutes; kinds labelled by the generator (similar, same name, name-only, overclaiming, broad, generic) |
| Queries | 198 real BigCodeBench tasks, 3-5 skills each | 120 test + 36 dev queries joined from 1-3 hand-written phrasings, 1-3 skills each |
| Router | Claude Haiku 4.5 (and four API models), two calls | qwen3:4b (thinking off) and llama3.2:3b, one call returning 5 IDs under a JSON schema, temperature 0 |
| Display order | Fixed per query and checkpoint | Fixed per checkpoint (shared by all queries, so the prompt prefix can be cached); two extra order seeds as a check |
| Generator | Gemini 3.5 Flash-Lite; DeepSeek-V4-Flash for synthetic queries | Claude Haiku 5.5 (if approved) and qwen3:4b for every call |
| Similarity | MiniLM, Qwen3-Embedding-4B | Character 3-5-gram TF-IDF fitted once on the skill corpus (all skills' original metadata, bodies and synthetic queries). A dev-time check: the most similar earlier skill by name + description (Eq. 7) is the skill an incoming skill was written to resemble for 53 of 107 non-generic incoming skills with TF-IDF and 49-55 with nomic-embed-text (local, four task prefixes); TF-IDF was kept |
| Regeneration | Retries, then a stronger model | Up to 3 tries with the same model, then the original text |
| Error typing | Model judges, verified substitutes excluded | Code, from the generator's labels (no substitutes exist by construction) |
| Plasticity of incoming skills | 1,864 synthetic queries of 673 skills, rank-1 rate | One hand-written probe per incoming skill (88 test, 29 dev), hit@5 and hit@1 |
| Baselines | Body-distilled, Neighbor-contrastive, R&R(-CFT), Hybrid, CC-Pages | Body-distilled only; two ablations (no exclusions, no name clarification) and a qwen3:4b-written Skill++ |
