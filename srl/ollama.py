"""Local models through the Ollama chat API (JSON-schema constrained output, thinking off for qwen3)."""

from __future__ import annotations

import json
import os
import time

import requests

HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def chat(model: str, prompt: str, schema: dict, num_ctx: int, num_predict: int, temperature: float = 0.0,
         seed: int = 0) -> dict:
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False, "format": schema,
            "options": {"temperature": temperature, "seed": seed, "num_ctx": num_ctx, "num_predict": num_predict}}
    if model.startswith("qwen3"):
        body["think"] = False
    last = None
    for attempt in range(6):
        try:
            t = time.time()
            r = requests.post(f"{HOST}/api/chat", json=body, timeout=900)
            r.raise_for_status()
            d = r.json()
            return {"content": d["message"]["content"], "prompt_tokens": d.get("prompt_eval_count", 0),
                    "output_tokens": d.get("eval_count", 0), "seconds": round(time.time() - t, 2),
                    "done_reason": d.get("done_reason")}
        except Exception as exc:  # noqa: BLE001 - connection resets, server restarts
            last = exc
            time.sleep(10 * 2 ** min(attempt, 4))
    raise RuntimeError(f"{model}: {last}")


def parse_json(text: str) -> dict | None:
    try:
        v = json.loads(text)
        return v if isinstance(v, dict) else None
    except ValueError:
        return None
