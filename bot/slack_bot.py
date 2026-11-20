"""Thin Slack bot over the same /ask API (Socket Mode: no public URL needed). Needs workspace admin approval."""
import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

API = os.getenv("API_URL", "http://localhost:8000")
KEY = {"X-Api-Key": os.getenv("API_KEY", "dev-key-change-me")}
app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.event("app_mention")
def on_mention(event, say, client):
    text = " ".join(w for w in event["text"].split() if not w.startswith("<@"))
    email = client.users_info(user=event["user"])["user"]["profile"].get("email", "")
    r = requests.post(f"{API}/resolve_email", params={"email": email}, headers=KEY, timeout=30)
    if not r.ok:
        say(thread_ts=event["ts"], text="I can't match your Slack account to a pilot user.")
        return
    uid = r.json()["user_id"]
    res = requests.post(f"{API}/ask", json={"question": text}, headers={**KEY, "X-User-Id": uid}, timeout=600).json()
    lines = [res["answer"]]
    for c in res.get("citations", []):
        lines.append(f"[{c['n']}] <{c['url']}|{c['title']}> (updated {c['last_updated']})"
                     + (" ⚠️ possibly outdated" if c["possibly_outdated"] else ""))
    say(thread_ts=event["ts"], text="\n".join(lines))


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
