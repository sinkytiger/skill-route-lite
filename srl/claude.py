"""Claude Haiku 5.5 through the official SDK, with one spending cap shared by every paid call.

Prices are $ per million tokens (Claude API pricing, as used in fin-formulate-lite and order-gate-lite): Haiku 5.5
$0.10 in / $0.50 out for prompts up to 100,000 tokens, cache reads 0.1x and 5-minute cache writes 1.25x the input
price. Every request is refused once the spend recorded in the saved files (data/rewrites and runs, archived ones
included) plus this process's spend reaches BUDGET. The API key is read at run time and never stored or printed.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

PRICES = {"claude-haiku-5-5": (0.10, 0.50)}
BUDGET = float(os.environ.get("SRL_BUDGET", "3.0"))   # dollars; the cap proposed to the user


class BudgetExceeded(RuntimeError):
    pass


def cost_of(model: str, u: dict) -> float:
    if model not in PRICES:
        return 0.0
    pin, pout = PRICES[model]
    return (u.get("input_tokens", 0) * pin + u.get("cache_creation_input_tokens", 0) * pin * 1.25
            + u.get("cache_read_input_tokens", 0) * pin * 0.1 + u.get("output_tokens", 0) * pout) / 1e6


def _walk(o, model: str, acc: list) -> None:
    """Every 'usage' dict in a saved record, priced with the nearest enclosing 'model'."""
    if isinstance(o, dict):
        if isinstance(o.get("model"), str):
            model = o["model"]
        if isinstance(o.get("usage"), dict):
            acc.append(cost_of(model, o["usage"]))
        for k, v in o.items():
            if k != "usage":
                _walk(v, model, acc)
    elif isinstance(o, list):
        for v in o:
            _walk(v, model, acc)


def spent(roots: list[Path]) -> float:
    acc: list = []
    for root in roots:
        if not root.exists():
            continue
        for f in root.rglob("*.json"):
            try:
                _walk(json.loads(f.read_text(encoding="utf-8")), "", acc)
            except (OSError, ValueError):
                continue
    return sum(acc)


class Budget:
    def __init__(self, roots: list[Path]):
        self.base, self.session = spent(roots), 0.0

    def check(self) -> None:
        if self.base + self.session >= BUDGET:
            raise BudgetExceeded(f"spend ${self.base + self.session:.4f} reached the ${BUDGET} budget")

    def charge(self, model: str, u: dict) -> None:
        self.session += cost_of(model, u)


def make_client():
    import anthropic
    key = os.environ.get("ANTHROPIC_API_KEY") or \
        (Path.home() / ".harnessforge" / "anthropic_api_key.txt").read_text(encoding="utf-8").strip()
    return anthropic.Anthropic(api_key=key, max_retries=4, timeout=120)


def usage_of(r) -> dict:
    return {"input_tokens": r.usage.input_tokens or 0, "output_tokens": r.usage.output_tokens or 0,
            "cache_creation_input_tokens": r.usage.cache_creation_input_tokens or 0,
            "cache_read_input_tokens": r.usage.cache_read_input_tokens or 0}


UNSUPPORTED = ("minItems", "maxItems", "minLength", "maxLength", "minimum", "maximum", "uniqueItems")


def api_schema(s):
    """Structured outputs reject array/string/number constraints; drop them (lengths are enforced in code)."""
    if isinstance(s, dict):
        return {k: api_schema(v) for k, v in s.items() if k not in UNSUPPORTED}
    if isinstance(s, list):
        return [api_schema(v) for v in s]
    return s


class ClaudeJSON:
    """One structured-output call: the reply is constrained to the given JSON schema. Thinking off, default
    sampling. `cache_prefix`, when given, is sent as a separate first content block with cache_control so that a
    long shared prefix (the skill list of the router) is cached."""

    def __init__(self, model: str, budget: Budget, client=None):
        self.model, self.budget = model, budget
        self.client = client or make_client()

    def call(self, prompt: str, schema: dict, max_tokens: int, cache_prefix: str | None = None) -> dict:
        self.budget.check()
        t = time.time()
        if cache_prefix is None:
            content = prompt
        else:
            content = [{"type": "text", "text": cache_prefix, "cache_control": {"type": "ephemeral"}},
                       {"type": "text", "text": prompt}]
        r = self.client.messages.create(model=self.model, max_tokens=max_tokens, thinking={"type": "disabled"},
                                        output_config={"format": {"type": "json_schema",
                                                                  "schema": api_schema(schema)}},
                                        messages=[{"role": "user", "content": content}])
        u = usage_of(r)
        self.budget.charge(self.model, u)
        text = "".join(b.text for b in r.content if b.type == "text").strip()
        return {"content": text, "model": self.model, "usage": u, "seconds": round(time.time() - t, 2),
                "stop_reason": r.stop_reason}
