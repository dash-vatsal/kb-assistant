"""API tests with the database and answer layer mocked."""
from contextlib import contextmanager
import pytest
from fastapi.testclient import TestClient
from kb import api, config


class _Cur:
    def __init__(self, row): self.row = row
    def fetchone(self): return self.row
    def fetchall(self): return [self.row] if self.row else []


class FakeConn:
    def __init__(self, user_exists=True): self.user_exists = user_exists
    def execute(self, *a, **k): return _Cur((1,) if self.user_exists else None)
    def __enter__(self): return self
    def __exit__(self, *a): return False


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(api, "connect", lambda: FakeConn())
    monkeypatch.setattr(api, "answer_question",
                        lambda conn, q, u: {"query_id": 1, "found": False, "answer": "x", "citations": [], "_hits": []})
    api.limiter._hits.clear()
    return TestClient(api.app)


H = {"X-Api-Key": config.API_KEY, "X-User-Id": "alice_a"}


def test_bad_key_rejected(client):
    assert client.post("/ask", json={"question": "hi"}, headers={**H, "X-Api-Key": "nope"}).status_code == 401


def test_unknown_user_rejected(client, monkeypatch):
    monkeypatch.setattr(api, "connect", lambda: FakeConn(user_exists=False))
    assert client.post("/ask", json={"question": "hi"}, headers=H).status_code == 403


def test_internal_fields_hidden(client):
    body = client.post("/ask", json={"question": "hi"}, headers=H).json()
    assert "_hits" not in body and body["found"] is False


def test_rate_limit(client):
    codes = [client.post("/ask", json={"question": "hi"}, headers=H).status_code for _ in range(22)]
    assert codes[:20] == [200] * 20 and codes[20] == 429


def test_feedback_rating_validated(client):
    assert client.post("/feedback", json={"query_id": 1, "rating": 5}, headers=H).status_code == 422
