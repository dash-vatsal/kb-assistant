"""Ingestion: hash-skip unchanged docs, re-embed changed ones, propagate permission changes, delete removed docs."""
import hashlib
from collections import Counter
import numpy as np
from kb import config
from kb.llm import embed
from kb.chunking import chunk_document
from kb.models import Document
from kb.permissions import groups_for


def _hash(doc: Document) -> str:
    return hashlib.sha256(f"{doc.title}\n{doc.text}".encode()).hexdigest()


def remove_document(conn, doc_id: str):
    conn.execute("DELETE FROM documents WHERE doc_id=%s", (doc_id,))   # chunks cascade


def ingest_document(conn, doc: Document, groups: list[str], force: bool = False) -> str:
    if not groups:
        raise ValueError(f"No access groups for {doc.doc_id}; refusing to ingest (default deny)")
    h = _hash(doc)
    row = conn.execute("SELECT content_hash, access_groups FROM documents WHERE doc_id=%s",
                       (doc.doc_id,)).fetchone()
    if row and row[0] == h and not force:
        if sorted(row[1]) != sorted(groups):            # permission change only: no re-embedding
            with conn.transaction():
                conn.execute("UPDATE documents SET access_groups=%s WHERE doc_id=%s", (groups, doc.doc_id))
                conn.execute("UPDATE chunks SET access_groups=%s WHERE doc_id=%s", (groups, doc.doc_id))
            return "permissions_updated"
        return "unchanged"

    chunks = chunk_document(doc.title, doc.text)
    embs = [np.array(embed(c.embed_text)) for c in chunks]
    with conn.transaction():
        conn.execute("""
            INSERT INTO documents (doc_id, source, container, title, url, owner, last_updated,
                                   content_hash, access_groups, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s, now())
            ON CONFLICT (doc_id) DO UPDATE SET title=EXCLUDED.title, url=EXCLUDED.url,
              owner=EXCLUDED.owner, last_updated=EXCLUDED.last_updated,
              content_hash=EXCLUDED.content_hash, access_groups=EXCLUDED.access_groups, synced_at=now()
        """, (doc.doc_id, doc.source, doc.container, doc.title, doc.url, doc.owner,
              doc.last_updated, h, groups))
        conn.execute("DELETE FROM chunks WHERE doc_id=%s", (doc.doc_id,))
        for c, e in zip(chunks, embs):
            conn.execute("""INSERT INTO chunks (doc_id, ord, heading_path, text, embedding, access_groups)
                            VALUES (%s,%s,%s,%s,%s,%s)""",
                         (doc.doc_id, c.ord, c.heading_path, c.text, e, groups))
    return "updated" if row else "added"


def run_connector(conn, source: str, container: str, docs, full: bool = True, force: bool = False) -> Counter:
    groups = groups_for(source, container)
    stats: Counter = Counter()
    if not groups:
        print(f"[skip] {source}/{container}: not in config/access_map.yaml (default deny)")
        return stats
    seen = set()
    for d in docs:
        seen.add(d.doc_id)
        if d.restricted:                                 # page-level restriction => never index
            remove_document(conn, d.doc_id)
            stats["skipped_restricted"] += 1
            continue
        stats[ingest_document(conn, d, groups, force)] += 1
    if full and seen:                                    # never mass-delete on an empty/failed fetch
        for (doc_id,) in conn.execute("SELECT doc_id FROM documents WHERE source=%s AND container=%s",
                                      (source, container)).fetchall():
            if doc_id not in seen:
                remove_document(conn, doc_id)
                stats["deleted"] += 1
    return stats
