"""Retention: delete query logs (and their feedback) older than N days.  python scripts/purge_logs.py 90"""
import sys
from kb.db import connect

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    conn = connect()
    conn.execute("DELETE FROM feedback WHERE query_id IN (SELECT id FROM query_log WHERE ts < now() - make_interval(days => %s))", (days,))
    n = conn.execute("DELETE FROM query_log WHERE ts < now() - make_interval(days => %s)", (days,)).rowcount
    print(f"deleted {n} query_log rows older than {days} days")
