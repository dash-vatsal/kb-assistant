"""Unit tests for the answer gates. No database or Bedrock: everything external is mocked."""
import json
from datetime import datetime, timezone
import pytest
from kb import answer as A


def _hit(i, sim=0.8, ts=datetime(2026, 11, 1, tzinfo=timezone.utc)):
    return {"chunk_id": i, "doc_id": f"d{i}", "title": f"Doc {i}", "url": f"https://x/{i}", "last_updated": ts,
            "heading_path": "H", "text": f"text {i}", "sim": sim, "rrf": 0.1}


@pytest.fixture
def wire(monkeypatch):
    state = {"hits": [_hit(1), _hit(2)], "model": json.dumps({"found": True, "answer": "Yes [1]", "citations": [1]})}
    monkeypatch.setattr(A, "user_groups", lambda conn, uid: ["all-staff"])
    monkeypatch.setattr(A, "hybrid_search", lambda conn, q, g: state["hits"])
    monkeypatch.setattr(A, "rerank", lambda q, h, n: h)
    monkeypatch.setattr(A, "generate", lambda system, user, **kw: state["model"])
    monkeypatch.setattr(A, "log_query", lambda *a, **k: 1)
    return state


def test_happy_path_returns_valid_citation(wire):
    r = A.answer_question(None, "q", "u")
    assert r["found"] and [c["n"] for c in r["citations"]] == [1]


def test_no_hits_is_not_found(wire):
    wire["hits"] = []
    assert not A.answer_question(None, "q", "u")["found"]


def test_low_similarity_is_not_found(wire):
    wire["hits"] = [_hit(1, sim=0.05)]
    r = A.answer_question(None, "q", "u")
    assert not r["found"] and r["_note"] == "below_similarity_threshold"


def test_answer_without_valid_citation_is_not_found(wire):
    wire["model"] = json.dumps({"found": True, "answer": "Yes [9]", "citations": [9]})
    assert not A.answer_question(None, "q", "u")["found"]


def test_model_says_not_found(wire):
    wire["model"] = json.dumps({"found": False, "answer": "", "citations": []})
    assert not A.answer_question(None, "q", "u")["found"]


def test_garbage_model_output_is_not_found(wire):
    wire["model"] = "I think the answer is..."
    r = A.answer_question(None, "q", "u")
    assert not r["found"] and r["_note"] == "unparseable_model_output"


def test_old_source_flagged(wire):
    wire["hits"] = [_hit(1, ts=datetime(2020, 1, 1, tzinfo=timezone.utc))]
    assert A.answer_question(None, "q", "u")["citations"][0]["possibly_outdated"]
