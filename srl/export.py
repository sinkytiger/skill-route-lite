"""Exports saved routing decisions to CSV files in reports/.

    python -m srl.export test dev test2 v2dev

`test` and `dev` hold v1's six conditions (the v1 record); `test2` holds every v2 test run; `v2dev` holds the v2 dev
runs, which were made on v1's dev and test queries (retrieval conditions and the short Skill++ rewrites). v2 rows add
the split, the number of candidates the router saw and whether all required skills were among them.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from . import build as B
from .route import RUNS

ROOT = Path(__file__).resolve().parent.parent
V1_CONDS = {"vanilla", "spp_haiku", "spp_noexcl_haiku", "spp_noname_haiku", "bodydist_haiku", "spp_qwen3_4b"}


def _blocks(name: str) -> list[tuple[str, dict]]:
    if name in ("dev", "test", "test2"):
        splits = [name]
    elif name == "v2dev":
        splits = ["dev", "test"]
    else:
        raise ValueError(name)
    out = []
    for sp in splits:
        for f in sorted(RUNS.glob(f"*/*/{sp}/S*_o*.json")):
            st = json.loads(f.read_text(encoding="utf-8"))
            v1 = st["cond"] in V1_CONDS
            if (name in ("dev", "test") and v1) or name == "test2" or (name == "v2dev" and not v1):
                out.append((sp, st))
    return out


def export(name: str) -> Path:
    sk = {s["id"]: s for s in B.load("skills.json")}
    req = {q["qid"]: q for q in B.load("queries.json")}
    if (B.DATA / "queries_v2.json").exists():
        req.update({q["qid"]: q for q in B.load("queries_v2.json")})
    probes = {p["pid"]: p for p in B.load("probes.json")}
    v2 = name in ("test2", "v2dev")
    out = ROOT / "reports" / f"routing_{name}.csv"
    out.parent.mkdir(exist_ok=True)
    rows = []
    for sp, st in _blocks(name):
        for iid, r in sorted(st["items"].items()):
            need = req[iid]["required"] if iid in req else [probes[iid]["skill"]]
            sel_keys = [sk[i]["key"] for i in r["selected"]]
            hit = sum(k in sel_keys for k in need)
            row = {"router": st["router"], "condition": st["cond"], "checkpoint": st["checkpoint"],
                   "order_seed": st["order_seed"], "item": iid, "kind": "query" if iid in req else "probe",
                   "required": ";".join(need), "selected": ";".join(sel_keys),
                   "fc5": int(hit == len(need)), "recall5": round(hit / len(need), 4),
                   "parsed": int(r["parsed"]), "seconds": r.get("seconds", "")}
            if v2:
                cands = r.get("candidates")
                ck = {sk[i]["key"] for i in cands} if cands else None
                row = {"split": sp, **row, "candidates": len(cands) if cands else st["library_size"],
                       "all_required_shown": int(ck is None or all(k in ck for k in need))}
            rows.append(row)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return out


if __name__ == "__main__":
    import sys
    for s in sys.argv[1:]:
        print(export(s))
