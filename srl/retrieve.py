"""v2 candidate narrowing: before the router call, keep only the K installed skills whose metadata is most similar to
the request (the paper's R&R baselines narrow to 50 candidates with an embedding retriever and a reranker; here one
retriever, no reranker). Similarity is computed on the same metadata the router reads under the condition
("name. first 300 characters of the description"), so rewrites change what is retrieved as well as what is read.

  tfidf  character 3-5-gram TF-IDF (srl/textsim.py), fitted on the library's metadata texts of the condition
  nomic  nomic-embed-text through Ollama, "search_query: " / "search_document: " prefixes, cosine; embeddings are
         cached in runs/emb_cache.json (deterministic, so the cache only saves time)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import requests

from .conditions import DISPLAY_CHARS
from .ollama import HOST
from .textsim import CharTfidf

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "runs" / "emb_cache.json"
EMBED_MODEL = "nomic-embed-text"


def doc_text(name: str, desc: str) -> str:
    return f"{name}. {desc[:DISPLAY_CHARS]}"


class Embedder:
    def __init__(self):
        self.cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
        self.dirty = False

    def _key(self, text: str) -> str:
        return hashlib.sha1(f"{EMBED_MODEL}\n{text}".encode()).hexdigest()

    def embed(self, texts: list[str]) -> np.ndarray:
        missing = [t for t in dict.fromkeys(texts) if self._key(t) not in self.cache]
        for i in range(0, len(missing), 64):
            batch = missing[i:i + 64]
            r = requests.post(f"{HOST}/api/embed", json={"model": EMBED_MODEL, "input": batch}, timeout=600)
            r.raise_for_status()
            for t, v in zip(batch, r.json()["embeddings"]):
                self.cache[self._key(t)] = v
            self.dirty = True
        m = np.array([self.cache[self._key(t)] for t in texts], dtype=np.float32)
        return m / np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-12)

    def save(self) -> None:
        if self.dirty:
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            tmp = CACHE.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.cache), encoding="utf-8")
            tmp.replace(CACHE)
            self.dirty = False


class Retriever:
    """Scores requests against one library (a list of skills with their condition metadata)."""

    def __init__(self, method: str, lib: list[dict], meta: dict, embedder: Embedder | None = None):
        self.method, self.lib = method, lib
        docs = [doc_text(*meta[s["key"]]) for s in lib]
        if method == "tfidf":
            self.tf = CharTfidf(docs)
            self.D = self.tf.vec(docs)
        elif method == "nomic":
            self.emb = embedder or Embedder()
            self.D = self.emb.embed(["search_document: " + d for d in docs])
        else:
            raise ValueError(method)

    def scores(self, texts: list[str]) -> np.ndarray:
        if self.method == "tfidf":
            Q = self.tf.vec(texts)
        else:
            Q = self.emb.embed(["search_query: " + t for t in texts])
        return Q @ self.D.T

    def top(self, text: str, k: int) -> list[dict]:
        s = self.scores([text])[0]
        order = sorted(range(len(self.lib)), key=lambda i: (-s[i], self.lib[i]["step"]))
        return [self.lib[i] for i in order[:k]]
