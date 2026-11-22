"""Frozen before the first test2 run (docs/hypotheses_v2.md): v2 queries, length-controlled rewrites, retrieval code,
settings and decision constants."""

import hashlib
import inspect
import json
from pathlib import Path

from srl import build as B
from srl import prereg_v2 as P2
from srl import report_v2 as RV
from srl import retrieve as RT
from srl import rewrite_v2 as W2
from srl import route as R

ROOT = Path(__file__).resolve().parent.parent


def test_v2_data_digests():
    assert B.digest(B.load("queries_v2.json")) == "72de4367827c98eb"
    d = json.loads((ROOT / "data" / "rewrites" / "haiku_short.json").read_text(encoding="utf-8"))
    assert B.digest({"skills": d["skills"]}) == "ec27d59966d28b2b"


def test_v2_code_and_settings():
    assert hashlib.sha256(inspect.getsource(RT).encode()).hexdigest()[:16] == "f6de4b662f51f2d9"
    assert hashlib.sha256(W2.P_DIFF_SHORT.encode()).hexdigest()[:16] == "04c01015d20ee47c"
    assert R.PROMPT_DIGEST == "9bc1461c55253de1"
    assert (RV.K, RV.RET) == (30, "+r30tfidf")
    assert (W2.DESC_ASK, W2.DESC_MAX_SHORT, W2.LMAX_SHORT) == (110, 130, 160)
    assert (P2.R1_DROP, P2.V1_MAX_GAIN, P2.V2_GAIN, P2.V4_SHARE) == (0.15, 0.05, 0.10, 0.5)
