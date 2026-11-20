from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Document:
    doc_id: str
    source: str
    container: str
    title: str
    url: str
    owner: str
    last_updated: Optional[datetime]
    text: str              # markdown-ish, headings kept as '#'
    restricted: bool = False   # page-level restriction found at the source -> never ingested


def parse_ts(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f%z")
