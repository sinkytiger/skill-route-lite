"""Scores from saved routing blocks.

FC@5      1 if every required skill of the query is among the 5 selected IDs (paper's primary metric)
Recall@5  share of the query's required skills among the 5 selected IDs
At checkpoint c, the queries scored are all queries released at S0..Sc (as in the paper). They split into
  old: released before c (stability)      new: released at c (plasticity of the newly installed required skills)
Interference set: queries released at S0..S4, each scored at its first checkpoint (S1 for S0 queries, else its
release session) and again at S5 ("correct when first available, wrong at S5", paper Appendix C.1).
Probes (S5 only): hit@5 / hit@1 of the incoming skill the probe was written for (plasticity of incoming skills).
Error types (S5): every required skill missing from the selection gets one type, decided from the generator's
labels (kind and target of each incoming skill), in the paper's order: description inconsistency, similar-skill
confusion (same name or not), scope overreach, name confusion (substitution: a selected incoming skill targets the
missing skill); then duplicate crowding (a selected incoming skill targets another required skill of the query, or
two selected skills share a target), generic crowding (a generic skill was selected), other. As in the paper's
Table A3, "other" is a third column, not part of crowding.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from . import build as B
from .route import block_path

SUBST = ("description_inconsistency", "similar_same_name", "similar", "scope_overreach", "name_confusion")
CROWD = ("duplicate_crowding", "generic_crowding")   # "other" is counted apart, as the paper does
KIND_TYPE = {"overclaim": "description_inconsistency", "samename": "similar_same_name", "similar": "similar",
             "broad": "scope_overreach", "nameonly": "name_confusion"}


class Data:
    def __init__(self):
        self.skills = B.load("skills.json")
        self.queries = B.load("queries.json")
        if (B.DATA / "queries_v2.json").exists():
            self.queries += B.load("queries_v2.json")
        self.probes = B.load("probes.json")
        self.by_key = {s["key"]: s for s in self.skills}
        self.by_id = {s["id"]: s for s in self.skills}
        self.id_of = {s["key"]: s["id"] for s in self.skills}

    def qs(self, split: str, upto: int | None = None) -> list[dict]:
        return [q for q in self.queries if q["split"] == split and (upto is None or q["session"] <= upto)]

    def pr(self, split: str) -> list[dict]:
        split = "test" if split == "test2" else split      # v2 reuses v1's test probes
        return [p for p in self.probes if p["split"] == split]


def load_items(router: str, cond: str, split: str, c: int, seed: int = 0) -> dict | None:
    p = block_path(router, cond, split, c, seed)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))["items"]


def fc_recall(sel_ids: list[str], req_ids: list[str]) -> tuple[int, float]:
    hit = sum(r in sel_ids for r in req_ids)
    return int(hit == len(req_ids)), hit / len(req_ids)


def per_query(D: Data, items: dict, queries: list[dict]) -> dict[str, tuple[int, float]]:
    out = {}
    for q in queries:
        rec = items.get(q["qid"])
        if rec is None:
            raise KeyError(f"missing routing result for {q['qid']}")
        out[q["qid"]] = fc_recall(rec["selected"], [D.id_of[k] for k in q["required"]])
    return out


def first_checkpoint(q: dict) -> int:
    return max(1, q["session"])


def error_type(D: Data, missing: str, sel_ids: list[str], required: list[str]) -> str:
    sel = [D.by_id[i] for i in sel_ids]
    inc = [s for s in sel if s["kind"] not in ("required", "generic")]
    hits = [s for s in inc if missing == s["target"] or missing in s["also"]]
    if hits:
        types = {KIND_TYPE[s["kind"]] for s in hits}
        for t in SUBST:
            if t in types:
                return t
    others = [r for r in required if r != missing]
    targets = Counter(s["target"] for s in inc)
    if any(s["target"] in others or set(s["also"]) & set(others) for s in inc) or any(v > 1 for v in targets.values()):
        return "duplicate_crowding"
    if any(s["kind"] == "generic" for s in sel):
        return "generic_crowding"
    return "other"


def errors_at(D: Data, items: dict, queries: list[dict]) -> Counter:
    c: Counter = Counter()
    for q in queries:
        sel = items[q["qid"]]["selected"]
        for k in q["required"]:
            if D.id_of[k] not in sel:
                c[error_type(D, k, sel, q["required"])] += 1
    return c


def incoming_slots(D: Data, items: dict, queries: list[dict]) -> dict[str, int]:
    """Per query: how many of the selected IDs are incoming skills (none of which any query needs)."""
    return {q["qid"]: sum(D.by_id[i]["kind"] != "required" for i in items[q["qid"]]["selected"]) for q in queries}


def exclusion_pairs(D: Data, rw: dict, queries: list[dict]) -> list[tuple[str, str]]:
    """(qid, incoming skill key) pairs where the incoming skill's kept exclusion phrases (Skill++ full) were written
    for a reference skill that the query requires: the H4 'pull' events are these skills being selected."""
    refs_of = {}
    for key, r in rw.items():
        raw = r["phrases_raw"] if len(r["phrases_raw"]) == len(r["G"]) else []
        refs_of[key] = {g for g, p in zip(r["G"], raw) if p in r["phrases_used"]}
    out = []
    for q in queries:
        need = set(q["required"])
        for key in sorted(refs_of):
            if need & refs_of[key]:
                out.append((q["qid"], key))
    return out
