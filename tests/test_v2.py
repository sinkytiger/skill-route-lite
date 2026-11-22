"""v2 data: fresh held-out queries and the length-controlled rewrites."""

import json
from collections import Counter

from srl import build as B
from srl import build_v2 as V
from srl import rewrite_v2 as W2
from srl.catalog_required import REQUIRED
from srl.catalog_v2 import PHRASES_TEST2
from srl.conditions import load_rewrites, metadata
from srl.route import parse_label


def test_test2_rebuilds_and_is_fresh():
    qs = V.build_v2(write=False)
    assert B.load("queries_v2.json") == qs
    assert Counter(q["session"] for q in qs) == {s: 20 for s in range(6)}
    v1_phrases = {p for r in REQUIRED for p in r["phrases_test"] + r["phrases_dev"]}
    new = [p for v in PHRASES_TEST2.values() for p in v]
    assert len(new) == len(set(new)) == 160 and not v1_phrases & set(new)
    assert not {q["text"] for q in qs} & {q["text"] for q in B.load("queries.json")}
    sk = {s["key"]: s for s in B.load("skills.json")}
    for q in qs:
        assert all(sk[k]["kind"] == "required" and sk[k]["session"] <= q["session"] for k in q["required"])
        assert "the company have" not in q["text"] and "the company shares" not in q["text"]


def test_short_rewrites_change_only_the_description():
    full, short = load_rewrites("haiku"), load_rewrites("haiku_short")
    assert set(full) == set(short)
    for k, r in short.items():
        f = full[k]
        for field in ("g", "G", "phrases_raw", "phrases_kept", "name", "name_conflict"):
            assert r[field] == f[field], (k, field)
        assert r["d_fallback"] or len(r["d_hat"]) <= W2.DESC_MAX_SHORT
        assert len(r["assembled"]) <= W2.LMAX_SHORT or not r["phrases_used"]
        assert r["assembled"].startswith(r["d_hat"])
    assert sum(r["d_fallback"] for r in short.values()) == 8


def test_noexcl_short_differs_from_noexcl_only_in_description_text():
    sk = B.load("skills.json")
    a, b = metadata("spp_noexcl_haiku", sk), metadata("spp_noexcl_haiku_short", sk)
    for s in sk:
        assert a[s["key"]][0] == b[s["key"]][0]                  # same names everywhere
        if s["kind"] == "required":
            assert a[s["key"]] == b[s["key"]]


def test_retrieval_labels():
    assert parse_label("spp_haiku+r20tfidf") == ("spp_haiku", 20, "tfidf")
    assert parse_label("vanilla") == ("vanilla", None, None)
