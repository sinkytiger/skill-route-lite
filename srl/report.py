"""Tables from the saved routing blocks, and the pre-registered decisions (docs/hypotheses.md) for the test split."""

from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

import numpy as np

from . import metrics as M
from .conditions import load_rewrites
from .stats import boot_paired, boot_stat, discordant, mcnemar_exact

ROOT = Path(__file__).resolve().parent.parent
ROUTERS = ["qwen3:4b", "llama3.2:3b", "claude-haiku-5-5"]
CONDS = ["vanilla", "bodydist_haiku", "spp_haiku", "spp_noexcl_haiku", "spp_noname_haiku",
         "bodydist_qwen3_4b", "spp_qwen3_4b", "spp_noexcl_qwen3_4b", "spp_noname_qwen3_4b"]
CPS = [1, 2, 3, 4, 5]


def pct(x: float) -> str:
    return f"{100 * x:.1f}"


def pp(x: float) -> str:
    return f"{100 * x:+.1f}"


class Runs:
    def __init__(self, split: str, seed: int = 0):
        self.D, self.split, self.seed = M.Data(), split, seed
        self._c: dict = {}

    def items(self, router, cond, c, seed=None):
        k = (router, cond, c, self.seed if seed is None else seed)
        if k not in self._c:
            self._c[k] = M.load_items(router, cond, self.split, c, k[3])
        return self._c[k]

    def complete(self, router, cond, cps=CPS) -> bool:
        for c in cps:
            it = self.items(router, cond, c)
            if it is None or any(q["qid"] not in it for q in self.D.qs(self.split, c)):
                return False
        return True

    def fc(self, router, cond, c, seed=None) -> dict[str, int]:
        it = self.items(router, cond, c, seed)
        return {k: v[0] for k, v in M.per_query(self.D, it, self.D.qs(self.split, c)).items()}

    def rec(self, router, cond, c) -> dict[str, float]:
        it = self.items(router, cond, c)
        return {k: v[1] for k, v in M.per_query(self.D, it, self.D.qs(self.split, c)).items()}

    def probes(self, router, cond) -> tuple[list[int], list[int]] | None:
        it = self.items(router, cond, 5)
        pr = self.D.pr(self.split)
        if it is None or any(p["pid"] not in it for p in pr):
            return None
        h5 = [int(self.D.id_of[p["skill"]] in it[p["pid"]]["selected"]) for p in pr]
        h1 = [int(it[p["pid"]]["selected"][:1] == [self.D.id_of[p["skill"]]]) for p in pr]
        return h5, h1

    def drop_stat(self, router, cond):
        """FC@5 at S1 (queries released S0-S1) minus FC@5 at S5 (all queries): a bootstrap-ready statistic over the
        split's queries."""
        qs = self.D.qs(self.split)
        f1, f5 = self.fc(router, cond, 1), self.fc(router, cond, 5)
        early = np.array([q["session"] <= 1 for q in qs])
        a1 = np.array([f1.get(q["qid"], 0) for q in qs], float)
        a5 = np.array([f5[q["qid"]] for q in qs], float)

        def stat(idx):
            e = early[idx]
            return (a1[idx][e].mean() if e.any() else np.nan) - a5[idx].mean()
        return stat, len(qs)

    def interference(self, router, cond):
        """Queries released S0-S4: correct at their first checkpoint, and how many of those fail at S5."""
        qs = [q for q in self.D.qs(self.split) if q["session"] <= 4]
        f5 = self.fc(router, cond, 5)
        first = {q["qid"]: self.fc(router, cond, M.first_checkpoint(q))[q["qid"]] for q in qs}
        ok_first = [q["qid"] for q in qs if first[q["qid"]] == 1]
        return len(ok_first), sum(f5[k] == 0 for k in ok_first), len(qs)


