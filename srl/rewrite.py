"""Skill++ (arXiv:2611.00544, Sec. 3.2 and Appendix A) and the Body-distilled baseline, for any generator.

For every incoming skill c_t, in addition order, Skill++ sees only c_t and the records H_{t-1} of earlier skills
(original names, descriptions, bodies and synthetic queries); never evaluation queries, labels or routing results.

  g_t   = earlier skill whose original "name. description" is most similar to c_t's (Eq. 7)
  d_hat = generator(n_t, body_t[:1600], n_g, body_g[:1200]): <= 220 chars, only capabilities in body_t, lead with
          what g_t lacks, never name g_t. Regenerated up to 3 times; the original description is kept if none passes.
  G_t   = top 3 earlier skills by the fused rank of sigma1-3 (Eqs. 11-14); one exclusion phrase each, from the
          reference's name and the first 180 chars of its description; phrases containing a reference's name head
          are dropped, then phrases are dropped from the end until "d_hat Does not cover: p1; p2." fits 298 chars.
  name  = if the name of c_t contains the name head (first segment, > 3 chars) of an earlier original name, the
          generator proposes a qualified name from n_t, body_t[:1400] and n_g; kept if 4-60 chars (3 tries).
Body-distilled: description from the skill's own name and body only (<= 220 chars), original name kept.
Only incoming skills are rewritten; required skills keep their original metadata (as in the paper's main study).
Similarity uses character n-gram TF-IDF instead of MiniLM / Qwen3-Embedding.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

import numpy as np

from . import ollama
from .textsim import CharTfidf

DESC_MAX, LMAX, NAME_MIN, NAME_MAX = 220, 298, 4, 60
TRIES = 3

Q_SCHEMA = {"type": "object", "properties": {"queries": {"type": "array", "items": {"type": "string"},
                                                          "maxItems": 8}}, "required": ["queries"],
            "additionalProperties": False}
D_SCHEMA = {"type": "object", "properties": {"description": {"type": "string"}}, "required": ["description"],
            "additionalProperties": False}
E_SCHEMA = {"type": "object", "properties": {"phrases": {"type": "array", "items": {"type": "string"}}},
            "required": ["phrases"], "additionalProperties": False}
N_SCHEMA = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"],
            "additionalProperties": False}

P_QUERIES = """Below is the body of a skill that an AI assistant can load when a user's request needs it.

<skill_body>
{body}
</skill_body>

Write up to 8 different requests that a user might type during their work and that this skill would help with. \
Phrase them as the user would, one or two sentences each, in English. Do not mention the skill's name.
Return JSON: {{"queries": ["...", "..."]}}"""

P_DIFF = """You are improving the routing description of a NEW skill that is being added to a skill library. \
A router picks skills by reading only their names and short descriptions.

NEW skill name: {n_t}
NEW skill body (excerpt):
<new_body>
{b_t}
</new_body>

The most similar EXISTING skill in the library is shown only so that you can tell the two apart.
EXISTING skill name: {n_g}
EXISTING skill body (excerpt):
<existing_body>
{b_g}
</existing_body>

Write a description of the NEW skill, at most 220 characters, that:
- states only capabilities contained in the NEW skill's body;
- leads with what the NEW skill does that the EXISTING skill does not offer;
- never names or alludes to the EXISTING skill.
Return JSON: {{"description": "..."}}"""

P_EXCL = """Each numbered line below is a skill in a library (name: description). For each skill, write one short \
lowercase phrase (3 to 8 words) naming the work it is responsible for, so that it can be listed after \
"Does not cover". Do not use the skills' names.
Return JSON: {{"phrases": ["...", "..."]}} with exactly one phrase per skill, in the same order.

{lines}"""

P_NAME = """A NEW skill is being added to a skill library, and its name overlaps with the name of an existing skill.

NEW skill name: {n_t}
NEW skill body (excerpt):
<new_body>
{b_t}
</new_body>

EXISTING skill name: {n_g}

Propose a more specific name for the NEW skill that adds a qualifier taken from its body, such as its market, \
data source, subtopic or type of guidance. Use lowercase words joined by hyphens.
Return JSON: {{"name": "..."}}"""

P_BODY = """Below is a skill that an AI assistant can load. A router picks skills by reading only their names and \
short descriptions.

Skill name: {n_t}
Skill body (excerpt):
<body>
{b_t}
</body>

