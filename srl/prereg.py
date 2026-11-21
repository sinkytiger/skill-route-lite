"""Pre-registered decisions (docs/hypotheses.md), computed from the saved test-split runs.

Primary router: qwen3:4b. The same statistics are reported for llama3.2:3b and Claude Haiku 5.5 (where run) without
verdicts. FC@5 at checkpoint c is scored over all queries released at S0..Sc. Bootstrap: 10,000 resamples of the
test queries, seed 0; McNemar: exact, two-sided.
"""

from __future__ import annotations

import statistics

import numpy as np

from . import metrics as M
from .stats import boot_paired, boot_stat, discordant, mcnemar_exact, r1

PRIMARY = "qwen3:4b"
H1_DROP = 0.15          # Vanilla FC@5 falls at least 15 pp from S1 to S5
H2_SHARE = 0.5          # Skill++ (Haiku) recovers at least half of that fall at S5
H3_SHARE = 0.5          # qwen3:4b-written Skill++ gains at most half of the Haiku-written gain
JUDGE_MIN = 0.05        # H2 is judged only if the Vanilla fall is >= 5 pp; H3 only if the Haiku gain is >= 5 pp
                        # with a 95% interval above zero


def pct(x):
    return r1(100 * x)


def pp(x):
    return r1(100 * x, sign=True) + " pp"


def ci(t):
    return f"{pp(t[0])} [95% CI {r1(100 * t[1], True)}, {r1(100 * t[2], True)}]"


def s5_pair(R, router, a, b):
    """Paired FC@5 at S5 over all test queries: (diff, lo, hi), McNemar p, discordant counts."""
    fa, fb = R.fc(router, a, 5), R.fc(router, b, 5)
    keys = sorted(fa)
    xa, xb = [fa[k] for k in keys], [fb[k] for k in keys]
    d = boot_paired(xa, xb)
    b_, c_ = discordant(xa, xb)
    return d, mcnemar_exact(b_, c_), (b_, c_)


def fc_mean(R, router, cond, c):
    return statistics.mean(R.fc(router, cond, c).values())


def h1(R, router):
    stat, n = R.drop_stat(router, "vanilla")
    d = boot_stat(n, stat)
    early = [q for q in R.D.qs(R.split) if q["session"] <= 1]
    f1, f5 = R.fc(router, "vanilla", 1), R.fc(router, "vanilla", 5)
    b_, c_ = discordant([f1[q["qid"]] for q in early], [f5[q["qid"]] for q in early])
    ok, lost, nq = R.interference(router, "vanilla")
    holds = d[0] >= H1_DROP and d[1] > 0
    return d, holds, [
        f"- Vanilla FC@5: S1 {pct(fc_mean(R, router, 'vanilla', 1))}% -> S5 {pct(fc_mean(R, router, 'vanilla', 5))}%; "
        f"fall {ci(d)}.",
        f"- Same {len(early)} queries (released S0-S1) at S1 vs S5: correct only at S1 {b_}, only at S5 {c_}, "
        f"McNemar p = {mcnemar_exact(b_, c_):.4f}.",
        f"- Queries released S0-S4 correct at their first checkpoint: {ok} of {nq}; wrong at S5: {lost}.",
        f"- **H1 {'holds' if holds else 'not supported'}** (rule: fall >= 15 pp and interval above 0)."]


def h2(R, router, d1):
    fall = d1[0]
    (d, p, bc) = s5_pair(R, router, "spp_haiku", "vanilla")
    share = d[0] / fall if fall > 0 else float("nan")
    lines = [f"- Skill++ (Haiku) minus Vanilla at S5: {ci(d)}; McNemar {bc[0]}/{bc[1]}, p = {p:.4f}.",
             f"- Share of the Vanilla S1->S5 fall ({pp(fall)}) recovered at S5: {share:.2f}."]
    if fall < JUDGE_MIN:
        return lines + ["- **H2 not judged** (Vanilla fell less than 5 pp)."]
    holds = share >= H2_SHARE and d[1] > 0
    return lines + [f"- **H2 {'holds' if holds else 'not supported'}** (rule: share >= 0.5 and interval above 0)."]


