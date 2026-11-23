"""v3 pre-registered decisions (docs/hypotheses_v3.md), on the fresh split test3.

Primary router qwen3:4b; llama3.2:3b is reported with the same statistics, no verdicts. Comparisons at S5 use each
query's FC@5 averaged over seeds 0, 1 and 2 (display order for the full list, candidate shuffle for top 30).
Retrieval and probe comparisons (D4, D5) use seed 0: the candidate set does not depend on the seed, and probes run
at seed 0 only. Bootstrap: 10,000 resamples of the 120 test3 queries, seed 0; McNemar: exact, two-sided.
"""

from __future__ import annotations

import statistics

from .prereg import ci, pct
from .prereg_v2 import _fall_stat
from .report_v2 import RET, seed_mean
from .report_v3 import DEC
from .stats import boot_paired, boot_stat, mcnemar_exact

PRIMARY = "qwen3:4b"
R1_DROP = 0.15      # v1/v2 interference replicates
N1_GAIN = 0.10      # narrowing raises Vanilla by at least 10 pp (v2's V2 again)
ALPHA = 0.05

VAN = "vanilla" + RET
SPP = "spp_haiku" + RET
DEC_SPP = "spp_haiku" + RET + DEC
DEC_SHORT = "spp_noexcl_haiku_short" + RET + DEC


def _pair(a: dict, b: dict):
    k = sorted(a)
    return boot_paired([a[x] for x in k], [b[x] for x in k])


def all_retrieved(R, router, cond, c=5) -> dict[str, int]:
    it = R.items(router, cond, c)
    return {q["qid"]: int(all(R.D.id_of[k] in it[q["qid"]]["candidates"] for k in q["required"]))
            for q in R.D.qs(R.split, c)}


def r1(R, router):
    d = boot_stat(len(R.D.qs(R.split)), _fall_stat(R, router, "vanilla"))
    holds = d[0] >= R1_DROP and d[1] > 0
    return [f"- Vanilla (full list) FC@5: S1 {pct(statistics.mean(R.fc(router, 'vanilla', 1).values()))}% -> "
            f"S5 {pct(statistics.mean(R.fc(router, 'vanilla', 5).values()))}%; fall {ci(d)}.",
            f"- **R1 {'holds' if holds else 'not supported'}** (rule: fall >= 15 pp and interval above 0)."]


def n1(R, router):
    a, b = seed_mean(R, router, VAN), seed_mean(R, router, "vanilla")
    if a is None or b is None:
        return ["- not run"]
    d = _pair(a, b)
    holds = d[0] >= N1_GAIN and d[1] > 0
    return [f"- Vanilla top 30 (mean of 3 shuffles, {pct(statistics.mean(a.values()))}%) minus Vanilla full list (mean "
            f"of 3 orders, {pct(statistics.mean(b.values()))}%), S5: {ci(d)}.",
            f"- **N1 {'holds' if holds else 'not supported'}** (rule: gain >= 10 pp and interval above 0)."]


def _shown(R, router, cond, label, tag):
    a, b = seed_mean(R, router, cond), seed_mean(R, router, VAN)
    if a is None or b is None:
        return ["- not run"]
    d = _pair(a, b)
    holds = d[1] > 0
    return [f"- Same 30 candidates: {label} shown ({pct(statistics.mean(a.values()))}%) minus original metadata shown "
            f"({pct(statistics.mean(b.values()))}%), S5, mean of 3 shuffles: {ci(d)}.",
            f"- **{tag} {'holds' if holds else 'not supported'}** (rule: interval above 0)."]


def d1(R, router):
    return _shown(R, router, DEC_SPP, "Skill++ (Haiku) metadata", "D1")


def d2(R, router):
    return _shown(R, router, DEC_SHORT, "short Skill++ without the clause", "D2")


def d3(R, router):
    a, b = seed_mean(R, router, DEC_SPP), seed_mean(R, router, SPP)
    if a is None or b is None:
        return ["- not run"]
    d = _pair(a, b)
    holds = d[1] > 0
    return [f"- Skill++ shown, retrieved on original metadata ({pct(statistics.mean(a.values()))}%) minus retrieved on "
            f"Skill++ metadata ({pct(statistics.mean(b.values()))}%), S5, mean of 3 shuffles: {ci(d)}.",
            f"- **D3 {'holds' if holds else 'not supported'}** (rule: interval above 0)."]


def d4(R, router):
    v, s = all_retrieved(R, router, VAN), all_retrieved(R, router, SPP)
    lost = sum(1 for q in v if v[q] and not s[q])
    gained = sum(1 for q in v if s[q] and not v[q])
    p = mcnemar_exact(lost, gained)
    holds = lost > gained and p < ALPHA
    return [f"- S5, all required skills among the 30: original metadata {sum(v.values())}/{len(v)}, Skill++ metadata "
            f"{sum(s.values())}/{len(s)}; lost {lost}, gained {gained}, exact McNemar p = {p:.4f}.",
            f"- **D4 {'holds' if holds else 'not supported'}** (rule: more lost than gained, p < 0.05)."]


def d5(R, router):
    pa, pb = R.probes(router, DEC_SPP), R.probes(router, SPP)
    if pa is None or pb is None:
        return ["- not run"]
    lost = sum(1 for x, y in zip(pa[0], pb[0]) if y and not x)
    gained = sum(1 for x, y in zip(pa[0], pb[0]) if x and not y)
    p = mcnemar_exact(lost, gained)
    holds = lost > gained and p < ALPHA
    return [f"- Incoming-skill probes hit@5 with Skill++ shown: retrieved on original metadata {sum(pa[0])}/{len(pa[0])}, "
            f"on Skill++ metadata {sum(pb[0])}/{len(pb[0])}; lost {lost}, gained {gained}, exact McNemar p = {p:.4f}.",
            f"- **D5 {'holds' if holds else 'not supported'}** (rule: more lost than gained, p < 0.05)."]


def decisions_v3(R) -> list[str]:
    out = ["## v3 pre-registered decisions (docs/hypotheses_v3.md)", ""]
    for router in (PRIMARY, "llama3.2:3b"):
        if not R.complete(router, VAN) or not R.complete(router, DEC_SPP):
            continue
        tag = "primary" if router == PRIMARY else "secondary, no verdict counted"
        out += [f"### {router} ({tag})", ""]
        if R.complete(router, "vanilla"):
            out += ["**R1** the interference replicates on fresh queries"] + r1(R, router)
            out += ["", "**N1** narrowing to 30 candidates raises Vanilla"] + n1(R, router)
            out.append("")
        out += ["**D1** with the same candidates, Skill++ metadata helps the router"] + d1(R, router)
        if R.complete(router, DEC_SHORT):
            out += ["", "**D2** with the same candidates, short Skill++ without the clause helps the router"] + d2(R, router)
        if R.complete(router, SPP):
            out += ["", "**D3** retrieving on the original metadata beats retrieving on Skill++ metadata"] + d3(R, router)
            out += ["", "**D4** Skill++ metadata loses required skills at retrieval (v2 finding)"] + d4(R, router)
            out += ["", "**D5** retrieving on the original metadata costs incoming-skill probes"] + d5(R, router)
        out.append("")
    return out
