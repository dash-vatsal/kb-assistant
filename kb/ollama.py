"""Local models through Ollama (https://ollama.com). Nothing leaves the machine."""
import requests
from kb import config


def _post(path: str, payload: dict, timeout: int = 600) -> dict:
    try:
        r = requests.post(f"{config.OLLAMA_BASE_URL}{path}", json=payload, timeout=timeout)
    except requests.ConnectionError as e:
        raise RuntimeError(f"Cannot reach Ollama at {config.OLLAMA_BASE_URL}. Is it running? ({e})") from e
    if r.status_code == 404:
        raise RuntimeError(f"Ollama says model not found: {r.text[:200]}. Run `make models`.")
    r.raise_for_status()
    return r.json()


def embed(text: str) -> list[float]:
    data = _post("/api/embed", {"model": config.OLLAMA_EMBED_MODEL, "input": text[:12000]})
    vec = data["embeddings"][0]
    if len(vec) != config.EMBED_DIM:
        raise RuntimeError(f"Embedding model returned {len(vec)} dims but the schema expects {config.EMBED_DIM}. "
                           "Use bge-m3, or change EMBED_DIM and sql/schema.sql and re-index.")
    return vec


def generate(system: str, user: str, role: str = "answer", max_tokens: int = 1024,
             temperature: float = 0.0, json_mode: bool = False) -> str:
    model = config.OLLAMA_RERANK_MODEL if role == "rerank" else config.OLLAMA_CHAT_MODEL
    payload = {
        "model": model, "stream": False,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "options": {"temperature": temperature, "num_ctx": config.OLLAMA_NUM_CTX, "num_predict": max_tokens},
    }
    if json_mode:
        payload["format"] = "json"
    return _post("/api/chat", payload)["message"]["content"]
