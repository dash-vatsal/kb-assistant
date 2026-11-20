import os
from dotenv import load_dotenv

load_dotenv()


def _b(name, default):
    return os.getenv(name, default).lower() in ("1", "true", "yes")


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kb:kb@localhost:5432/kb")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")          # ollama (local) | bedrock
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "bge-m3")   # 1024 dimensions
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:7b-instruct")
OLLAMA_RERANK_MODEL = os.getenv("OLLAMA_RERANK_MODEL", OLLAMA_CHAT_MODEL)
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))        # must fit 5 chunks + prompt; Ollama default is too small
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
EMBED_MODEL_ID = os.getenv("EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
EMBED_DIM = 1024
ANSWER_MODEL_ID = os.getenv("ANSWER_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
RERANK_MODEL_ID = os.getenv("RERANK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")

CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL", "").rstrip("/")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")
ATLASSIAN_EMAIL = os.getenv("ATLASSIAN_EMAIL", "")
ATLASSIAN_API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN", "")

MS_TENANT_ID = os.getenv("MS_TENANT_ID", "")
MS_CLIENT_ID = os.getenv("MS_CLIENT_ID", "")
MS_CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET", "")
MS_DRIVE_ID = os.getenv("MS_DRIVE_ID", "")

API_KEY = os.getenv("API_KEY", "dev-key-change-me")

CHUNK_TARGET_CHARS = int(os.getenv("CHUNK_TARGET_CHARS", "1800"))
CHUNK_OVERLAP_CHARS = int(os.getenv("CHUNK_OVERLAP_CHARS", "200"))
MIN_CHUNK_CHARS = 40

TOP_K_RETRIEVE = 30      # per retriever
TOP_K_RERANK_IN = 20
TOP_K_FINAL = 5
MIN_VECTOR_SIM = float(os.getenv("MIN_VECTOR_SIM", "0.30"))
USE_RERANK = _b("USE_RERANK", "false")
USE_HYBRID = _b("USE_HYBRID", "true")
STALE_DAYS = 365

NOT_FOUND_MESSAGE = (
    "I couldn't find this in the sources available to you. "
    "Try rephrasing, or ask the team that owns the topic."
)
