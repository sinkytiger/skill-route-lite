"""v2 tables (split test2, and v1's dev/test splits as v2 dev material) and the v2 pre-registered decisions."""

from __future__ import annotations

import statistics

from . import metrics as M
from .report import Runs, main_table, pct, pp, side_table
from .route import parse_label
from .stats import boot_paired

K = 30
RET = f"+r{K}tfidf"
FULL = ["vanilla", "spp_haiku", "spp_noexcl_haiku", "spp_noexcl_haiku_short", "spp_haiku_short"]
RETR = [c + RET for c in ("vanilla", "spp_haiku", "spp_noexcl_haiku_short", "spp_haiku_short")]
SEEDS = (0, 1, 2)
SEEDED = ["vanilla", "spp_noexcl_haiku", "spp_noexcl_haiku_short"]


def ceiling(R: Runs, router: str, cond: str, c: int) -> float | None:
    """Share of queries whose required skills were all among the retrieved candidates."""
    it = R.items(router, cond, c)
    if it is None:
        return None
    qs = R.D.qs(R.split, c)
    hits = [all(R.D.id_of[k] in it[q["qid"]]["candidates"] for k in q["required"]) for q in qs if q["qid"] in it]
    return statistics.mean(hits) if hits else None


def ceiling_table(R: Runs, router: str) -> list[str]:
    conds = [c for c in RETR if R.complete(router, c)]
    if not conds:
        return []
    out = [f"### Router {router}: share of queries whose required skills were all retrieved (top {K}, %)", "",
           "| Condition | " + " | ".join(f"S{c}" for c in range(1, 6)) + " |", "|---|" + "---|" * 5]
    for cond in conds:
        out.append(f"| {cond} | " + " | ".join(pct(ceiling(R, router, cond, c)) for c in range(1, 6)) + " |")
    return out + [""]


def seed_mean(R: Runs, router: str, cond: str, seeds=SEEDS) -> dict[str, float] | None:
    """Per-query FC@5 at S5 averaged over display-order seeds (None if a seed is missing)."""
    per = []
    for s in seeds:
        if R.items(router, cond, 5, s) is None:
            return None
        per.append(R.fc(router, cond, 5, s))
    return {k: statistics.mean(p[k] for p in per) for k in per[0]}


def seed_table(R: Runs, router: str) -> list[str]:
    rows = []
    for cond in SEEDED:
        if all(R.items(router, cond, 5, s) is not None for s in SEEDS):
            vals = [statistics.mean(R.fc(router, cond, 5, s).values()) for s in SEEDS]
            rows.append(f"| {cond} | " + " | ".join(pct(v) for v in vals) + f" | {pct(statistics.mean(vals))} |")
    if not rows:
        return []
    return [f"### Router {router}: FC@5 at S5 by display-order seed (%)", "",
            "| Condition | seed 0 | seed 1 | seed 2 | mean |", "|---|---|---|---|---|"] + rows + [""]


def report_v2(split: str = "test2") -> str:
    R = Runs(split)
    lines = [f"# v2 results: {split} split", ""]
    for router in ("qwen3:4b", "llama3.2:3b"):
        conds = [c for c in FULL + RETR if R.complete(router, c)]
        if not conds:
            continue
        lines += main_table(R, router, conds) + side_table(R, router, conds)
        lines += ceiling_table(R, router) + seed_table(R, router)
    if split == "test2":
        from .prereg_v2 import decisions_v2
        lines += decisions_v2(R)
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    print(report_v2(sys.argv[1] if len(sys.argv) > 1 else "test2"))
