"""Builds the data files from the catalog written for this study.

data/skills.json   every skill with its display ID, install session, addition step, kind, target and original metadata
data/queries.json  evaluation queries (test and dev): text, release session, required skill keys
data/probes.json   one probe request per incoming skill (its own work), split test/dev

Session recipe (after the paper's Appendix B.1, scaled down): S0 installs 20 required skills; each later session
installs 4 new required skills, then the incoming skills of that session. Within a session the required skills come
first (catalog order), then the incoming skills in a seeded random order; every addition is one step.
Queries: each session releases 20 test and 6 dev queries. From S1 on, 12 test (4 dev) queries need one of the
session's new skills and 8 (2) need only earlier skills. A query needs 1, 2 or 3 skills (30/40/30%).
"""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from .catalog_incoming import INCOMING
from .catalog_required import REQUIRED

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SEED = 20261120
SESSIONS = range(6)

COMPANIES = ["Samsung Electronics", "SK hynix", "Hyundai Motor", "Kia", "LG Chem", "LG Energy Solution",
             "POSCO Holdings", "NAVER", "Kakao", "Celltrion", "Samsung Biologics", "Hyundai Mobis", "KT&G",
             "LG Electronics", "Samsung SDI", "Lotte Chemical", "CJ CheilJedang", "Amorepacific",
             "HD Hyundai Heavy Industries", "Hanwha Aerospace", "Korean Air", "E-mart", "Coway", "Orion",
             "Doosan Enerbility", "SK Telecom", "KT", "Hanmi Pharm", "Yuhan", "NCSoft", "Krafton", "HYBE",
             "Samsung C&T", "LG H&H", "S-Oil"]
CONNECTORS = ["Also, ", "Then ", "On top of that, ", "Next, ", "And "]
SIZE_P = [(1, 0.3), (2, 0.4), (3, 0.3)]
PER_SESSION = {"test": (20, 12), "dev": (6, 4)}   # (queries per session, of which need a new skill) for S1-S5


def validate() -> None:
    req = {r["key"]: r for r in REQUIRED}
    keys = [r["key"] for r in REQUIRED] + [i["key"] for i in INCOMING]
    assert len(keys) == len(set(keys)), "duplicate keys"
    assert len(REQUIRED) == 40 and Counter(r["session"] for r in REQUIRED) == {0: 20, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4}
    for i in INCOMING:
        assert 1 <= i["session"] <= 5, i["key"]
        assert i["kind"] in ("similar", "samename", "nameonly", "overclaim", "broad", "generic"), i["key"]
        if i["kind"] == "generic":
            assert i["target"] is None
            continue
        for t in [i["target"], *i["also"]]:
            assert t in req, (i["key"], t)
            assert req[t]["session"] < i["session"], f"{i['key']} arrives before its target {t}"
        if i["kind"] == "samename":
            assert i["name"] == req[i["target"]]["name"], i["key"]
        if i["kind"] == "similar":
            assert i["style"] in ("vague", "specific"), i["key"]


def _size(rng: random.Random) -> int:
    x, acc = rng.random(), 0.0
    for k, p in SIZE_P:
        acc += p
        if x < acc:
            return k
    return SIZE_P[-1][0]


def _render(phrases: list[str], company: str, rng: random.Random) -> str:
    out, named = [], False
    for j, p in enumerate(phrases):
        if "{co}" in p:
            if not named:
                p = p.replace("{co}", company)
                named = True
            else:
                p = p.replace("{co}'s", "its").replace("{co}", "the company")
        if j > 0:
            first = p.split(" ", 1)[0]
            if first not in ("I", "I'm", "I'd") and len(first) > 1 and first[1:2].islower():
                p = p[0].lower() + p[1:]
            p = rng.choice(CONNECTORS) + p
        out.append(p)
    return " ".join(out)


