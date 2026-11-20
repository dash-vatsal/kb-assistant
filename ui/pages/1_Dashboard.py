import pandas as pd
import streamlit as st
from kb.db import connect

st.title("Pilot dashboard")
conn = connect()
q = pd.read_sql("SELECT * FROM query_log", conn)
fb = pd.read_sql("SELECT * FROM feedback", conn)
if q.empty:
    st.info("No queries yet.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Queries", len(q))
c2.metric("Active users", q.user_id.nunique())
c3.metric("Not-found rate", f"{(~q.found).mean():.0%}")
c4.metric("Thumbs-up rate", f"{(fb.rating == 1).mean():.0%}" if len(fb) else "n/a")

st.subheader("Queries per day")
st.bar_chart(q.assign(day=q.ts.dt.date).groupby("day").size())
st.subheader("Repeat usage (queries per user)")
st.bar_chart(q.groupby("user_id").size())
st.subheader("Top unanswered questions  (= documentation gaps)")
st.dataframe(q[~q.found][["ts", "user_id", "question"]].sort_values("ts", ascending=False), use_container_width=True)
st.subheader("Thumbs-down answers")
bad = fb[fb.rating == -1].merge(q, left_on="query_id", right_on="id")
st.dataframe(bad[["ts_x", "user_id", "question", "answer", "comment"]] if len(bad) else bad, use_container_width=True)

st.subheader("Sync health (latest run per source)")
runs = pd.read_sql("""SELECT DISTINCT ON (source, container) source, container, status, started_at, finished_at, stats, error
                      FROM sync_runs ORDER BY source, container, started_at DESC""", conn)
st.dataframe(runs, use_container_width=True)
