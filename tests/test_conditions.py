"""The saved rewrites obey the Skill++ limits, and conditions differ only in incoming skills' metadata."""

import pytest

from srl import build as B
from srl import rewrite as W
from srl.conditions import load_rewrites, metadata

GENS = ["haiku", "qwen3_4b"]


@pytest.mark.parametrize("gen", GENS)
def test_rewrite_limits(gen):
    sk = {s["key"]: s for s in B.load("skills.json")}
    rw = load_rewrites(gen)
    assert set(rw) == {k for k, s in sk.items() if s["kind"] != "required"}
    for key, r in rw.items():
        s = sk[key]
        assert len(r["assembled"]) <= W.LMAX or r["phrases_used"] == []
        assert r["d_fallback"] or len(r["d_hat"]) <= W.DESC_MAX
        assert r["bd_fallback"] or len(r["bd_desc"]) <= W.DESC_MAX
        assert r["assembled"].startswith(r["d_hat"])
        if r["name_conflict"] and not r["name_fallback"]:
            assert W.NAME_MIN <= len(r["name"]) <= W.NAME_MAX
        else:
            assert r["name"] == s["name"]
        assert r["name_conflict"] == W.name_conflict(s["name"], [e["name"] for e in sk.values()
                                                                if e["step"] < s["step"]])
        assert set(r["phrases_used"]) <= set(r["phrases_kept"]) <= set(r["phrases_raw"])
        earlier = {e["key"] for e in sk.values() if e["step"] < s["step"]}
        assert r["g"] in earlier and set(r["G"]) <= earlier and len(r["G"]) == 3


@pytest.mark.parametrize("gen", GENS)
def test_conditions_change_only_incoming_skills(gen):
    sk = B.load("skills.json")
    rw = load_rewrites(gen)
    base = metadata("vanilla", sk)
    for cond in [f"spp_{gen}", f"spp_noexcl_{gen}", f"spp_noname_{gen}", f"bodydist_{gen}"]:
        m = metadata(cond, sk)
        for s in sk:
            if s["kind"] == "required":
                assert m[s["key"]] == base[s["key"]]
    full, noex, non = metadata(f"spp_{gen}", sk), metadata(f"spp_noexcl_{gen}", sk), metadata(f"spp_noname_{gen}", sk)
    for key, r in rw.items():
        assert full[key] == (r["name"], r["assembled"])
        assert noex[key] == (r["name"], r["d_hat"])
        assert non[key] == (base[key][0], r["assembled"])