def main_table(R: Runs, router: str, conds: list[str]) -> list[str]:
    out = [f"### Router {router}: FC@5 (%) by checkpoint", "",
           "| Condition | " + " | ".join(f"S{c} (n={len(R.D.qs(R.split, c))})" for c in CPS) +
           " | Avg | Recall@5 S5 | S5 old / new | <5 distinct IDs |",
           "|---|" + "---|" * (len(CPS) + 4)]
    for cond in conds:
        if not R.complete(router, cond):
            continue
        fcs = [statistics.mean(R.fc(router, cond, c).values()) for c in CPS]
        rc5 = statistics.mean(R.rec(router, cond, 5).values())
        f5 = R.fc(router, cond, 5)
        old = [f5[q["qid"]] for q in R.D.qs(R.split, 5) if q["session"] < 5]
        new = [f5[q["qid"]] for q in R.D.qs(R.split, 5) if q["session"] == 5]
        short = sum(len(r["selected"]) < 5 for c in CPS for r in R.items(router, cond, c).values())
        total = sum(len(R.items(router, cond, c)) for c in CPS)
        out.append(f"| {cond} | " + " | ".join(pct(x) for x in fcs) + f" | {pct(statistics.mean(fcs))} | "
                   f"{pct(rc5)} | {pct(statistics.mean(old))} / {pct(statistics.mean(new))} | {short}/{total} |")
    return out + [""]


def side_table(R: Runs, router: str, conds: list[str]) -> list[str]:
    out = [f"### Router {router}: interference, incoming-skill probes and S5 error forms", "",
           "| Condition | correct at first checkpoint -> wrong at S5 | probe hit@5 | probe hit@1 | "
           "incoming skills in 5 slots (S5 mean) | missing skills at S5 | substitution | crowding | top types |",
           "|---|---|---|---|---|---|---|---|---|"]
    for cond in conds:
        if not R.complete(router, cond):
            continue
        ok, lost, n = R.interference(router, cond)
        pr = R.probes(router, cond)
        ph5 = f"{sum(pr[0])}/{len(pr[0])}" if pr else "-"
        ph1 = f"{sum(pr[1])}/{len(pr[1])}" if pr else "-"
        err = M.errors_at(R.D, R.items(router, cond, 5), R.D.qs(R.split, 5))
        tot = sum(err.values())
        sub = sum(err[t] for t in M.SUBST)
        crowd = sum(err[t] for t in M.CROWD)
        top = ", ".join(f"{t} {v}" for t, v in err.most_common(3))
        sl = M.incoming_slots(R.D, R.items(router, cond, 5), R.D.qs(R.split, 5))
        out.append(f"| {cond} | {lost} of {ok} (of {n}) | {ph5} | {ph1} | {statistics.mean(sl.values()):.2f} | "
                   f"{tot} | {sub} | {crowd} | {top} |")
    return out + [""]


def h4_pairs(R: Runs, router: str, gen: str):
    """Per query: pull events (incoming skill with an exclusion phrase about a skill the query needs, selected) under
    spp_<gen> and spp_noexcl_<gen>, over the same (query, skill) pairs."""
    rw = load_rewrites(gen)
    qs = R.D.qs(R.split, 5)
    pairs = M.exclusion_pairs(R.D, rw, qs)
    a_it, b_it = R.items(router, f"spp_{gen}", 5), R.items(router, f"spp_noexcl_{gen}", 5)
    per_q: dict = {}
    for qid, key in pairs:
        sid = R.D.id_of[key]
        a, b = int(sid in a_it[qid]["selected"]), int(sid in b_it[qid]["selected"])
        per_q.setdefault(qid, []).append((a, b))
    return pairs, per_q


def report(split: str) -> str:
    R = Runs(split)
    lines = [f"# Results: {split} split", ""]
    for router in ROUTERS:
        if not any(R.complete(router, c) for c in CONDS):
            continue
        lines += main_table(R, router, CONDS) + side_table(R, router, CONDS)
        for gen in ("haiku", "qwen3_4b"):
            if R.complete(router, f"spp_{gen}", [5]) and R.complete(router, f"spp_noexcl_{gen}", [5]):
                pairs, per_q = h4_pairs(R, router, gen)
                a = sum(x for v in per_q.values() for x, _ in v)
                b = sum(y for v in per_q.values() for _, y in v)
                lines.append(f"Exclusion pull ({gen}, {router}): {len(pairs)} (query, excluding skill) pairs over "
                             f"{len(per_q)} queries; selected with exclusions {a}, without {b}.")
        lines.append("")
    if split == "test":
        from .prereg import decisions
        lines += decisions(R)
    return "\n".join(lines)
