"""Library metadata per condition. Only incoming skills differ between conditions; required skills always keep their
original name and description.

  vanilla            original metadata
  bodydist_<g>       description written from the skill's own body by generator g (original name)
  spp_<g>            Skill++ by generator g: clarified name + differentiated description + exclusion clause
  spp_noexcl_<g>     Skill++ without the exclusion clause
  spp_noname_<g>     Skill++ with the original name
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REWRITES = ROOT / "data" / "rewrites"
DISPLAY_CHARS = 300   # the router reads the first 300 characters of each description (paper, Appendix B.2)


def load_rewrites(tag: str) -> dict:
    return json.loads((REWRITES / f"{tag}.json").read_text(encoding="utf-8"))["skills"]


def parse(cond: str) -> tuple[str, str | None]:
    if cond == "vanilla":
        return "vanilla", None
    for v in ("spp_noexcl", "spp_noname", "bodydist", "spp"):
        if cond.startswith(v + "_"):
            return v, cond[len(v) + 1:]
    raise ValueError(cond)


def metadata(cond: str, skills: list[dict], rw_cache: dict | None = None) -> dict[str, tuple[str, str]]:
    """{skill key: (name, description)} for every skill under the condition."""
    variant, gen = parse(cond)
    rw = {}
    if gen is not None:
        rw_cache = rw_cache if rw_cache is not None else {}
        if gen not in rw_cache:
            rw_cache[gen] = load_rewrites(gen)
        rw = rw_cache[gen]
    out = {}
    for s in skills:
        name, desc = s["name"], s["desc"]
        if s["kind"] != "required" and variant != "vanilla":
            r = rw[s["key"]]
            if variant == "bodydist":
                desc = r["bd_desc"]
            elif variant == "spp":
                name, desc = r["name"], r["assembled"]
            elif variant == "spp_noexcl":
                name, desc = r["name"], r["d_hat"]
            elif variant == "spp_noname":
                desc = r["assembled"]
        out[s["key"]] = (name, desc)
    return out
