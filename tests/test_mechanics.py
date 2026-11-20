"""Skill++ mechanics, routing helpers, metrics and statistics on small hand-made cases."""

import numpy as np

from srl import metrics as M
from srl import rewrite as W
from srl import route as R
from srl.stats import boot_paired, discordant, mcnemar_exact


def test_name_head_rule():
    assert W.name_head("dividend-yield-payout") == "dividend"
    assert W.name_head("pe-band-chart") is None            # heads of 3 characters or fewer do not count
    assert W.name_head("Bond Duration") == "bond"
    assert W.name_head("risk—dashboard") == "risk"
    assert W.name_conflict("dividend-calculator", ["dividend-yield-payout"])
    assert not W.name_conflict("trailing-pe", ["pe-band-chart"])
    assert W.name_conflict("trailing-pe", ["trailing-pe"])


def test_fused_rank_prefers_any_single_top_rank_then_sum():
    s1 = np.array([0.9, 0.1, 0.5, 0.2])
    s2 = np.array([0.1, 0.9, 0.5, 0.2])
    s3 = np.array([0.2, 0.2, 0.6, 0.9])
    # ranks (1 = most similar; ties by addition order): s1 0,2,3,1  s2 1,2,3,0  s3 3,2,0,1
    # (min rank, sum of ranks): 0 (1, 8), 1 (1, 9), 2 (2, 6), 3 (1, 7) -> 3, 0, 1; 2 is never first
    assert W.fused_top(s1, s2, s3, 3) == [3, 0, 1]


def test_assemble_trims_phrases_from_the_end():
    d = "x" * 200
    text, used = W.assemble(d, ["a" * 40, "b" * 40, "c" * 40])
    assert len(text) <= W.LMAX and used == ["a" * 40]
    text, used = W.assemble("short", [])
    assert text == "short" and used == []


def test_description_checks():
    assert W._desc_ok("ok text", "ref-name", "own") == "ok text"
    assert W._desc_ok("y" * 221, None, "own") is None
    assert W._desc_ok("unlike ref-name this does more", "ref-name", "own") is None
    assert W._desc_ok("same name allowed: trailing-pe", "trailing-pe", "trailing-pe") is not None
    assert W._name_ok("abc") is None and W._name_ok("abcd") == "abcd" and W._name_ok("x" * 61) is None


def test_display_order_is_deterministic_and_condition_free():
    lib = [{"id": f"k{i}", "step": i, "session": 0} for i in range(30)]
    a = R.display_order(lib, 3, 0)
    b = R.display_order(lib, 3, 0)
    c = R.display_order(lib, 3, 1)
    assert [x["id"] for x in a] == [x["id"] for x in b] != [x["id"] for x in c]


def test_parse_selection_dedupes_and_drops_unknown_ids():
    sel, ok = R.parse_selection('{"skills": ["k1", "k1", "k9", "k2"]}', {"k1", "k2"})
    assert ok and sel == ["k1", "k2"]
    assert R.parse_selection("not json", {"k1"}) == ([], False)


def test_fc_and_recall():
    assert M.fc_recall(["a", "b", "c", "d", "e"], ["a", "c"]) == (1, 1.0)
    assert M.fc_recall(["a", "b", "c", "d", "e"], ["a", "z"]) == (0, 0.5)


class _D:
    def __init__(self, skills):
        self.by_id = {s["id"]: s for s in skills}


def _sk(i, kind, target=None, also=()):
    return {"id": i, "key": i, "kind": kind, "target": target, "also": list(also)}


def test_error_types_follow_the_paper_order():
    D = _D([_sk("R", "required"), _sk("Q", "required"), _sk("o", "overclaim", "R"), _sk("s", "similar", "R"),
            _sk("n", "nameonly", "R"), _sk("d", "similar", "Q"), _sk("g", "generic"), _sk("b", "broad", "X", ["R"])])
    assert M.error_type(D, "R", ["s", "o", "Q"], ["R", "Q"]) == "description_inconsistency"
    assert M.error_type(D, "R", ["n", "s"], ["R"]) == "similar"
    assert M.error_type(D, "R", ["b"], ["R"]) == "scope_overreach"
    assert M.error_type(D, "R", ["n"], ["R"]) == "name_confusion"
    assert M.error_type(D, "R", ["d", "Q"], ["R", "Q"]) == "duplicate_crowding"
    assert M.error_type(D, "R", ["g", "Q"], ["R", "Q"]) == "generic_crowding"
    assert M.error_type(D, "R", ["Q"], ["R", "Q"]) == "other"


def test_mcnemar_and_bootstrap():
    assert mcnemar_exact(0, 0) == 1.0
    assert abs(mcnemar_exact(0, 6) - 0.03125) < 1e-12
    assert abs(mcnemar_exact(2, 8) - 0.109375) < 1e-12
    assert discordant([1, 1, 0, 0], [1, 0, 1, 0]) == (1, 1)
    m, lo, hi = boot_paired([1, 1, 1, 0], [0, 0, 1, 0])
    assert m == 0.5 and lo <= m <= hi
    assert boot_paired([1, 0, 1], [0, 0, 1]) == boot_paired([1, 0, 1], [0, 0, 1])
