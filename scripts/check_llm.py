"""Smoke test for the model layer.   python scripts/check_llm.py"""
import json
import time
from kb import config
from kb.llm import embed, generate

print(f"provider={config.LLM_PROVIDER}  embed={config.OLLAMA_EMBED_MODEL if config.LLM_PROVIDER == 'ollama' else config.EMBED_MODEL_ID}")
t = time.time()
v = embed("What is our code review process?")
print(f"embedding ok: {len(v)} dims in {time.time() - t:.1f}s (expected {config.EMBED_DIM})")
t = time.time()
out = generate("Reply with JSON only.", 'Return {"ok": true}', json_mode=True, max_tokens=50)
print(f"generate ok in {time.time() - t:.1f}s: {out.strip()[:80]}")
json.loads(out)
print("JSON mode ok. Model layer is ready.")
