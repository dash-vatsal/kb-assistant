"""Permission-aware hybrid retrieval. The ACL filter is inside every SQL query, i.e. BEFORE ranking."""
import re
import numpy as np
from kb import config
from kb.llm import embed

RRF_K = 60


def _vector(conn, qv, groups, k):
    return conn.execute("""
        SELECT chunk_id FROM chunks
        WHERE access_groups && %s::text[]
        ORDER BY embedding <=> %s LIMIT %s""", (groups, qv, k)).fetchall()


def _keyword(conn, question, groups, k):
    words = {w.lower() for w in re.findall(r"[A-Za-z0-9]{3,}", question)}
    if not words:
        return []
    tsq = " | ".join(sorted(words))
    return conn.execute("""
        SELECT chunk_id FROM chunks, to_tsquery('english', %s) q
        WHERE tsv @@ q AND access_groups && %s::text[]
        ORDER BY ts_rank_cd(tsv, q) DESC LIMIT %s""", (tsq, groups, k)).fetchall()


def hybrid_search(conn, question: str, groups: list[str], k: int | None = None) -> list[dict]:
    """Returns hits: chunk_id, doc_id, title, url, last_updated, heading_path, text, sim, rrf."""
    if not groups:                       # default deny
        return []
    k = k or config.TOP_K_RETRIEVE
    qv = np.array(embed(question))
    rankings = [[r[0] for r in _vector(conn, qv, groups, k)]]
    if config.USE_HYBRID:
        rankings.append([r[0] for r in _keyword(conn, question, groups, k)])
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (RRF_K + rank + 1)
    if not scores:
        return []
    top_ids = sorted(scores, key=scores.get, reverse=True)[: config.TOP_K_RERANK_IN]
    rows = conn.execute("""
        SELECT c.chunk_id, c.doc_id, d.title, d.url, d.last_updated, c.heading_path, c.text,
               1 - (c.embedding <=> %s) AS sim
        FROM chunks c JOIN documents d USING (doc_id)
        WHERE c.chunk_id = ANY(%s) AND c.access_groups && %s::text[]""",   # belt and braces
        (qv, top_ids, groups)).fetchall()
    cols = ["chunk_id", "doc_id", "title", "url", "last_updated", "heading_path", "text", "sim"]
    hits = [dict(zip(cols, r), rrf=scores[r[0]]) for r in rows]
    return sorted(hits, key=lambda h: h["rrf"], reverse=True)
