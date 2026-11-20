"""Confluence Cloud connector (REST v1). Yields Document objects for every current page in a space."""
import requests
from markdownify import markdownify as md
from kb import config
from kb.models import Document, parse_ts


def _session():
    s = requests.Session()
    s.auth = (config.ATLASSIAN_EMAIL, config.ATLASSIAN_API_TOKEN)
    s.headers["Accept"] = "application/json"
    return s


def iter_pages(space_key: str):
    s = _session()
    url = f"{config.CONFLUENCE_BASE_URL}/wiki/rest/api/content"
    params = {
        "spaceKey": space_key, "type": "page", "status": "current", "limit": 50,
        "expand": ("body.storage,version,history,"
                   "restrictions.read.restrictions.user,restrictions.read.restrictions.group"),
    }
    while url:
        r = s.get(url, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        base = data.get("_links", {}).get("base", f"{config.CONFLUENCE_BASE_URL}/wiki")
        for p in data["results"]:
            restr = p.get("restrictions", {}).get("read", {}).get("restrictions", {})
            restricted = bool(restr.get("user", {}).get("results") or restr.get("group", {}).get("results"))
            html = p.get("body", {}).get("storage", {}).get("value", "")
            body = md(html, heading_style="ATX")
            yield Document(
                doc_id=f"confluence:{p['id']}",
                source="confluence",
                container=space_key,
                title=p["title"],
                url=base + p["_links"]["webui"],
                owner=p.get("history", {}).get("createdBy", {}).get("displayName", ""),
                last_updated=parse_ts(p.get("version", {}).get("when")),
                text=f"# {p['title']}\n\n{body}",
                restricted=restricted,
            )
        nxt = data.get("_links", {}).get("next")
        url, params = (base + nxt, None) if nxt else (None, None)
