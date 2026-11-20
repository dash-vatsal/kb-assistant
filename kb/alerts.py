import json
import os
import requests


def alert(message: str):
    """Post to a Slack/Teams incoming webhook if ALERT_WEBHOOK_URL is set; always print."""
    print(f"[ALERT] {message}")
    url = os.getenv("ALERT_WEBHOOK_URL")
    if url:
        try:
            requests.post(url, data=json.dumps({"text": message}),
                          headers={"Content-Type": "application/json"}, timeout=10)
        except Exception as e:
            print(f"[alert delivery failed] {e}")
