"""Jira Cloud connector. Issues become one document each: summary, description, resolution, comments."""
import requests
from kb import config
from kb.models import Document, parse_ts

FIELDS = ["summary", "description", "comment", "resolution", "status",
          "updated", "reporter", "assignee", "issuetype"]


def adf_to_text(node) -> str:
    """Atlassian Document Format (JSON) -> plain text."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    t = node.get("type")
    if t == "text":
        return node.get("text", "")
    inner = "".join(adf_to_text(c) for c in node.get("content", []))
    if t in ("paragraph", "heading", "bulletList", "orderedList", "codeBlock", "blockquote"):
        return inner + "\n"
    if t == "listItem":
        return "- " + inner
    if t == "hardBreak":
        return "\n"
    return inner


def iter_issues(project_key: str, since: str | None = None):
    """since: 'YYYY-MM-DD HH:mm' for incremental runs."""
    s = requests.Session()
    s.auth = (config.ATLASSIAN_EMAIL, config.ATLASSIAN_API_TOKEN)
    s.headers["Accept"] = "application/json"
    jql = f'project = "{project_key}"'
    if since:
        jql += f' AND updated >= "{since}"'
    jql += " ORDER BY updated DESC"
    token = None
    while True:
        body = {"jql": jql, "maxResults": 50, "fields": FIELDS}
        if token:
            body["nextPageToken"] = token
        r = s.post(f"{config.JIRA_BASE_URL}/rest/api/3/search/jql", json=body, timeout=60)
        r.raise_for_status()
        data = r.json()
        for it in data.get("issues", []):
            f = it["fields"]
            comments = f.get("comment", {}).get("comments", [])
            parts = [f"# {it['key']}: {f.get('summary', '')}",
                     f"Status: {(f.get('status') or {}).get('name', '')}  "
                     f"Type: {(f.get('issuetype') or {}).get('name', '')}  "
                     f"Resolution: {(f.get('resolution') or {}).get('name', 'Unresolved')}",
                     "## Description", adf_to_text(f.get("description"))]
            if comments:
                parts.append("## Comments")
                for c in comments:
                    parts.append(f"- {c['author']['displayName']}: {adf_to_text(c['body']).strip()}")
            yield Document(
                doc_id=f"jira:{it['key']}", source="jira", container=project_key,
                title=f"{it['key']}: {f.get('summary', '')}",
                url=f"{config.JIRA_BASE_URL}/browse/{it['key']}",
                owner=(f.get("reporter") or {}).get("displayName", ""),
                last_updated=parse_ts(f.get("updated")),
                text="\n".join(parts),
            )
        token = data.get("nextPageToken")
        if not token or data.get("isLast"):
            break
