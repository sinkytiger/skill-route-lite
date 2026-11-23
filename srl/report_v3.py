"""v3 tables (split test3; v2's test2 is v3's dev material) and the v3 pre-registered decisions.

v3 separates what the retriever reads from what the router reads: 'spp_haiku+r30tfidf@vanilla' retrieves the top 30
on the original metadata (the same candidates, in the same shuffled order, as 'vanilla+r30tfidf') and shows the
router the Skill++ metadata of those candidates.
"""

from __future__ import annotations

import statistics

from .report import Runs, main_table, pct, side_table
from .report_v2 import K, RET, SEEDS, ceiling, seed_mean

DEC = "@vanilla"
FULL = ["vanilla"]
RETR = ["vanilla" + RET, "spp_haiku" + RET, "spp_haiku" + RET + DEC, "spp_noexcl_haiku_short" + RET + DEC]
SEEDED = ["vanilla"] + RETR


def ceiling_table(R: Runs, router: str) -> list[str]:
    conds = [c for c in RETR if R.complete(router, c)]
    if not conds:
        return []
    out = [f"### Router {router}: share of queries whose required skills were all retrieved (top {K}, %)", "",
           "| Condition | " + " | ".join(f"S{c}" for c in range(1, 6)) + " |", "|---|" + "---|" * 5]
    for cond in conds:
        out.append(f"| {cond} | " + " | ".join(pct(ceiling(R, router, cond, c)) for c in range(1, 6)) + " |")
    return out + [""]


def seed_table(R: Runs, router: str) -> list[str]:
    rows = []
    for cond in SEEDED:
        if all(R.items(router, cond, 5, s) is not None for s in SEEDS):
            vals = [statistics.mean(R.fc(router, cond, 5, s).values()) for s in SEEDS]
            rows.append(f"| {cond} | " + " | ".join(pct(v) for v in vals) + f" | {pct(statistics.mean(vals))} |")
    if not rows:
        return []
    return [f"### Router {router}: FC@5 at S5 by seed (%; display order for the full list, candidate shuffle for "
            "top 30)", "", "| Condition | seed 0 | seed 1 | seed 2 | mean |", "|---|---|---|---|---|"] + rows + [""]


def report_v3(split: str = "test3") -> str:
    R = Runs(split)
    lines = [f"# v3 results: {split} split", ""]
    for router in ("qwen3:4b", "llama3.2:3b"):
        conds = [c for c in FULL + RETR if R.complete(router, c)]
        if not conds:
            continue
        lines += main_table(R, router, conds) + side_table(R, router, conds)
        lines += ceiling_table(R, router) + seed_table(R, router)
    if split == "test3":
        from .prereg_v3 import decisions_v3
        lines += decisions_v3(R)
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    print(report_v3(sys.argv[1] if len(sys.argv) > 1 else "test3"))
