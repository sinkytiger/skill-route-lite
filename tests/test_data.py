"""The data are rebuilt from the catalog and must match the saved files; required/incoming roles must hold."""

from collections import Counter

from srl import build as B


def test_rebuild_matches_saved_files():
    files = B.build(write=False)
    for name, obj in files.items():
        assert B.load(name) == obj, f"{name} differs from a fresh build"


def test_library_growth_and_counts():
    sk = B.load("skills.json")
    sizes = [sum(s["session"] <= c for s in sk) for c in range(6)]
    assert sizes == [20, 48, 76, 104, 131, 157]
    assert Counter(s["kind"] for s in sk)["required"] == 40
    assert len({s["id"] for s in sk}) == len(sk)
    assert [s["step"] for s in sorted(sk, key=lambda s: s["step"])] == list(range(len(sk)))
    # within a session, required skills are added before incoming skills
    for c in range(6):
        steps = [(s["kind"] != "required", s["step"]) for s in sk if s["session"] == c]
        assert sorted(steps) == sorted(steps, key=lambda x: x[1])


def test_queries_need_only_installed_required_skills():
    sk = {s["key"]: s for s in B.load("skills.json")}
    qs = B.load("queries.json")
    assert Counter(q["split"] for q in qs) == {"test": 120, "dev": 36}
    for q in qs:
        assert 1 <= len(q["required"]) <= 3
        for k in q["required"]:
            assert sk[k]["kind"] == "required"
            assert sk[k]["session"] <= q["session"]
        assert q["needs_new"] == (q["session"] > 0 and any(sk[k]["session"] == q["session"] for k in q["required"]))
    for s in range(6):
        assert sum(q["split"] == "test" and q["session"] == s for q in qs) == 20
        assert sum(q["split"] == "dev" and q["session"] == s for q in qs) == 6


def test_dev_and_test_use_disjoint_phrasings():
    from srl.catalog_required import REQUIRED
    for r in REQUIRED:
        assert not set(r["phrases_test"]) & set(r["phrases_dev"]), r["key"]
    qs = B.load("queries.json")
    assert not {q["text"] for q in qs if q["split"] == "dev"} & {q["text"] for q in qs if q["split"] == "test"}


def test_probes_belong_to_incoming_skills():
    sk = {s["key"]: s for s in B.load("skills.json")}
    pr = B.load("probes.json")
    assert len(pr) == sum(s["kind"] != "required" for s in sk.values())
    assert all(sk[p["skill"]]["kind"] != "required" for p in pr)
    assert Counter(p["split"] for p in pr) == {"test": 88, "dev": 29}