def h3(R, router):
    (gh, _, _) = s5_pair(R, router, "spp_haiku", "vanilla")
    (gq, pq, bcq) = s5_pair(R, router, "spp_qwen3_4b", "vanilla")
    (dd, pd, bcd) = s5_pair(R, router, "spp_haiku", "spp_qwen3_4b")
    lines = [f"- Gain over Vanilla at S5: Haiku-written {ci(gh)}; qwen3:4b-written {ci(gq)} (McNemar p = {pq:.4f}).",
             f"- Haiku-written minus qwen3:4b-written: {ci(dd)}; McNemar {bcd[0]}/{bcd[1]}, p = {pd:.4f}."]
    if not (gh[0] >= JUDGE_MIN and gh[1] > 0):
        return lines + ["- **H3 not judged** (the Haiku-written gain is below 5 pp or its interval includes 0)."]
    holds = gq[0] <= H3_SHARE * gh[0]
    return lines + [f"- Ratio qwen/Haiku gain: {gq[0] / gh[0]:.2f}.",
                    f"- **H3 {'holds' if holds else 'not supported'}** (rule: qwen-written gain <= half the "
                    f"Haiku-written gain)."]


def h4(R, router, gen="haiku"):
    from .report import h4_pairs
    pairs, per_q = h4_pairs(R, router, gen)
    qids = sorted(per_q)
    a = np.array([sum(x for x, _ in per_q[q]) for q in qids], float)
    b = np.array([sum(y for _, y in per_q[q]) for q in qids], float)
    n = np.array([len(per_q[q]) for q in qids], float)

    def stat(idx):
        return a[idx].sum() / n[idx].sum() - b[idx].sum() / n[idx].sum()
    d = boot_stat(len(qids), stat)
    flat_a = [x for q in qids for x, _ in per_q[q]]
    flat_b = [y for q in qids for _, y in per_q[q]]
    b_, c_ = discordant(flat_a, flat_b)
    lines = [f"- {len(pairs)} (query, incoming skill) pairs over {len(qids)} queries, where the skill's exclusion "
             f"clause names work the query needs. Selected with the clause {int(a.sum())} "
             f"({pct(a.sum() / n.sum())}%), without it {int(b.sum())} ({pct(b.sum() / n.sum())}%).",
             f"- Difference {ci(d)} (bootstrap over queries); pair-level McNemar {b_}/{c_}, "
             f"p = {mcnemar_exact(b_, c_):.4f}."]
    if d[1] > 0:
        verdict = "holds"
    elif d[2] < 0:
        verdict = "not supported; the clause pushed the router away (the paper's intended effect)"
    else:
        verdict = "not supported (no difference shown)"
    return lines + [f"- **H4 {verdict}** (rule: with-clause minus without-clause pick rate, interval above 0)."]


def h5(R, router):
    (d, p, bc) = s5_pair(R, router, "spp_haiku", "vanilla")
    holds = d[2] < 0
    return [f"- Skill++ (Haiku) minus Vanilla at S5: {ci(d)}; McNemar {bc[0]}/{bc[1]}, p = {p:.4f}.",
            f"- **H5 {'holds' if holds else 'not supported'}** (rule: interval below 0)."]


def slots(R, router, cond, c=5):
    return M.incoming_slots(R.D, R.items(router, cond, c), R.D.qs(R.split, c))


def h6(R, router):
    (d, p, bc) = s5_pair(R, router, "spp_noexcl_haiku", "spp_haiku")
    holds = d[1] > 0
    return [f"- Skill++ without the exclusion clause minus full Skill++ (both Haiku-written) at S5: {ci(d)}; "
            f"McNemar {bc[0]}/{bc[1]}, p = {p:.4f}.",
            f"- **H6 {'holds' if holds else 'not supported'}** (rule: interval above 0)."]


