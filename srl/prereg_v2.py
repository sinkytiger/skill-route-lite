"""v2 pre-registered decisions (docs/hypotheses_v2.md), on the fresh split test2.

Primary router qwen3:4b; llama3.2:3b is reported with the same statistics, no verdicts. FC@5 at checkpoint c is
scored over all test2 queries released at S0..Sc. Comparisons of full-list conditions at S5 use each query's FC@5
averaged over display-order seeds 0, 1 and 2; retrieval conditions shuffle the candidates per query (seed 0).
Bootstrap: 10,000 resamples of the 120 test2 queries, seed 0; McNemar: exact, two-sided, on seed-0 outcomes.
"""

from __future__ import annotations

import statistics

import numpy as np

from .prereg import ci, pct, pp
from .report_v2 import RET, seed_mean
from .stats import boot_paired, boot_stat, discordant, mcnemar_exact

PRIMARY = "qwen3:4b"
R1_DROP = 0.15       # replication of v1 H1
V1_MAX_GAIN = 0.05   # shortening gives no gain of 5 pp or more (upper CI bound below +5 pp)
V2_GAIN = 0.10       # retrieval raises Vanilla by at least 10 pp
V4_SHARE = 0.5       # with retrieval, the S1->S5 fall is at most half the full-list fall


def _pair(a: dict, b: dict):
    k = sorted(a)
    return boot_paired([a[x] for x in k], [b[x] for x in k])


def _mcn(R, router, a, b):
    fa, fb = R.fc(router, a, 5), R.fc(router, b, 5)
    k = sorted(fa)
    b_, c_ = discordant([fa[x] for x in k], [fb[x] for x in k])
    return f"McNemar (seed 0) {b_}/{c_}, p = {mcnemar_exact(b_, c_):.4f}"


def _fall_stat(R, router, cond):
    qs = R.D.qs(R.split)
    f1, f5 = R.fc(router, cond, 1), R.fc(router, cond, 5)
    early = np.array([q["session"] <= 1 for q in qs])
    a1 = np.array([f1.get(q["qid"], 0) for q in qs], float)
    a5 = np.array([f5[q["qid"]] for q in qs], float)
    return lambda idx: (a1[idx][early[idx]].mean() if early[idx].any() else np.nan) - a5[idx].mean()


def r1(R, router):
    stat = _fall_stat(R, router, "vanilla")
    d = boot_stat(len(R.D.qs(R.split)), stat)
    holds = d[0] >= R1_DROP and d[1] > 0
    return d, [f"- Vanilla (full list) FC@5: S1 {pct(statistics.mean(R.fc(router, 'vanilla', 1).values()))}% -> "
               f"S5 {pct(statistics.mean(R.fc(router, 'vanilla', 5).values()))}%; fall {ci(d)}.",
               f"- **R1 {'holds' if holds else 'not supported'}** (rule: fall >= 15 pp and interval above 0)."]


def v1(R, router):
    a, b = seed_mean(R, router, "spp_noexcl_haiku_short"), seed_mean(R, router, "spp_noexcl_haiku")
    if a is None or b is None:
        return ["- not run"]
    d = _pair(a, b)
    holds = d[2] < V1_MAX_GAIN
    return [f"- Skill++ without the clause, short (mean {pct(statistics.mean(a.values()))}%) minus long (mean "
            f"{pct(statistics.mean(b.values()))}%), S5, averaged over 3 display orders: {ci(d)}; "
            f"{_mcn(R, router, 'spp_noexcl_haiku_short', 'spp_noexcl_haiku')}.",
            f"- **V1 {'holds' if holds else 'not supported'}** (rule: upper bound of the interval below +5 pp)."]


def v2(R, router):
    a, b = R.fc(router, "vanilla" + RET, 5), seed_mean(R, router, "vanilla")
    if b is None:
        return ["- not run"]
    d = _pair(a, b)
    holds = d[0] >= V2_GAIN and d[1] > 0
    return [f"- Vanilla with retrieval ({pct(statistics.mean(a.values()))}%) minus Vanilla on the full list "
            f"(mean of 3 orders, {pct(statistics.mean(b.values()))}%), S5: {ci(d)}; "
            f"{_mcn(R, router, 'vanilla' + RET, 'vanilla')}.",
            f"- **V2 {'holds' if holds else 'not supported'}** (rule: gain >= 10 pp and interval above 0)."]


def v3(R, router):
    a, b = R.fc(router, "spp_haiku" + RET, 5), R.fc(router, "vanilla" + RET, 5)
    d = _pair(a, b)
    holds = d[1] > 0
    return [f"- With retrieval, Skill++ (Haiku) {pct(statistics.mean(a.values()))}% minus Vanilla "
            f"{pct(statistics.mean(b.values()))}% at S5: {ci(d)}; {_mcn(R, router, 'spp_haiku' + RET, 'vanilla' + RET)}.",
            f"- **V3 {'holds' if holds else 'not supported'}** (rule: interval above 0)."]


def v4(R, router, r1_holds: bool):
    full, ret = _fall_stat(R, router, "vanilla"), _fall_stat(R, router, "vanilla" + RET)
    n = len(R.D.qs(R.split))
    df, dr = boot_stat(n, full), boot_stat(n, ret)
    diff = boot_stat(n, lambda idx: full(idx) - ret(idx))
    lines = [f"- S1->S5 fall of Vanilla: full list {ci(df)}; with retrieval {ci(dr)}; difference {ci(diff)}."]
    if not r1_holds:
        return lines + ["- **V4 not judged** (R1 did not hold)."]
    holds = dr[0] <= V4_SHARE * df[0] and diff[1] > 0
    return lines + [f"- **V4 {'holds' if holds else 'not supported'}** (rule: fall with retrieval <= half the "
                    f"full-list fall, and the difference's interval above 0)."]


def decisions_v2(R) -> list[str]:
    out = ["## v2 pre-registered decisions (docs/hypotheses_v2.md)", ""]
    for router in (PRIMARY, "llama3.2:3b"):
        if not R.complete(router, "vanilla") or not R.complete(router, "vanilla" + RET):
            continue
        tag = "primary" if router == PRIMARY else "secondary, no verdict counted"
        out += [f"### {router} ({tag})", "", "**R1** v1's interference replicates on fresh queries"]
        d, lines = r1(R, router)
        out += lines
        out += ["", "**V1** shorter Skill++ descriptions give no gain"] + v1(R, router)
        out += ["", "**V2** narrowing to 30 retrieved candidates raises Vanilla"] + v2(R, router)
        if R.complete(router, "spp_haiku" + RET):
            out += ["", "**V3** with retrieval, Skill++ beats Vanilla"] + v3(R, router)
        out += ["", "**V4** retrieval shrinks the S1->S5 fall"] + v4(R, router, d[0] >= R1_DROP and d[1] > 0)
        out.append("")
    return out
