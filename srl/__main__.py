"""Command line.

  python -m srl build                                  write data/*.json from the catalog
  python -m srl rewrite --gen qwen3:4b|haiku            synthetic queries, Skill++ and Body-distilled rewrites
  python -m srl route --router qwen3:4b --split dev --conds vanilla,spp_qwen3_4b [--checkpoints 1,2,3,4,5]
                      [--order-seed 0] [--no-probes] [--probes-only]
  python -m srl report --split dev                     tables (and the pre-registered verdicts for test)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import build as B
from . import route as R

ROOT = Path(__file__).resolve().parent.parent
HAIKU = "claude-haiku-5-5"


def items_for(split: str, checkpoint: int, probes: bool, probes_only: bool) -> list[dict]:
    """v2's held-out split 'test2' has its own queries (data/queries_v2.json) and reuses v1's test probes."""
    source = "queries_v2.json" if split == "test2" else "queries.json"
    qs = [] if probes_only else [{"iid": q["qid"], "text": q["text"]} for q in B.load(source)
                                 if q["split"] == split and q["session"] <= checkpoint]
    probe_split = "test" if split == "test2" else split
    if (probes or probes_only) and checkpoint == 5:
        qs += [{"iid": p["pid"], "text": p["text"]} for p in B.load("probes.json") if p["split"] == probe_split]
    return qs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="srl")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    p = sub.add_parser("rewrite")
    p.add_argument("--gen", required=True)
    p.add_argument("--no-body-distilled", action="store_true")
    p = sub.add_parser("route")
    p.add_argument("--router", required=True)
    p.add_argument("--split", required=True, choices=["dev", "test", "test2"])
    p.add_argument("--conds", required=True)
    p.add_argument("--checkpoints", default="1,2,3,4,5")
    p.add_argument("--order-seed", type=int, default=0)
    p.add_argument("--no-probes", action="store_true")
    p.add_argument("--probes-only", action="store_true")
    p = sub.add_parser("report")
    p.add_argument("--split", required=True, choices=["dev", "test", "test2"])
    a = ap.parse_args(argv)

    if a.cmd == "build":
        B.build()
        return 0
    skills = B.load("skills.json")
    if a.cmd == "rewrite":
        from . import rewrite as W
        if a.gen == "haiku":
            from .claude import Budget
            gen = W.ClaudeGen(HAIKU, Budget([ROOT / "data" / "rewrites", ROOT / "runs"]))
        else:
            gen = W.LocalGen(a.gen)
        out = ROOT / "data" / "rewrites" / f"{gen.tag}.json"
        st = W.run(gen, skills, out, body_distilled=not a.no_body_distilled)
        print(f"{out.name}: {len(st['skills'])} incoming skills rewritten, {len(st['calls'])} calls")
        return 0
    if a.cmd == "route":
        claude = None
        if a.router.startswith("claude"):
            from .claude import Budget, ClaudeJSON
            claude = ClaudeJSON(a.router, Budget([ROOT / "data" / "rewrites", ROOT / "runs"]))
        rw_cache: dict = {}
        for cond in a.conds.split(","):
            for c in [int(x) for x in a.checkpoints.split(",")]:
                its = items_for(a.split, c, not a.no_probes, a.probes_only)
                if not its:
                    continue
                path = R.run_block(a.router, cond, a.split, c, a.order_seed, skills, its, rw_cache, claude)
                print(f"done {path.relative_to(ROOT)} ({len(its)} items)", flush=True)
        return 0
    if a.cmd == "report":
        from .report import report
        print(report(a.split))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
