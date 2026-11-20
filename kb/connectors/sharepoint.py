"""Wave 2: SharePoint/OneDrive via Microsoft Graph (app-only). Parses .docx and .pdf.
Needs an Entra app registration with Sites.Read.All / Files.Read.All (admin consent).
Google Drive: same shape, use the Drive API files.list + files.export instead."""
import io
import msal
import requests
from docx import Document as DocxDoc
from pypdf import PdfReader
from kb import config
from kb.models import Document, parse_ts

GRAPH = "https://graph.microsoft.com/v1.0"


def _token() -> str:
    app = msal.ConfidentialClientApplication(
        config.MS_CLIENT_ID, client_credential=config.MS_CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{config.MS_TENANT_ID}")
    return app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])["access_token"]


def _docx_to_md(data: bytes) -> str:
    out = []
    for p in DocxDoc(io.BytesIO(data)).paragraphs:
        name = p.style.name or ""
        if name.startswith("Heading ") and name[8:].isdigit():
            out.append("#" * int(name[8:]) + " " + p.text)
        elif p.text.strip():
            out.append(p.text)
    return "\n\n".join(out)


def _pdf_to_text(data: bytes) -> str:
    return "\n\n".join((pg.extract_text() or "") for pg in PdfReader(io.BytesIO(data)).pages)


def _walk(headers, url):
    while url:
        r = requests.get(url, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        for item in data.get("value", []):
            yield item
        url = data.get("@odata.nextLink")


def iter_files(folder_path: str):
    """folder_path like 'Delivery/Process' (relative to drive root)."""
    h = {"Authorization": f"Bearer {_token()}"}
    stack = [f"{GRAPH}/drives/{config.MS_DRIVE_ID}/root:/{folder_path}:/children"]
    while stack:
        for item in _walk(h, stack.pop()):
            if "folder" in item:
                stack.append(f"{GRAPH}/drives/{config.MS_DRIVE_ID}/items/{item['id']}/children")
                continue
            name = item["name"].lower()
            if not name.endswith((".docx", ".pdf")):
                continue
            data = requests.get(item["@microsoft.graph.downloadUrl"], timeout=120).content
            text = _docx_to_md(data) if name.endswith(".docx") else _pdf_to_text(data)
            yield Document(
                doc_id=f"sharepoint:{item['id']}", source="sharepoint", container=folder_path,
                title=item["name"], url=item["webUrl"],
                owner=(item.get("createdBy", {}).get("user", {}) or {}).get("displayName", ""),
                last_updated=parse_ts(item.get("lastModifiedDateTime")),
                text=f"# {item['name']}\n\n{text}")
