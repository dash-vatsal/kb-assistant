"""Backend API. POC auth: shared API key + trusted client asserts the user id (X-User-Id).
PRODUCTION: replace with SSO (OIDC/JWT) and derive groups from the IdP / source systems."""
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from kb import config
from kb.answer import answer_question
from kb.audit import log_feedback
from kb.db import connect
from kb.ratelimit import RateLimiter

app = FastAPI(title="Internal Knowledge Assistant")
limiter = RateLimiter(max_calls=20, window_s=60)   # per user


class AskReq(BaseModel):
    question: str


class FeedbackReq(BaseModel):
    query_id: int
    rating: int          # 1 or -1
    comment: str | None = None


def _auth(x_api_key: str):
    if x_api_key != config.API_KEY:
        raise HTTPException(401, "bad api key")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/users")
def users(x_api_key: str = Header(...)):          # POC only: lets the UI simulate users
    _auth(x_api_key)
    with connect() as conn:
        return [{"user_id": r[0], "name": r[1]} for r in conn.execute("SELECT user_id, name FROM users ORDER BY 1")]


@app.post("/ask")
def ask(req: AskReq, x_api_key: str = Header(...), x_user_id: str = Header(...)):
    _auth(x_api_key)
    if not limiter.allow(x_user_id):
        raise HTTPException(429, "too many requests; try again in a minute")
    with connect() as conn:
        if not conn.execute("SELECT 1 FROM users WHERE user_id=%s", (x_user_id,)).fetchone():
            raise HTTPException(403, "unknown user")
        res = answer_question(conn, req.question.strip()[:2000], x_user_id)
    return {k: v for k, v in res.items() if not k.startswith("_")}


@app.post("/feedback")
def feedback(req: FeedbackReq, x_api_key: str = Header(...)):
    _auth(x_api_key)
    if req.rating not in (1, -1):
        raise HTTPException(422, "rating must be 1 or -1")
    with connect() as conn:
        log_feedback(conn, req.query_id, req.rating, req.comment)
    return {"ok": True}


@app.post("/resolve_email")
def resolve_email(email: str, x_api_key: str = Header(...)):   # used by the Slack bot
    _auth(x_api_key)
    with connect() as conn:
        row = conn.execute("SELECT user_id FROM users WHERE lower(email)=lower(%s)", (email,)).fetchone()
    if not row:
        raise HTTPException(404, "no such user")
    return {"user_id": row[0]}