def make_queries(rng: random.Random) -> list[dict]:
    req = {r["key"]: r for r in REQUIRED}
    out = []
    for split in ("test", "dev"):
        used: Counter = Counter()
        phrase_i: Counter = Counter()
        n_all, n_new = PER_SESSION[split]
        for s in SESSIONS:
            avail = [r["key"] for r in REQUIRED if r["session"] <= s]
            new = [r["key"] for r in REQUIRED if r["session"] == s]
            old = [k for k in avail if k not in new]
            if s == 0:
                anchors = list(new) if split == "test" else []
                while len(anchors) < n_all:
                    anchors.append(min(new, key=lambda k: (used[k], rng.random())))
                plan = [(a, avail) for a in anchors]
            else:
                plan = [(new[j % len(new)], avail) for j in range(n_new)]
                for _ in range(n_all - n_new):
                    plan.append((min(old, key=lambda k: (used[k], rng.random())), old))
            for anchor, pool in plan:
                k = _size(rng)
                chosen = [anchor]
                fams = {req[anchor]["family"]}
                while len(chosen) < k:
                    cands = [x for x in pool if x not in chosen and req[x]["family"] not in fams]
                    if not cands:
                        break
                    pick = min(cands, key=lambda x: (used[x], rng.random()))
                    chosen.append(pick)
                    fams.add(req[pick]["family"])
                for x in chosen:
                    used[x] += 1
                phrases = []
                for x in chosen:
                    pool_p = req[x][f"phrases_{split}"]
                    phrases.append(pool_p[phrase_i[x] % len(pool_p)])
                    phrase_i[x] += 1
                order = list(range(len(chosen)))
                rng.shuffle(order)
                text = _render([phrases[i] for i in order], rng.choice(COMPANIES), rng)
                out.append({"split": split, "session": s, "required": sorted(chosen), "text": text,
                            "needs_new": s > 0 and any(req[x]["session"] == s for x in chosen)})
    texts = [q["text"] for q in out]
    assert len(texts) == len(set(texts)), "duplicate query text"
    for n, q in enumerate(out):
        q["qid"] = f"{q['split'][0]}{n:03d}"
    return out


def make_skills(rng: random.Random) -> list[dict]:
    codes = rng.sample(range(100, 1000), len(REQUIRED) + len(INCOMING))
    skills, step = [], 0
    for s in SESSIONS:
        batch = [dict(r, kind="required", target=None, also=[], style="") for r in REQUIRED if r["session"] == s]
        inc = [dict(i) for i in INCOMING if i["session"] == s]
        rng.shuffle(inc)
        for sk in batch + inc:
            sk["step"] = step
            step += 1
            skills.append(sk)
    for sk, c in zip(skills, codes):
        sk["id"] = f"k{c}"
    keep = ("id", "key", "step", "session", "kind", "target", "also", "style", "family", "name", "desc", "body")
    return [{k: sk.get(k, "") for k in keep} for sk in skills]


def make_probes(rng: random.Random) -> list[dict]:
    out = []
    for n, i in enumerate(INCOMING):
        text = i["probe"].replace("{co}", rng.choice(COMPANIES))
        out.append({"pid": f"p{n:03d}", "split": "dev" if n % 4 == 3 else "test", "skill": i["key"],
                    "session": i["session"], "text": text})
    return out


def digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def build(write: bool = True) -> dict:
    validate()
    rng = random.Random(SEED)
    skills = make_skills(rng)
    queries = make_queries(rng)
    probes = make_probes(rng)
    files = {"skills.json": skills, "queries.json": queries, "probes.json": probes}
    if write:
        DATA.mkdir(exist_ok=True)
        for name, obj in files.items():
            (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    return files


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    f = build()
    sk, qs, pr = f["skills.json"], f["queries.json"], f["probes.json"]
    for s in SESSIONS:
        lib = [x for x in sk if x["session"] <= s]
        print(f"S{s}: library {len(lib)} (+{sum(x['session'] == s for x in sk)}), "
              f"test queries {sum(q['session'] <= s and q['split'] == 'test' for q in qs)}, "
              f"dev {sum(q['session'] <= s and q['split'] == 'dev' for q in qs)}")
    print("kinds:", Counter(x["kind"] for x in sk))
    print("sizes:", Counter((q["split"], len(q["required"])) for q in qs))
    print("probes:", Counter(p["split"] for p in pr))
    print({k: digest(v) for k, v in f.items()})
