"""Frozen before the first test3 run (docs/hypotheses_v3.md): v3 queries, the retrieval-source rule, the decision code
and the v3 tables."""

import hashlib
import inspect

from srl import build as B
from srl import prereg_v3 as P3
from srl import report_v3 as RV3
from srl import route as R


def _h(obj) -> str:
    return hashlib.sha256(inspect.getsource(obj).encode()).hexdigest()[:16]


def test_v3_data_digest():
    assert B.digest(B.load("queries_v3.json")) == "9f0125629666dfb0"


def test_v3_code_and_settings():
    assert _h(R.retrieval_source) == "9e06a27ba22fed46"
    assert R.PROMPT_DIGEST == "9bc1461c55253de1"
    assert _h(P3) == "3a999d77937c05b6"
    assert _h(RV3) == "2441797d89b787b0"
    assert (P3.R1_DROP, P3.N1_GAIN, P3.ALPHA) == (0.15, 0.10, 0.05)
    assert RV3.RETR == ["vanilla+r30tfidf", "spp_haiku+r30tfidf", "spp_haiku+r30tfidf@vanilla",
                        "spp_noexcl_haiku_short+r30tfidf@vanilla"]