Write a description of this skill, at most 220 characters, that states what it does, based only on its body.
Return JSON: {{"description": "..."}}"""

PROMPTS_DIGEST = hashlib.sha256("\n".join([P_QUERIES, P_DIFF, P_EXCL, P_NAME, P_BODY]).encode()).hexdigest()[:16]


# ---------------------------------------------------------------- generators
class LocalGen:
    """An Ollama model. First attempt at temperature 0; retries at 0.7 with a new seed."""

    def __init__(self, model: str, num_ctx: int = 4096):
        self.model, self.num_ctx, self.tag = model, num_ctx, model.replace(":", "_")

    def json(self, prompt: str, schema: dict, max_tokens: int, attempt: int) -> tuple[dict | None, dict]:
        r = ollama.chat(self.model, prompt, schema, self.num_ctx, max_tokens,
                        temperature=0.0 if attempt == 0 else 0.7, seed=attempt)
        log = {"model": self.model, "prompt_tokens": r["prompt_tokens"], "output_tokens": r["output_tokens"],
               "seconds": r["seconds"]}
        return ollama.parse_json(r["content"]), log


class ClaudeGen:
    """Claude Haiku 5.5 with structured outputs (default sampling)."""

    def __init__(self, model: str, budget):
        from .claude import ClaudeJSON
        self.model, self.tag = model, "haiku"
        self.api = ClaudeJSON(model, budget)

    def json(self, prompt: str, schema: dict, max_tokens: int, attempt: int) -> tuple[dict | None, dict]:
        r = self.api.call(prompt, schema, max_tokens)
        log = {"model": r["model"], "usage": r["usage"], "seconds": r["seconds"]}
        return ollama.parse_json(r["content"]), log


# ---------------------------------------------------------------- helpers
def name_head(name: str) -> str | None:
    seg = re.split(r"[\s\-—]+", name.strip().lower())[0] if name.strip() else ""
    return seg if len(seg) > 3 else None


def name_conflict(n_t: str, earlier_names: list[str]) -> bool:
    low = n_t.lower()
    return any((h := name_head(n)) is not None and h in low for n in earlier_names)


def u_text(name: str, desc: str) -> str:
    return f"{name}. {desc[:300]}"


def fused_top(s1: np.ndarray, s2: np.ndarray, s3: np.ndarray, k: int = 3) -> list[int]:
    """Indices (in addition order) of the top-k candidates by (min rank, sum of ranks), ties by addition order."""
    ranks = []
    for s in (s1, s2, s3):
        order = sorted(range(len(s)), key=lambda i: (-s[i], i))
        r = np.empty(len(s), dtype=int)
        for pos, i in enumerate(order):
            r[i] = pos + 1
        ranks.append(r)
    keyf = [(min(r[i] for r in ranks), sum(r[i] for r in ranks), i) for i in range(len(s1))]
    return [t[2] for t in sorted(keyf)[:k]]


def assemble(d_hat: str, phrases: list[str], lmax: int = LMAX) -> tuple[str, list[str]]:
    p = list(phrases)
    while p:
        text = f"{d_hat} Does not cover: {'; '.join(p)}."
        if len(text) <= lmax:
            return text, p
        p.pop()
    return d_hat, p


def _clean_phrase(p: str) -> str:
    return re.sub(r"\s+", " ", p.strip().strip(".;:").lower())


# ---------------------------------------------------------------- pipeline
class Rewriter:
    def __init__(self, gen, skills: list[dict], out: Path):
        self.gen, self.skills, self.out = gen, sorted(skills, key=lambda s: s["step"]), out
        self.state = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {
            "generator": getattr(gen, "model", "?"), "prompts_digest": PROMPTS_DIGEST, "synthetic": {}, "skills": {},
            "calls": []}
        assert self.state["prompts_digest"] == PROMPTS_DIGEST, "prompts changed since this file was written"

    def save(self) -> None:
        self.out.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.out.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(self.out)

    def _call(self, what: str, key: str, prompt: str, schema: dict, max_tokens: int, ok) -> tuple[object, int]:
        """Up to TRIES attempts; returns (value, attempts) with value None when no attempt passed `ok`."""
        for a in range(TRIES):
            val, log = self.gen.json(prompt, schema, max_tokens, a)
            res = ok(val) if val is not None else None
            self.state["calls"].append(dict(log, what=what, key=key, attempt=a, passed=res is not None))
            if res is not None:
                return res, a + 1
        return None, TRIES

    # synthetic queries for every skill (the records' Q~_s)
    def synth_all(self) -> None:
        for s in self.skills:
            if s["key"] in self.state["synthetic"]:
                continue
            def ok(v):
                q = [x.strip() for x in v.get("queries", []) if isinstance(x, str) and x.strip()][:8]
                return q or None
            q, _ = self._call("queries", s["key"], P_QUERIES.format(body=s["body"][:2600]), Q_SCHEMA, 700, ok)
            self.state["synthetic"][s["key"]] = q or []
            self.save()

    def refine_all(self, body_distilled: bool = True) -> None:
        syn = self.state["synthetic"]
        assert all(s["key"] in syn for s in self.skills), "run synth_all first"
        corpus = [u_text(s["name"], s["desc"]) for s in self.skills] + [s["body"] for s in self.skills] + \
            [q for s in self.skills for q in syn[s["key"]]]
        tf = CharTfidf(corpus)
        U = tf.vec([u_text(s["name"], s["desc"]) for s in self.skills])
        QV = {s["key"]: tf.vec(syn[s["key"]]) if syn[s["key"]] else np.zeros((0, U.shape[1]), np.float32)
              for s in self.skills}
        for t, c in enumerate(self.skills):
            if c["kind"] == "required" or (c["key"] in self.state["skills"]
                                           and ("bd_desc" in self.state["skills"][c["key"]] or not body_distilled)):
                continue
            rec = self.state["skills"].get(c["key"], {})
            earlier = self.skills[:t]
            if "d_hat" not in rec:
                rec.update(self._refine_one(c, earlier, U[:t], U[t], QV))
                self.state["skills"][c["key"]] = rec
                self.save()
            if body_distilled and "bd_desc" not in rec:
                prompt = P_BODY.format(n_t=c["name"], b_t=c["body"][:1600])
                d, tries = self._call("body_distilled", c["key"], prompt, D_SCHEMA, 200,
                                      lambda v: _desc_ok(v.get("description"), None, c["name"]))
                rec["bd_desc"], rec["bd_tries"], rec["bd_fallback"] = d or c["desc"], tries, d is None
                self.state["skills"][c["key"]] = rec
                self.save()

    def _refine_one(self, c: dict, earlier: list[dict], U_e: np.ndarray, u_t: np.ndarray, QV: dict) -> dict:
        sims = U_e @ u_t
        g = earlier[int(np.argmax(sims))]
        # description differentiation
        prompt = P_DIFF.format(n_t=c["name"], b_t=c["body"][:1600], n_g=g["name"], b_g=g["body"][:1200])
        d_hat, d_tries = self._call("differentiate", c["key"], prompt, D_SCHEMA, 200,
                                    lambda v: _desc_ok(v.get("description"), g["name"], c["name"]))
        # reference set for exclusions (sigma1: incoming metadata vs earlier synthetic queries; sigma2: synthetic
        # queries vs synthetic queries; sigma3: metadata vs metadata)
        qt = QV[c["key"]]
        s1 = np.array([float((QV[e["key"]] @ u_t).max()) if len(QV[e["key"]]) else 0.0 for e in earlier])
        s2 = np.array([float((QV[e["key"]] @ qt.T).max()) if len(QV[e["key"]]) and len(qt) else 0.0
                       for e in earlier])
        s3 = sims
        G = [earlier[i] for i in fused_top(s1, s2, s3, 3)]
        lines = "\n".join(f"{i + 1}. {r['name']}: {r['desc'][:180]}" for i, r in enumerate(G))
        def ok_e(v):
            p = [_clean_phrase(x) for x in v.get("phrases", []) if isinstance(x, str) and x.strip()]
            return p if len(p) == len(G) else None
        phrases, e_tries = self._call("exclusions", c["key"], P_EXCL.format(lines=lines), E_SCHEMA, 200, ok_e)
        phrases = phrases or []
        heads = [h for h in (name_head(r["name"]) for r in G) if h]
        kept = [p for p in phrases if not any(h in p for h in heads)]
        # name clarification
        conflict = name_conflict(c["name"], [e["name"] for e in earlier])
        new_name, n_tries = None, 0
        if conflict:
            prompt = P_NAME.format(n_t=c["name"], b_t=c["body"][:1400], n_g=g["name"])
            new_name, n_tries = self._call("name", c["key"], prompt, N_SCHEMA, 60, lambda v: _name_ok(v.get("name")))
        d_final = d_hat or c["desc"]
        assembled, used = assemble(d_final, kept)
        return {"g": g["key"], "G": [r["key"] for r in G], "d_hat": d_final, "d_tries": d_tries,
                "d_fallback": d_hat is None, "phrases_raw": phrases, "phrases_kept": kept, "phrases_used": used,
                "e_tries": e_tries, "assembled": assembled, "name_conflict": conflict,
                "name": new_name or c["name"], "n_tries": n_tries, "name_fallback": conflict and new_name is None}


def _desc_ok(d, ref_name: str | None, own_name: str):
    if not isinstance(d, str):
        return None
    d = re.sub(r"\s+", " ", d).strip()
    if not d or len(d) > DESC_MAX:
        return None
    if ref_name and ref_name.lower() != own_name.lower() and ref_name.lower() in d.lower():
        return None
    return d


def _name_ok(n):
    if not isinstance(n, str):
        return None
    n = n.strip().strip('"').strip()
    return n if NAME_MIN <= len(n) <= NAME_MAX else None


def run(gen, skills: list[dict], out: Path, body_distilled: bool = True) -> dict:
    t = time.time()
    rw = Rewriter(gen, skills, out)
    rw.synth_all()
    rw.refine_all(body_distilled=body_distilled)
    rw.state["seconds_total"] = rw.state.get("seconds_total", 0) + round(time.time() - t, 1)
    rw.save()
    return rw.state
