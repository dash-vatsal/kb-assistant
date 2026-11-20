"""CLI:
  python -m kb.sync confluence ENG ONB
  python -m kb.sync jira ALPHA BETA [--since "2026-11-01 00:00"]
  python -m kb.sync sharepoint "Delivery/Process"
  add --force to re-chunk/re-embed everything
Every run is recorded in sync_runs. Failures alert (ALERT_WEBHOOK_URL) and the process exits non-zero."""
import argparse
import json
import sys
from kb.alerts import alert
from kb.db import connect
from kb.ingest import run_connector


def _docs(source, container, since):
    if source == "confluence":
        from kb.connectors.confluence import iter_pages
        return iter_pages(container), True
    if source == "jira":
        from kb.connectors.jira import iter_issues
        return iter_issues(container, since), since is None
    from kb.connectors.sharepoint import iter_files
    return iter_files(container), True


def sync_container(conn, source, container, since=None, force=False) -> bool:
    run_id = conn.execute("INSERT INTO sync_runs (source, container) VALUES (%s,%s) RETURNING id",
                          (source, container)).fetchone()[0]
    try:
        docs, full = _docs(source, container, since)
        stats = dict(run_connector(conn, source, container, docs, full=full, force=force))
        conn.execute("UPDATE sync_runs SET status='ok', finished_at=now(), stats=%s WHERE id=%s",
                     (json.dumps(stats), run_id))
        print(source, container, stats)
        return True
    except Exception as e:                                  # connector/API/Bedrock failure
        conn.execute("UPDATE sync_runs SET status='failed', finished_at=now(), error=%s WHERE id=%s",
                     (str(e)[:2000], run_id))
        alert(f"Sync FAILED for {source}/{container}: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", choices=["confluence", "jira", "sharepoint"])
    ap.add_argument("containers", nargs="+")
    ap.add_argument("--since")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    conn = connect()
    ok = all([sync_container(conn, a.source, c, a.since, a.force) for c in a.containers])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
