"""v2 held-out queries: data/queries_v2.json, split "test2", built exactly like v1's test split (srl/build.py) but from
the new phrasings in srl/catalog_v2.py and a different seed. v1's files are not touched; v1's dev and test queries
are v2's dev material.
"""

from __future__ import annotations

import json
import random
from collections import Counter

from . import build as B
from .catalog_required import REQUIRED
from .catalog_v2 import PHRASES_TEST2

SEED_V2 = 20261122
N_ALL, N_NEW = 20, 12
OUT = B.DATA / "queries_v2.json"


def make_queries_v2(rng: random.Random) -> list[dict]:
    req = {r["key"]: dict(r, phrases_test2=PHRASES_TEST2[r["key"]]) for r in REQUIRED}
    used: Counter = Counter()
    phrase_i: Counter = Counter()
    out = []
    for s in B.SESSIONS:
        avail = [r["key"] for r in REQUIRED if r["session"] <= s]
        new = [r["key"] for r in REQUIRED if r["session"] == s]
        old = [k for k in avail if k not in new]
        if s == 0:
            plan = [(a, avail) for a in new]
        else:
            plan = [(new[j % len(new)], avail) for j in range(N_NEW)]
            for _ in range(N_ALL - N_NEW):
                plan.append((min(old, key=lambda k: (used[k], rng.random())), old))
        for anchor, pool in plan:
            k = B._size(rng)
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
                pool_p = req[x]["phrases_test2"]
                phrases.append(pool_p[phrase_i[x] % len(pool_p)])
                phrase_i[x] += 1
            order = list(range(len(chosen)))
            rng.shuffle(order)
            text = B._render([phrases[i] for i in order], rng.choice(B.COMPANIES), rng)
            out.append({"split": "test2", "session": s, "required": sorted(chosen), "text": text,
                        "needs_new": s > 0 and any(req[x]["session"] == s for x in chosen)})
    texts = [q["text"] for q in out]
    assert len(texts) == len(set(texts)), "duplicate query text"
    for n, q in enumerate(out):
        q["qid"] = f"v{n:03d}"
    return out


def build_v2(write: bool = True) -> list[dict]:
    assert set(PHRASES_TEST2) == {r["key"] for r in REQUIRED}
    assert all(len(v) == 4 for v in PHRASES_TEST2.values())
    qs = make_queries_v2(random.Random(SEED_V2))
    if write:
        OUT.write_text(json.dumps(qs, ensure_ascii=False, indent=1), encoding="utf-8")
    return qs


if __name__ == "__main__":
    qs = build_v2()
    print(len(qs), Counter(len(q["required"]) for q in qs), Counter(q["session"] for q in qs))
    print("digest", B.digest(qs))
    for q in qs[:3] + qs[60:62]:
        print(q["qid"], q["session"], q["required"], "|", q["text"])
