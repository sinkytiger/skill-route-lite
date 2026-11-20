"""Character n-gram TF-IDF similarity (numpy only). Stands in for the paper's MiniLM and Qwen3-Embedding models.

The vectorizer is fitted once on the skill corpus (original names, descriptions, bodies and the generator's synthetic
queries of all skills); evaluation queries are never part of it. Like a pretrained embedding model, it is fixed while
the library grows.
"""

from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np


def _grams(text: str, lo: int = 3, hi: int = 5) -> Counter:
    c: Counter = Counter()
    for w in re.findall(r"[a-z0-9가-힣%&/.+-]+", text.lower()):
        w = f" {w} "
        for n in range(lo, hi + 1):
            for i in range(max(1, len(w) - n + 1)):
                c[w[i:i + n]] += 1
    return c


class CharTfidf:
    def __init__(self, corpus: list[str], min_df: int = 2):
        df: Counter = Counter()
        for t in corpus:
            df.update(set(_grams(t)))
        vocab = sorted(g for g, d in df.items() if d >= min_df)
        self.index = {g: i for i, g in enumerate(vocab)}
        n = len(corpus)
        self.idf = np.array([math.log((1 + n) / (1 + df[g])) + 1.0 for g in vocab], dtype=np.float32)

    def vec(self, texts: list[str]) -> np.ndarray:
        m = np.zeros((len(texts), len(self.index)), dtype=np.float32)
        for r, t in enumerate(texts):
            for g, c in _grams(t).items():
                j = self.index.get(g)
                if j is not None:
                    m[r, j] = (1.0 + math.log(c)) * self.idf[j]
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return m / norms
