"""Access model. Rule #1: unknown = denied."""
from functools import lru_cache
from pathlib import Path
import yaml


@lru_cache
def _map() -> dict:
    p = Path(__file__).parent.parent / "config" / "access_map.yaml"
    return yaml.safe_load(p.read_text()) or {}


def groups_for(source: str, container: str) -> list[str]:
    """Access groups a document gets. Empty list => do not ingest."""
    return list(_map().get(source, {}).get(container, []) or [])


def user_groups(conn, user_id: str) -> list[str]:
    row = conn.execute("SELECT groups FROM users WHERE user_id=%s", (user_id,)).fetchone()
    return list(row[0]) if row else []   # unknown user => no groups => sees nothing
