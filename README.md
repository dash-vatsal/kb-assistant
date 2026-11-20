# Internal Knowledge Assistant: 30-day POC kit

Permission-aware RAG over Confluence + Jira (then SharePoint/Drive) on AWS Bedrock, with cited answers or an honest "not found".

**Start here:** `docs/STAGE1_EXECUTION_PLAN.md` (6-week plan mapped to backlog tasks), then `docs/PLAN.md` (30-day learning plan).

## Layout
| Path | What |
|---|---|
| `docs/PLAN.md` | Day-by-day plan with steps and exit criteria |
| `docs/*.md` | Templates: scope, permission model, pilot note, demo script, write-up, Bedrock KB comparison |
| `config/access_map.yaml` | (source, container) -> access groups. **Default deny** |
| `sql/schema.sql` | Postgres + pgvector schema (docs, chunks, users, logs, feedback) |
| `kb/connectors/` | Confluence, Jira, SharePoint |
| `kb/chunking.py`, `kb/ingest.py`, `kb/sync.py` | Chunk, embed, incremental sync, deletions, permission changes |
| `kb/retrieval.py`, `kb/rerank.py`, `kb/answer.py` | Hybrid search with ACL filter, rerank, grounded answers |
| `kb/api.py`, `ui/`, `bot/` | FastAPI backend, Streamlit app + dashboard, Slack bot |
| `scripts/seed_synthetic.py` | 5 test users + canary docs for permission tests |
| `eval/`, `tests/` | Scoring script, trap questions, security tests |

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # Atlassian creds; models default to local Ollama
make up && make init            # Postgres+pgvector + Ollama, create schema
make models                     # pull bge-m3 and qwen2.5:7b-instruct (about 6 GB, once)
make check                      # model smoke test
make seed                       # synthetic users + docs
make test                       # chunking + security tests
make api                        # terminal 1
make ui                         # terminal 2 -> http://localhost:8501
```
Real data: edit `config/access_map.yaml`, then `python -m kb.sync confluence ENG ONB` and `python -m kb.sync jira ALPHA`.

## Known POC shortcuts (fix before any real rollout)
- Identity: shared API key + `X-User-Id` header. Replace with SSO (OIDC/JWT).
- Groups: static map + `users` table. Replace with groups synced from the IdP / source systems.
- Local 7B models are weaker than hosted ones; the eval decides whether answer quality is good enough. Bedrock stays available via `LLM_PROVIDER=bedrock`.
- Confluence page-level restrictions are skipped (not indexed). Space-level access comes from `access_map.yaml`.

## Working with Claude Code (recommended)
1. Export the BRD and FRD tabs of the planning doc as Markdown into `docs/brd.md` and `docs/frd.md`.
2. Open this folder in VS Code and start Claude Code. It reads `CLAUDE.md` and `.claude/` automatically.
3. Pick the next unticked task in `TASKS.md`, then run `/start-task T-0xx`, approve the plan, let it write tests first, then `/finish-task T-0xx`.
4. Other commands: `/security-review`, `/eval-report`. Subagent: `security-reviewer`.
Never let the assistant read `.env`, push to git, or change `eval/security_traps.yaml` to make a test pass.
