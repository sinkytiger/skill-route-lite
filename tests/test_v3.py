"""v3: fresh test3 phrasings and the retrieval-source label."""

from srl.catalog_required import REQUIRED
from srl.catalog_v2 import PHRASES_TEST2
from srl.catalog_v3 import PHRASES_TEST3
from srl.route import parse_label, retrieval_source
from srl.textsim import CharTfidf


def test_phrases_v3_new_and_distinct():
    keys = {r["key"] for r in REQUIRED}
    assert set(PHRASES_TEST3) == keys and all(len(v) == 4 for v in PHRASES_TEST3.values())
    old = [p for r in REQUIRED for p in r["phrases_test"] + r["phrases_dev"] + PHRASES_TEST2[r["key"]]]
    new = [p for v in PHRASES_TEST3.values() for p in v]
    assert len(set(new)) == len(new) == 160
    assert not set(new) & set(old)
    tf = CharTfidf(old + new)
    assert float((tf.vec(new) @ tf.vec(old).T).max()) < 0.75


def test_phrases_v3_render_cleanly():
    for v in PHRASES_TEST3.values():
        for p in v:
            first = p.split(" ", 1)[0]
            assert len(first) > 1 or first == "I", p      # a one-letter first word is not lower-cased when joined


def test_retrieval_source_labels():
    assert parse_label("spp_haiku+r30tfidf@vanilla") == ("spp_haiku", 30, "tfidf")
    assert parse_label("spp_qwen3_4b+r30tfidf@vanilla") == ("spp_qwen3_4b", 30, "tfidf")
    assert retrieval_source("spp_haiku+r30tfidf@vanilla") == "vanilla"
    assert retrieval_source("spp_haiku+r30tfidf") is None
