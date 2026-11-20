"""Exports every saved routing decision of a split to reports/routing_<split>.csv (runs/ is not committed)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from . import build as B
from .route import RUNS

ROOT = Path(__file__).resolve().parent.parent


def export(split: str) -> Path:
    sk = {s["id"]: s for s in B.load("skills.json")}
    req = {q["qid"]: q for q in B.load("queries.json")}
    probes = {p["pid"]: p for p in B.load("probes.json")}
    out = ROOT / "reports" / f"routing_{split}.csv"
    out.parent.mkdir(exist_ok=True)
    rows = []
    for f in sorted(RUNS.glob(f"*/*/{split}/S*_o*.json")):
        st = json.loads(f.read_text(encoding="utf-8"))
        for iid, r in sorted(st["items"].items()):
            if iid in req:
                need = req[iid]["required"]
            else:
                need = [probes[iid]["skill"]]
            sel_keys = [sk[i]["key"] for i in r["selected"]]
            hit = sum(k in sel_keys for k in need)
            rows.append({"router": st["router"], "condition": st["cond"], "checkpoint": st["checkpoint"],
                         "order_seed": st["order_seed"], "item": iid, "kind": "query" if iid in req else "probe",
                         "required": ";".join(need), "selected": ";".join(sel_keys),
                         "fc5": int(hit == len(need)), "recall5": round(hit / len(need), 4),
                         "parsed": int(r["parsed"]), "seconds": r.get("seconds", "")})
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return out


if __name__ == "__main__":
    import sys
    for s in sys.argv[1:]:
        print(export(s))
