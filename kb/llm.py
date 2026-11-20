"""Provider switch: LLM_PROVIDER=ollama (local, default) or bedrock. The rest of the code only imports from here."""
from kb import config


def _impl():
    if config.LLM_PROVIDER == "ollama":
        from kb import ollama
        return ollama
    if config.LLM_PROVIDER == "bedrock":
        from kb import bedrock
        return bedrock
    raise ValueError(f"Unknown LLM_PROVIDER={config.LLM_PROVIDER!r} (use 'ollama' or 'bedrock')")


def embed(text: str) -> list[float]:
    return _impl().embed(text)


def generate(system: str, user: str, role: str = "answer", max_tokens: int = 1024,
             temperature: float = 0.0, json_mode: bool = False) -> str:
    """role: 'answer' | 'rerank' | 'judge'. json_mode asks the model for strict JSON where supported."""
    impl = _impl()
    if config.LLM_PROVIDER == "bedrock":
        model = config.RERANK_MODEL_ID if role == "rerank" else config.ANSWER_MODEL_ID
        return impl.generate(system, user, model_id=model, max_tokens=max_tokens, temperature=temperature)
    return impl.generate(system, user, role=role, max_tokens=max_tokens, temperature=temperature, json_mode=json_mode)
