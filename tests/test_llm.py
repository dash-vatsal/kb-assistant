import pytest
from kb import config, llm, ollama


class _Resp:
    def __init__(self, data, status=200): self._d, self.status_code, self.text = data, status, "x"
    def json(self): return self._d
    def raise_for_status(self): pass


def test_embed_checks_dimension(monkeypatch):
    monkeypatch.setattr(ollama.requests, "post", lambda *a, **k: _Resp({"embeddings": [[0.1] * 768]}))
    with pytest.raises(RuntimeError, match="768"):
        ollama.embed("hi")


def test_embed_ok(monkeypatch):
    monkeypatch.setattr(ollama.requests, "post", lambda *a, **k: _Resp({"embeddings": [[0.1] * config.EMBED_DIM]}))
    assert len(ollama.embed("hi")) == config.EMBED_DIM


def test_generate_sends_context_size_and_json_mode(monkeypatch):
    seen = {}

    def fake(url, json=None, timeout=None):
        seen.update(url=url, **json)
        return _Resp({"message": {"content": "{}"}})
    monkeypatch.setattr(ollama.requests, "post", fake)
    assert ollama.generate("s", "u", json_mode=True) == "{}"
    assert seen["format"] == "json" and seen["options"]["num_ctx"] == config.OLLAMA_NUM_CTX and seen["stream"] is False


def test_connection_error_is_friendly(monkeypatch):
    def boom(*a, **k): raise ollama.requests.ConnectionError("down")
    monkeypatch.setattr(ollama.requests, "post", boom)
    with pytest.raises(RuntimeError, match="Is it running"):
        ollama.embed("hi")


def test_provider_switch(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "nope")
    with pytest.raises(ValueError):
        llm.embed("x")
