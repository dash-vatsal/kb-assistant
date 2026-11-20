"""Heading-aware chunking. Keeps the heading path with each chunk so retrieval has context."""
import re
from dataclasses import dataclass
from kb import config

HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


@dataclass
class Chunk:
    ord: int
    heading_path: str
    text: str
    embed_text: str


def split_sections(md: str) -> list[tuple[str, str]]:
    """-> [(heading_path, body)]"""
    stack: list[tuple[int, str]] = []
    sections, buf, path = [], [], ""
    in_code = False

    def flush():
        body = "\n".join(buf).strip()
        if body:
            sections.append((path, body))
        buf.clear()

    for line in md.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        m = None if in_code else HEADING.match(line)
        if m:
            flush()
            level, title = len(m.group(1)), m.group(2)
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            path = " > ".join(t for _, t in stack)
        else:
            buf.append(line)
    flush()
    return sections


def _split_long(body: str, target: int, overlap: int) -> list[str]:
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    out, cur = [], ""
    for p in paras:
        while len(p) > target:                      # a single huge paragraph
            if cur:
                out.append(cur); cur = ""
            out.append(p[:target]); p = p[target - overlap:]
        if cur and len(cur) + len(p) + 2 > target:
            out.append(cur)
            cur = cur[-overlap:] + "\n\n" + p if overlap else p
        else:
            cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        out.append(cur)
    return out


def chunk_document(title: str, md: str, target: int | None = None, overlap: int | None = None) -> list[Chunk]:
    target = target or config.CHUNK_TARGET_CHARS
    overlap = config.CHUNK_OVERLAP_CHARS if overlap is None else overlap
    chunks: list[Chunk] = []
    for path, body in split_sections(md):
        pieces = [body] if len(body) <= target else _split_long(body, target, overlap)
        for piece in pieces:
            if len(piece.strip()) < config.MIN_CHUNK_CHARS:
                continue
            hp = path or title
            chunks.append(Chunk(len(chunks), hp, piece.strip(), f"{title} > {hp}\n{piece.strip()}"))
    return chunks
