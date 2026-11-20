import os
import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")
H = {"X-Api-Key": os.getenv("API_KEY", "dev-key-change-me")}

st.set_page_config(page_title="Internal Knowledge Assistant", page_icon="📚")
st.title("📚 Internal Knowledge Assistant")

users = requests.get(f"{API}/users", headers=H, timeout=30).json()
uid = st.sidebar.selectbox("Simulated user (POC only)", [u["user_id"] for u in users])
st.sidebar.caption("In the pilot, identity comes from SSO, not a dropdown.")

q = st.text_input("Ask a question", placeholder="How did we handle HL7 integration on past projects?")
if st.button("Ask") and q.strip():
    with st.spinner("Searching..."):
        r = requests.post(f"{API}/ask", json={"question": q}, headers={**H, "X-User-Id": uid}, timeout=600)
    st.session_state["last"] = r.json() if r.ok else {"error": r.text}

res = st.session_state.get("last")
if res:
    if "error" in res:
        st.error(res["error"])
    else:
        (st.markdown if res["found"] else st.info)(res["answer"])
        if res["citations"]:
            st.subheader("Sources")
            for c in res["citations"]:
                warn = " ⚠️ possibly outdated" if c["possibly_outdated"] else ""
                st.markdown(f"**[{c['n']}]** [{c['title']}]({c['url']}) — {c['section']} "
                            f"· updated {c['last_updated']}{warn}")
        c1, c2, _ = st.columns([1, 1, 6])
        if c1.button("👍"):
            requests.post(f"{API}/feedback", json={"query_id": res["query_id"], "rating": 1}, headers=H)
            st.toast("Thanks!")
        if c2.button("👎"):
            requests.post(f"{API}/feedback", json={"query_id": res["query_id"], "rating": -1}, headers=H)
            st.toast("Thanks, logged.")
