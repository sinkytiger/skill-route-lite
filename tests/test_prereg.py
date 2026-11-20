"""Frozen before the first test-split run: data, rewrites, prompts and decision constants. A change to any of them
after pre-registration makes this file fail."""

import hashlib
import json
from pathlib import Path

from srl import build as B
from srl import prereg as P
from srl import rewrite as W
from srl import route as R

ROOT = Path(__file__).resolve().parent.parent

FROZEN = {
    "skills.json": "22037c69c3259deb",
    "queries.json": "975d4f85668489e4",
    "probes.json": "29a5d7d8db045add",
}
REWRITE_DIGESTS = {
    "haiku": "5d8f2b03e046c80c",
    "qwen3_4b": "e70e3da1314bb9d1",
}


def _file_digest(path: Path) -> str:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if "skills" in obj and "synthetic" in obj:          # rewrites: freeze the outputs, not the call log
        obj = {"synthetic": obj["synthetic"], "skills": obj["skills"], "prompts_digest": obj["prompts_digest"]}
    return B.digest(obj)


def test_data_digests():
    for name, want in FROZEN.items():
        assert B.digest(B.load(name)) == want, name


def test_rewrite_digests():
    for tag, want in REWRITE_DIGESTS.items():
        assert _file_digest(ROOT / "data" / "rewrites" / f"{tag}.json") == want, tag


def test_prompts_and_rules():
    assert W.PROMPTS_DIGEST == "24f4532c87185c1d"
    assert R.PROMPT_DIGEST == "9bc1461c55253de1"
    assert R.NUM_CTX == {"qwen3:4b": 10240, "llama3.2:3b": 10240}
    assert (P.H1_DROP, P.H2_SHARE, P.H3_SHARE, P.JUDGE_MIN) == (0.15, 0.5, 0.5, 0.05)
