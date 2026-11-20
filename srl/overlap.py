"""Checks that the generators' synthetic queries (used only to pick exclusion references) do not copy evaluation
queries or probes: highest character n-gram TF-IDF cosine between any synthetic query and any evaluation text."""

from __future__ import annotations

import json

from . import build as B
from .conditions import REWRITES
from .textsim import CharTfidf


def check(tag: str, threshold: float = 0.8) -> dict:
    syn = json.loads((REWRITES / f"{tag}.json").read_text(encoding="utf-8"))["synthetic"]
    sq = [(k, q) for k, qs in syn.items() for q in qs]
    ev = [q["text"] for q in B.load("queries.json")] + [p["text"] for p in B.load("probes.json")]
    tf = CharTfidf([q for _, q in sq] + ev)
    S = tf.vec([q for _, q in sq]) @ tf.vec(ev).T
    best = S.max(axis=1)
    i = int(best.argmax())
    return {"generator": tag, "synthetic_queries": len(sq), "evaluation_texts": len(ev),
            "max_cosine": round(float(best.max()), 3), f"n_at_or_above_{threshold}": int((best >= threshold).sum()),
            "closest_pair": [sq[i][1], ev[int(S[i].argmax())]]}


if __name__ == "__main__":
    import sys
    for t in sys.argv[1:]:
        print(json.dumps(check(t), ensure_ascii=False, indent=1))
