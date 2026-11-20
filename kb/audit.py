def log_query(conn, user_id, question, hits, answer, found, latency_ms) -> int:
    row = conn.execute("""
        INSERT INTO query_log (user_id, question, returned_chunk_ids, returned_doc_ids, answer, found, latency_ms)
        VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
        (user_id, question, [h["chunk_id"] for h in hits], sorted({h["doc_id"] for h in hits}),
         answer, found, latency_ms)).fetchone()
    return row[0]


def log_feedback(conn, query_id: int, rating: int, comment: str | None = None):
    conn.execute("INSERT INTO feedback (query_id, rating, comment) VALUES (%s,%s,%s)",
                 (query_id, rating, comment))
