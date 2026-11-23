"""Data files for the v2 results dashboard, computed from the raw test2 runs.

    python -m srl.dashboard_data <out_dir>

Writes fc.json, decisions.json, extras.json, order.json, ceiling.json and probes.json, each {rows, meta}, where meta
holds this script's own text. Uses the same scoring and statistics code as reports/results_test2.md
(srl.report.Runs, srl.report_v2, srl.stats: paired bootstrap 10,000 resamples seed 0, exact McNemar).
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

import numpy as np

from .prereg_v2 import R1_DROP, V1_MAX_GAIN, V2_GAIN, V4_SHARE, _fall_stat
from .report import Runs
from .report_v2 import RET, seed_mean
from .stats import boot_paired, boot_stat, discordant, mcnemar_exact, r1

SPLIT = "test2"
CPS = (1, 2, 3, 4, 5)
QWEN, LLAMA = "qwen3:4b", "llama3.2:3b"
FULL = ["vanilla", "spp_haiku", "spp_noexcl_haiku", "spp_noexcl_haiku_short", "spp_haiku_short"]
NARROW = [c + RET for c in ("vanilla", "spp_haiku", "spp_noexcl_haiku_short", "spp_haiku_short")]
LLAMA_CONDS = ["vanilla", "spp_haiku", "vanilla" + RET, "spp_haiku" + RET]


def f1(x) -> float:
    return float(r1(x))


def pc(x) -> float:
    return f1(100 * x)


def diff_row(id_, a: dict, b: dict, note: str) -> dict:
    k = sorted(a)
    x, y = [a[i] for i in k], [b[i] for i in k]
    d = boot_paired(x, y)
    bb, cc = discordant([round(v) for v in x], [round(v) for v in y]) if all(v in (0, 1) for v in x + y) else (None, None)
    return {"id": id_, "value": f1(100 * d[0]), "ci_low": f1(100 * d[1]), "ci_high": f1(100 * d[2]),
            "a": pc(statistics.mean(x)), "b": pc(statistics.mean(y)),
            "mcnemar_p": round(mcnemar_exact(bb, cc), 4) if bb is not None else None, "note": note}


def main(out: Path) -> None:
    R = Runs(SPLIT)
    qs = R.D.qs(SPLIT)
    code = Path(__file__).read_text(encoding="utf-8")
    meta = [{"label": "dashboard_data.py", "value": code, "type": "code", "lang": "python"},
            {"label": "Input", "value": "runs/route/<router>/<condition>/test2/S<c>_o<seed>.json, data/*.json "
                                        "(github.com/sinkytiger/skill-route-lite, commit 37b29be)"}]

    def dump(name, rows):
        (out / name).write_text(json.dumps({"rows": rows, "meta": meta}, ensure_ascii=False, indent=1),
                                encoding="utf-8")

    # FC@5 by checkpoint
    fc = []
    for router, conds in ((QWEN, FULL + NARROW), (LLAMA, LLAMA_CONDS)):
        for cond in conds:
            for c in CPS:
                f = R.fc(router, cond, c)
                fc.append({"key": f"{router}|{cond}|S{c}", "router": router, "condition": cond.replace(RET, ""),
                           "list": "top30" if cond.endswith(RET) else "full", "checkpoint": f"S{c}",
                           "queries": len(f), "correct": sum(f.values()), "fc5": pc(statistics.mean(f.values()))})
    dump("fc.json", fc)

    # pre-registered decisions (qwen3:4b), same rules as srl/prereg_v2.py
    n = len(qs)
    dec = []
    d = boot_stat(n, _fall_stat(R, QWEN, "vanilla"))
    r1_holds = d[0] >= R1_DROP and d[1] > 0
    dec.append({"id": "R1", "value": f1(100 * d[0]), "ci_low": f1(100 * d[1]), "ci_high": f1(100 * d[2]),
                "verdict": "holds" if r1_holds else "not supported", "threshold": 15.0})
    a, b = seed_mean(R, QWEN, "spp_noexcl_haiku_short"), seed_mean(R, QWEN, "spp_noexcl_haiku")
    k = sorted(a)
    d = boot_paired([a[i] for i in k], [b[i] for i in k])
    dec.append({"id": "V1", "value": f1(100 * d[0]), "ci_low": f1(100 * d[1]), "ci_high": f1(100 * d[2]),
                "verdict": "holds" if d[2] < V1_MAX_GAIN else "not supported", "threshold": 5.0})
    a, b = R.fc(QWEN, "vanilla" + RET, 5), seed_mean(R, QWEN, "vanilla")
    d = boot_paired([a[i] for i in k], [b[i] for i in k])
    dec.append({"id": "V2", "value": f1(100 * d[0]), "ci_low": f1(100 * d[1]), "ci_high": f1(100 * d[2]),
                "verdict": "holds" if d[0] >= V2_GAIN and d[1] > 0 else "not supported", "threshold": 10.0})
    a, b = R.fc(QWEN, "spp_haiku" + RET, 5), R.fc(QWEN, "vanilla" + RET, 5)
    d = boot_paired([a[i] for i in k], [b[i] for i in k])
    dec.append({"id": "V3", "value": f1(100 * d[0]), "ci_low": f1(100 * d[1]), "ci_high": f1(100 * d[2]),
                "verdict": "holds" if d[1] > 0 else "not supported", "threshold": 0.0})
    full, ret = _fall_stat(R, QWEN, "vanilla"), _fall_stat(R, QWEN, "vanilla" + RET)
    df, dr = boot_stat(n, full), boot_stat(n, ret)
    dd = boot_stat(n, lambda idx: full(idx) - ret(idx))
    v4 = r1_holds and dr[0] <= V4_SHARE * df[0] and dd[1] > 0
    dec.append({"id": "V4", "value": f1(100 * dd[0]), "ci_low": f1(100 * dd[1]), "ci_high": f1(100 * dd[2]),
                "verdict": "holds" if v4 else "not supported", "threshold": 0.0,
                "fall_full": f1(100 * df[0]), "fall_top30": f1(100 * dr[0])})
    for row in dec:
        row["router"] = QWEN
    dump("decisions.json", dec)

    # exploratory and secondary figures
    ex = []
    ex.append(diff_row("qwen_v2_seed0", R.fc(QWEN, "vanilla" + RET, 5), R.fc(QWEN, "vanilla", 5),
                       "qwen3:4b, Vanilla top 30 minus full list, display order seed 0"))
    ex.append(diff_row("qwen_spp_full", R.fc(QWEN, "spp_haiku", 5), R.fc(QWEN, "vanilla", 5),
                       "qwen3:4b, full list, Skill++ (Haiku) minus Vanilla, S5, seed 0"))
    ex.append(diff_row("llama_v2_seed0", R.fc(LLAMA, "vanilla" + RET, 5), R.fc(LLAMA, "vanilla", 5),
                       "llama3.2:3b, Vanilla top 30 minus full list, S5, seed 0"))
    ex.append(diff_row("llama_spp_full", R.fc(LLAMA, "spp_haiku", 5), R.fc(LLAMA, "vanilla", 5),
                       "llama3.2:3b, full list, Skill++ (Haiku) minus Vanilla, S5"))
    ex.append(diff_row("llama_spp_top30", R.fc(LLAMA, "spp_haiku" + RET, 5), R.fc(LLAMA, "vanilla" + RET, 5),
                       "llama3.2:3b, top 30, Skill++ (Haiku) minus Vanilla, S5"))
    d = boot_stat(n, _fall_stat(R, LLAMA, "vanilla"))
    ex.append({"id": "llama_r1", "value": f1(100 * d[0]), "ci_low": f1(100 * d[1]), "ci_high": f1(100 * d[2]),
               "note": "llama3.2:3b, Vanilla full list, S1 -> S5 fall"})

    # retrieval trade-off at S5 (qwen3:4b, seed 0)
    v_it, s_it = R.items(QWEN, "vanilla" + RET, 5), R.items(QWEN, "spp_haiku" + RET, 5)
    by_id = R.D.by_id
    keys = lambda ids: {by_id[i]["key"] for i in ids}
    shown = lambda r, q: all(x in keys(r["candidates"]) for x in q["required"])
    hit = lambda r, q: all(x in keys(r["selected"]) for x in q["required"])
    vs = [shown(v_it[q["qid"]], q) for q in qs]
    ss = [shown(s_it[q["qid"]], q) for q in qs]
    lost = [q for q, a_, b_ in zip(qs, vs, ss) if a_ and not b_]
    gained = [q for q, a_, b_ in zip(qs, vs, ss) if b_ and not a_]
    both = [q for q, a_, b_ in zip(qs, vs, ss) if a_ and b_]
    x = [int(hit(s_it[q["qid"]], q)) for q in both]
    y = [int(hit(v_it[q["qid"]], q)) for q in both]
    dpair = boot_paired(x, y)
    bb, cc = discordant(x, y)
    ex += [
        {"id": "retrieved_vanilla", "value": sum(vs), "note": "queries with all required skills among the 30, Vanilla"},
        {"id": "retrieved_spp", "value": sum(ss), "note": "queries with all required skills among the 30, Skill++"},
        {"id": "retrieval_lost", "value": len(lost), "note": "retrieved fully under Vanilla only",
         "mcnemar_p": round(mcnemar_exact(len(lost), len(gained)), 4)},
        {"id": "retrieval_gained", "value": len(gained), "note": "retrieved fully under Skill++ only"},
        {"id": "vanilla_correct_on_lost", "value": sum(hit(v_it[q["qid"]], q) for q in lost),
         "note": "of the lost queries, answered correctly by Vanilla"},
        {"id": "both_retrieved", "value": len(both), "note": "queries both conditions retrieved fully"},
        {"id": "both_correct_spp", "value": sum(x), "note": "correct under Skill++ among them"},
        {"id": "both_correct_vanilla", "value": sum(y), "note": "correct under Vanilla among them"},
        {"id": "both_diff", "value": f1(100 * dpair[0]), "ci_low": f1(100 * dpair[1]), "ci_high": f1(100 * dpair[2]),
         "mcnemar_p": round(mcnemar_exact(bb, cc), 4), "note": "Skill++ minus Vanilla on those queries"},
        {"id": "prompt_full_vanilla", "value": round(statistics.mean(r["prompt_tokens"] for k_, r in
                                                                    R.items(QWEN, "vanilla", 5).items()
                                                                    if k_.startswith("v"))),
         "note": "mean prompt tokens at S5, test2 queries"},
        {"id": "prompt_top30_vanilla", "value": round(statistics.mean(v_it[q["qid"]]["prompt_tokens"] for q in qs)),
         "note": "mean prompt tokens at S5, test2 queries"},
    ]
    dump("extras.json", ex)

    # display order (qwen3:4b, S5)
    order = []
    for cond in ("vanilla", "spp_noexcl_haiku", "spp_noexcl_haiku_short"):
        for s in (0, 1, 2):
            f = R.fc(QWEN, cond, 5, s)
            order.append({"key": f"{cond}|{s}", "condition": cond, "seed": str(s), "fc5": pc(statistics.mean(f.values()))})
        m = seed_mean(R, QWEN, cond)
        order.append({"key": f"{cond}|mean", "condition": cond, "seed": "mean", "fc5": pc(statistics.mean(m.values()))})
    dump("order.json", order)

    # retrieval ceiling (does not depend on the router)
    ceil = []
    for cond in NARROW:
        for c in CPS:
            it = R.items(QWEN, cond, c)
            q_c = R.D.qs(SPLIT, c)
            got = sum(shown(it[q["qid"]], q) for q in q_c)
            ceil.append({"key": f"{cond.replace(RET, '')}|S{c}", "condition": cond.replace(RET, ""),
                         "checkpoint": f"S{c}", "queries": len(q_c), "retrieved_all": got,
                         "share": pc(got / len(q_c))})
    dump("ceiling.json", ceil)

    # incoming-skill probes at S5
    pr = []
    for router, conds in ((QWEN, ["vanilla", "spp_haiku", "vanilla" + RET, "spp_haiku" + RET]), (LLAMA, LLAMA_CONDS)):
        for cond in conds:
            h5, h1 = R.probes(router, cond)
            pr.append({"key": f"{router}|{cond}", "router": router, "condition": cond.replace(RET, ""),
                       "list": "top30" if cond.endswith(RET) else "full", "probes": len(h5),
                       "hit5": int(np.sum(h5)), "hit1": int(np.sum(h1))})
    dump("probes.json", pr)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    main(out)
    print("wrote", sorted(p.name for p in out.glob("*.json")))
