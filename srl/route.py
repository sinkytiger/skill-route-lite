"""The router: one call that reads every installed skill's ID, name and description and returns 5 skill IDs.

The paper's routing harness uses two calls (shortlist 10, then rerank) with Claude Haiku 4.5; here one call returns
the final 5, most useful first. The skill list comes first and the request last, so consecutive requests at the same
checkpoint and condition share a prompt prefix (Ollama reuses its cache; Claude uses prompt caching). Display order
is shuffled once per checkpoint and order seed, and is the same in every condition.
Local routers decode under a JSON schema whose items are restricted to the installed IDs (temperature 0, seed 0).
"""

from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path

from . import ollama
from .conditions import DISPLAY_CHARS, metadata

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs" / "route"
K = 5
NUM_CTX = {"qwen3:4b": 10240, "llama3.2:3b": 10240}

HEAD = """You are the skill router of an AI assistant for financial analysis. For each request the assistant can \
load at most five skills. Below are all installed skills, one per line: ID | name | description.

<skills>
{lines}
</skills>

Read the request at the end and choose the 5 skills the assistant should load for it, most useful first. A request \
may need one, two or three of these skills; fill the remaining places with the next most useful ones. Use only IDs \
from the list.

<request>
"""
TAIL = """{request}
</request>

Answer in JSON: {{"skills": ["ID", "ID", "ID", "ID", "ID"]}}"""
PROMPT_DIGEST = hashlib.sha256((HEAD + TAIL).encode()).hexdigest()[:16]


def tag(router: str) -> str:
    return router.replace(":", "_")


def library(skills: list[dict], checkpoint: int) -> list[dict]:
    return [s for s in sorted(skills, key=lambda s: s["step"]) if s["session"] <= checkpoint]


def display_order(lib: list[dict], checkpoint: int, order_seed: int) -> list[dict]:
    lib = list(lib)
    random.Random(f"order-{order_seed}-S{checkpoint}").shuffle(lib)
    return lib


def head_text(lib_ordered: list[dict], meta: dict) -> str:
    lines = []
    for s in lib_ordered:
        name, desc = meta[s["key"]]
        lines.append(f"{s['id']} | {name} | {desc[:DISPLAY_CHARS]}")
    return HEAD.format(lines="\n".join(lines))


def schema_for(ids: list[str], exact: bool = True) -> dict:
    arr = {"type": "array", "items": {"type": "string", "enum": ids}}
    if exact:
        arr.update(minItems=K, maxItems=K)
    return {"type": "object", "properties": {"skills": arr}, "required": ["skills"], "additionalProperties": False}


def parse_selection(content: str, ids: set[str]) -> tuple[list[str], bool]:
    v = ollama.parse_json(content)
    raw = v.get("skills") if v else None
    if not isinstance(raw, list):
        return [], False
    out = []
    for x in raw:
        if isinstance(x, str) and x.strip() in ids and x.strip() not in out:
            out.append(x.strip())
    return out[:K], True


def block_path(router: str, cond: str, split: str, checkpoint: int, order_seed: int) -> Path:
    return RUNS / tag(router) / cond / split / f"S{checkpoint}_o{order_seed}.json"


def retrieval_label(cond: str, k: int, method: str) -> str:
    return f"{cond}+r{k}{method}"


def parse_label(label: str) -> tuple[str, int | None, str | None]:
    """'spp_haiku+r20tfidf' -> ('spp_haiku', 20, 'tfidf'); a plain condition -> (cond, None, None).
    A v3 retrieval source ('spp_haiku+r30tfidf@vanilla') is ignored here; see retrieval_source()."""
    label = label.split("@", 1)[0]
    if "+r" not in label:
        return label, None, None
    cond, rest = label.split("+r", 1)
    k = int("".join(ch for ch in rest if ch.isdigit()))
    return cond, k, rest[len(str(k)):]


def retrieval_source(label: str) -> str | None:
    """v3: the condition whose metadata the retriever reads. 'spp_haiku+r30tfidf@vanilla' retrieves on the original
    metadata and shows the router the Skill++ metadata; without '@' (v2) the retriever reads what the router reads."""
    return label.split("@", 1)[1] if "@" in label else None


def run_block(router: str, cond: str, split: str, checkpoint: int, order_seed: int, skills: list[dict],
              items: list[dict], rw_cache: dict, claude=None) -> Path:
    """items: [{'iid', 'text'}]. Resumes from the saved block file. `cond` may carry a retrieval suffix
    ('vanilla+r20tfidf'): then each request sees only its top-K skills, shuffled per request (v2)."""
    path = block_path(router, cond, split, checkpoint, order_seed)
    base, k, method = parse_label(cond)
    lib = display_order(library(skills, checkpoint), checkpoint, order_seed)
    meta = metadata(base, skills, rw_cache)
    head = head_text(lib, meta)
    head_digest = hashlib.sha256(head.encode()).hexdigest()[:16]
    ids = [s["id"] for s in lib]
    idset = set(ids)
    retriever = None
    if k is not None:
        from .retrieve import Retriever
        src = retrieval_source(cond)
        rmeta = metadata(src, skills, rw_cache) if src else meta
        retriever = Retriever(method, library(skills, checkpoint), rmeta)
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "router": router, "cond": cond, "split": split, "checkpoint": checkpoint, "order_seed": order_seed,
        "prompt_digest": PROMPT_DIGEST, "head_digest": head_digest, "library_size": len(lib), "items": {}}
    assert state["head_digest"] == head_digest, f"{path}: the skill list changed since this block was started"
    todo = [it for it in items if it["iid"] not in state["items"]]
    if not todo:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)

    def save():
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(path)

    for n, it in enumerate(todo):
        tail = TAIL.format(request=it["text"])
        item_head, item_ids, item_idset, cands = head, ids, idset, None
        if retriever is not None:
            cands = retriever.top(it["text"], k)
            random.Random(f"cand-{order_seed}-S{checkpoint}-{it['iid']}").shuffle(cands)
            item_head = head_text(cands, meta)
            item_ids = [s["id"] for s in cands]
            item_idset = set(item_ids)
        t = time.time()
        if router.startswith("claude"):
            r = claude.call(tail, schema_for(item_ids, exact=False), max_tokens=120, cache_prefix=item_head)
            rec = {"content": r["content"], "model": r["model"], "usage": r["usage"], "seconds": r["seconds"]}
        else:
            nctx = NUM_CTX[router]
            r = ollama.chat(router, item_head + tail, schema_for(item_ids), num_ctx=nctx, num_predict=120)
            if r["prompt_tokens"] >= nctx - 16:
                raise RuntimeError(f"prompt of {r['prompt_tokens']} tokens may have been truncated (num_ctx {nctx})")
            rec = {"content": r["content"], "prompt_tokens": r["prompt_tokens"], "output_tokens": r["output_tokens"],
                   "seconds": r["seconds"]}
        sel, ok = parse_selection(rec["content"], item_idset)
        rec.update(selected=sel, parsed=ok)
        if cands is not None:
            rec["candidates"] = item_ids
        state["items"][it["iid"]] = rec
        if n % 5 == 4 or n == len(todo) - 1:
            save()
    return path