def h7(R, router):
    pv, ps = R.probes(router, "vanilla"), R.probes(router, "spp_haiku")
    b_, c_ = discordant(ps[0], pv[0])
    p = mcnemar_exact(b_, c_)
    holds = sum(ps[0]) > sum(pv[0]) and p < 0.05
    return [f"- Incoming-skill probes hit@5: Vanilla {sum(pv[0])}/{len(pv[0])}, Skill++ (Haiku) "
            f"{sum(ps[0])}/{len(ps[0])}; only under Skill++ {b_}, only under Vanilla {c_}, McNemar p = {p:.4f}. "
            f"hit@1: {sum(pv[1])} vs {sum(ps[1])}.",
            f"- **H7 {'holds' if holds else 'not supported'}** (rule: higher under Skill++ and McNemar p < 0.05)."]


def secondary(R, router) -> list[str]:
    out = []
    if R.complete(router, "bodydist_haiku") and R.complete(router, "spp_haiku"):
        (d, p, bc) = s5_pair(R, router, "spp_haiku", "bodydist_haiku")
        a, b = slots(R, router, "spp_haiku"), slots(R, router, "bodydist_haiku")
        k = sorted(a)
        ds = boot_paired([a[x] for x in k], [b[x] for x in k])
        out.append(f"- Skill++ minus Body-distilled (both Haiku-written) at S5: FC@5 {ci(d)} (McNemar p = {p:.4f}); "
                   f"incoming skills selected {ds[0]:+.2f} per query [95% CI {ds[1]:+.2f}, {ds[2]:+.2f}].")
    a, b = slots(R, router, "spp_haiku"), slots(R, router, "vanilla")
    k = sorted(a)
    ds = boot_paired([a[x] for x in k], [b[x] for x in k])
    out.append(f"- Incoming skills among the 5 selected at S5: Vanilla {statistics.mean(b.values()):.2f}, Skill++ "
               f"(Haiku) {statistics.mean(a.values()):.2f} per query; difference {ds[0]:+.2f} "
               f"[95% CI {ds[1]:+.2f}, {ds[2]:+.2f}].")
    if R.complete(router, "spp_noname_haiku"):
        (d, p, bc) = s5_pair(R, router, "spp_noname_haiku", "spp_haiku")
        out.append(f"- Skill++ with original names minus full Skill++ at S5: {ci(d)} (McNemar p = {p:.4f}).")
    return out


def decisions(R) -> list[str]:
    need = ["vanilla", "spp_haiku", "spp_noexcl_haiku", "spp_qwen3_4b"]
    out = ["## Pre-registered decisions (docs/hypotheses.md)", ""]
    for router in [PRIMARY, "llama3.2:3b", "claude-haiku-5-5"]:
        have = [c for c in need if R.complete(router, c)]
        if "vanilla" not in have:
            continue
        tag = "primary" if router == PRIMARY else "secondary, no verdict counted"
        out += [f"### {router} ({tag})", "", "**H1** interference under Vanilla"]
        d1, _, lines = h1(R, router)
        out += lines
        if "spp_haiku" in have:
            out += ["", "**H2** Skill++ (Haiku-written) recovers the fall"] + h2(R, router, d1)
        if "spp_qwen3_4b" in have and "spp_haiku" in have:
            out += ["", "**H3** a qwen3:4b writer gains at most half as much"] + h3(R, router)
        if "spp_noexcl_haiku" in have and "spp_haiku" in have:
            out += ["", "**H4** exclusion clauses pull the router toward the excluding skill"] + h4(R, router)
        if "spp_haiku" in have:
            out += ["", "**H5** (from dev) Skill++ (Haiku-written) lowers FC@5 at S5"] + h5(R, router)
            if "spp_noexcl_haiku" in have:
                out += ["", "**H6** (from dev) dropping the exclusion clause raises FC@5 at S5"] + h6(R, router)
            if R.probes(router, "vanilla") and R.probes(router, "spp_haiku"):
                out += ["", "**H7** (from dev) Skill++ makes incoming skills easier to select for their own "
                        "requests"] + h7(R, router)
            sec = secondary(R, router)
            if sec:
                out += ["", "Secondary comparisons (no verdict)"] + sec
        out.append("")
    return out
