"""v2 length control: Skill++ with a shorter description, everything else held fixed.

Starting from the Haiku-written Skill++ records (data/rewrites/haiku.json), only the description-differentiation call
is redone, with the same reference skill g, the same inputs and the same rules except the length limit: the prompt
asks for at most 110 characters and descriptions up to 130 are accepted (v1: 220 asked and enforced). Up to 5 tries;
a try over 130 is told its length. Haiku overshoots: three earlier runs that enforced 110 exactly fell back to the
original description for 62, 64 and 58 of 117 skills (one of them ran by mistake with unchanged settings); they are
kept in data/rewrites/archive/ and count toward spend. The exclusion phrases (after the name-head rule) and the
clarified names are reused as they are, and the clause is trimmed from the end to 160 characters in total (v1: 298). The result is
data/rewrites/haiku_short.json, used by the conditions spp_haiku_short, spp_noexcl_haiku_short, ...
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from . import build as B
from .rewrite import D_SCHEMA, _desc_ok, assemble

DESC_ASK, DESC_MAX_SHORT, LMAX_SHORT = 110, 130, 160   # asked for, accepted, total with the clause
TRIES_SHORT = 5   # v1 used 3; a try that is too long is told its length and retried
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "rewrites" / "haiku.json"
OUT = ROOT / "data" / "rewrites" / "haiku_short.json"

P_DIFF_SHORT = """You are improving the routing description of a NEW skill that is being added to a skill library. \
A router picks skills by reading only their names and short descriptions.

NEW skill name: {n_t}
NEW skill body (excerpt):
<new_body>
{b_t}
</new_body>

The most similar EXISTING skill in the library is shown only so that you can tell the two apart.
EXISTING skill name: {n_g}
EXISTING skill body (excerpt):
<existing_body>
{b_g}
</existing_body>

Write a description of the NEW skill, at most 110 characters, that:
- states only capabilities contained in the NEW skill's body;
- leads with what the NEW skill does that the EXISTING skill does not offer;
- never names or alludes to the EXISTING skill.
Return JSON: {{"description": "..."}}"""


def desc_ok_short(d, ref_name, own_name):
    d = _desc_ok(d, ref_name, own_name)
    return d if d is not None and len(d) <= DESC_MAX_SHORT else None


def run(gen) -> dict:
    src = json.loads(SRC.read_text(encoding="utf-8"))
    skills = {s["key"]: s for s in B.load("skills.json")}
    state = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {
        "generator": gen.model, "derived_from": "haiku.json", "desc_ask": DESC_ASK, "desc_max": DESC_MAX_SHORT,
        "lmax": LMAX_SHORT,
        "prompt": P_DIFF_SHORT, "skills": {}, "calls": []}
    t0 = time.time()
    for key, r in src["skills"].items():
        if key in state["skills"]:
            continue
        c, g = skills[key], skills[r["g"]]
        base = P_DIFF_SHORT.format(n_t=c["name"], b_t=c["body"][:1600], n_g=g["name"], b_g=g["body"][:1200])
        prompt, d_hat, tries = base, None, 0
        for a in range(TRIES_SHORT):
            val, log = gen.json(prompt, D_SCHEMA, 200, a)
            raw = val.get("description") if val else None
            res = desc_ok_short(raw, g["name"], c["name"]) if val else None
            state["calls"].append(dict(log, what="differentiate_short", key=key, attempt=a, passed=res is not None,
                                       chars=len(raw) if isinstance(raw, str) else None, text=raw))
            tries = a + 1
            if res is not None:
                d_hat = res
                break
            if isinstance(raw, str) and len(raw.strip()) > DESC_MAX_SHORT:
                prompt = base + (f"\n\nYour previous description had {len(raw.strip())} characters, over the "
                                 f"{DESC_ASK}-character limit. Write a shorter one.")
            else:
                prompt = base
        d_final = d_hat or c["desc"]
        assembled, used = assemble(d_final, r["phrases_kept"], LMAX_SHORT)
        state["skills"][key] = {"g": r["g"], "G": r["G"], "d_hat": d_final, "d_tries": tries,
                                "d_fallback": d_hat is None, "phrases_raw": r["phrases_raw"],
                                "phrases_kept": r["phrases_kept"], "phrases_used": used, "assembled": assembled,
                                "name_conflict": r["name_conflict"], "name": r["name"], "n_tries": r["n_tries"],
                                "name_fallback": r["name_fallback"]}
        tmp = OUT.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(OUT)
    state["seconds_total"] = state.get("seconds_total", 0) + round(time.time() - t0, 1)
    OUT.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    return state


if __name__ == "__main__":
    from .claude import Budget
    from .rewrite import ClaudeGen
    st = run(ClaudeGen("claude-haiku-5-5", Budget([ROOT / "data" / "rewrites", ROOT / "runs"])))
    import statistics
    r = st["skills"].values()
    print(len(st["skills"]), "skills; fallback", sum(x["d_fallback"] for x in r),
          "; mean assembled", round(statistics.mean(len(x["assembled"]) for x in r), 1),
          "; mean d_hat", round(statistics.mean(len(x["d_hat"]) for x in r), 1),
          "; phrases used", round(statistics.mean(len(x["phrases_used"]) for x in r), 2))
