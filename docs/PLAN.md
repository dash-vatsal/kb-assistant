# 30-day plan (about 5 hrs/day)

Never cut: Day 10 (permission filtering) and Days 25-26 (security tests). Cut order if late: Slack bot (24), SharePoint/Drive (16), dashboard (23).

## Before Day 1
- Get security + data-owner approval for the scope (use `docs/scope_template.md`).
- Pick 1-2 non-client Confluence spaces (handbook, onboarding, HIPAA/process).
- Get an Atlassian API token (id.atlassian.com > Security > API tokens) and the list of groups used for access.
- Write 20-30 real questions people ask. Save them in a doc; they become `eval/questions.yaml`.

---
## Phase 1: Scope and access (Days 1-3)

**Day 1: Scope, pilot group, questions**
- Learn: what RAG is (retrieve then generate); why access control is the main risk. Read AWS "RAG" overview and Anthropic "Reduce hallucinations".
- Build: fill `docs/scope_template.md`; choose pilot group (delivery team + pre-sales); finalize question list.
- Done when: scope doc and 20-30 questions exist and the data owner has seen them.

**Day 2: Environment and Bedrock**
- Learn: Bedrock model access, Titan Text Embeddings v2, Converse API.
- Build: `python -m venv .venv && pip install -r requirements.txt`; `cp .env.example .env`; in the Bedrock console enable model access (Titan Embeddings v2, a Claude Sonnet, a Claude Haiku) and copy exact model/inference-profile IDs into `.env`; `aws configure`; `make up && make init`.
- Smoke test: `python -c "from kb.bedrock import embed, generate; print(len(embed('hi'))); print(generate('Be brief','Say OK'))"` (expect 1024 and a reply).
- Done when: both calls work and the schema exists.

**Day 3: Permission model**
- Learn: groups vs ACLs; default-deny; why the filter must run before ranking.
- Build: fill `docs/permission_model.md`; map each space/project to groups in `config/access_map.yaml`; run `make seed` to create the 5 synthetic users (Project A member, Project B member, sales, new joiner, admin).
- Done when: the model is documented, reviewed by the data owner, and the synthetic users exist.

## Phase 2: Ingestion (Days 4-8)

**Day 4: Confluence connector**
- Learn: Confluence REST v1 `/wiki/rest/api/content`, `expand`, pagination, page restrictions.
- Build: `kb/connectors/confluence.py` is provided. Set `CONFLUENCE_BASE_URL`, `ATLASSIAN_*`. Test: `python -c "from kb.connectors.confluence import iter_pages; [print(p.title, p.url, p.restricted) for p in iter_pages('ENG')]"`.
- Check: titles, URLs open, markdown keeps headings, restricted pages flagged.
- Done when: pages for 1-2 spaces print correctly.

**Day 5: Jira connector**
- Learn: JQL, the `/rest/api/3/search/jql` endpoint (token pagination), Atlassian Document Format.
- Build: `kb/connectors/jira.py` provided. Test with a non-client project key you are allowed to index.
- Done when: issues come out with summary, description, comments, resolution.

**Day 6: Cleaning and chunking**
- Learn: why chunk by headings; chunk size/overlap tradeoffs.
- Build: `kb/chunking.py` provided; run `pytest tests/test_chunking.py`. Print chunks for 5 real pages and eyeball them. Strip nav/boilerplate if you see any.
- Done when: chunks look coherent, each has a heading path, none exceed ~2k chars.

**Day 7: Embeddings and pgvector**
- Learn: cosine similarity, HNSW index, why embed `title > heading + text`.
- Build: `python -m kb.sync confluence ENG ONB` (first make sure the spaces are in `access_map.yaml`). Inspect: `psql postgresql://kb:kb@localhost/kb -c "select count(*) from chunks"`.
- Done when: index is built and every chunk has `access_groups` set (query for empty arrays; expect 0).

**Day 8: Incremental sync**
- Learn: hash-based change detection, deletions, permission drift.
- Build: already in `kb/ingest.py`. Test the three cases: (1) edit a page then re-run sync, only it re-embeds; (2) delete a page, re-run, it disappears; (3) change a group in `access_map.yaml`, re-run, `access_groups` updates without re-embedding. Schedule: cron `0 * * * *` or EventBridge. Jira incremental: `--since "YYYY-MM-DD HH:mm"`.
- Done when: all three cases behave as described.

## Phase 3: Retrieval (Days 9-12)

**Day 9: Hybrid search**
- Learn: vector vs keyword (BM25-style) strengths; Reciprocal Rank Fusion.
- Build: `kb/retrieval.py` provided. Try 10 questions: `python -c "from kb.db import connect; from kb.retrieval import hybrid_search; c=connect(); [print(h['title'], round(h['sim'],2)) for h in hybrid_search(c,'code review process',['all-staff'])]"`. Compare `USE_HYBRID=false`.
- Done when: good hits on 10 queries.

**Day 10: Permission-aware retrieval (never cut)**
- Learn: filter-then-rank; default deny; the ACL clause runs in SQL for both retrievers and again on the final fetch.
- Build: run `make test` (`tests/test_security.py`). Also test by hand with each synthetic user. Add any missed trap.
- Done when: each test user sees only allowed chunks; unknown user sees nothing.

**Day 11: Reranking**
- Learn: bi-encoder vs cross-encoder/LLM rerank; cost vs latency.
- Build: `kb/rerank.py` (Haiku scoring top 20 to top 5) provided. Compare with/without (`--no-rerank` in eval later). Optional: try Cohere Rerank on Bedrock if available.
- Done when: relevance visibly improves on your hard questions.

**Day 12: Tuning and baseline**
- Build: tune `CHUNK_TARGET_CHARS`, `TOP_K_*`; for each of your questions check whether the right page is in top 5; record baseline hit rate in a spreadsheet.
- Done when: baseline number recorded.

## Phase 4: Answering (Days 13-16)

**Day 13: Grounded answers**
- Learn: prompt rules, citation formats, treating sources as untrusted data.
- Build: `kb/answer.py` provided. Run questions through `answer_question`; confirm each claim has `[n]` citations that map to sources.
- Done when: cited answers on your sample questions.

**Day 14: "Not found" behavior**
- Learn: two gates: similarity threshold + model sufficiency/citation check.
- Build: tune `MIN_VECTOR_SIM` with 10 off-topic questions (should refuse) and 10 answerable ones (should answer). Plot best-sim for both groups and choose the threshold between them.
- Done when: off-topic questions are refused, valid ones answered.

**Day 15: Stale and conflicting docs**
- Build: `last_updated` shows on every citation; `possibly_outdated` set after `STALE_DAYS`. The prompt tells the model to flag conflicts and prefer newer (synthetic data has an old/new code review pair: ask "how many reviewers does a PR need?").
- Done when: warnings appear and conflicts are surfaced.

**Day 16: Wave 2 connector (SharePoint/Drive)**
- Learn: Microsoft Graph app-only auth, drive items, docx/pdf parsing. (Needs an Entra app registration with admin consent; if blocked, document it and move on.)
- Build: `kb/connectors/sharepoint.py` provided; set `MS_*`; `python -m kb.sync sharepoint "Delivery/Process"` after adding the folder to `access_map.yaml`.
- Done when: documents are searchable with access tags (or blocker documented).

## Phase 5: Evaluation (Days 17-20)

**Day 17: Test set**
- Build: `eval/questions.yaml` with 40-60 items: about 30 answerable (with `expected_urls` and a short `reference`), about 10 `no_answer`, about 10 `trap` (with `forbidden` strings). Have a second person sanity-check the references.
- Done when: test set is ready and reviewed.

**Day 18: Scoring**
- Build: `python eval/run_eval.py eval/questions.yaml --judge`. Prints hit@5, correctness, citation accuracy, not-found rate, trap pass rate; writes `eval/results.csv`. Hand-score 10 answers to check the LLM judge agrees with you.
- Done when: scores run end to end.

**Day 19: Variants**
- Run and tabulate: baseline; `--no-rerank`; `--vector-only`; chunk size 900 vs 1800 vs 3000 (`CHUNK_TARGET_CHARS=900 python -m kb.sync confluence ENG ONB --force`, then eval).
- Done when: results table exists.

**Day 20: Failure analysis**
- Build: open `results.csv`, sort failures into missing doc / retrieval miss / bad answer / bad citation; fix the top 3 causes; tag the repo `v1`.
- Done when: first reportable numbers frozen.

## Phase 6: Interface and feedback (Days 21-24)

**Day 21: API**: `make api`; test `/ask` with curl:
`curl -s localhost:8000/ask -H 'X-Api-Key: dev-key-change-me' -H 'X-User-Id: new_nina' -H 'content-type: application/json' -d '{"question":"What is the code review process?"}'`
Done when: it returns answer + citations and rejects bad key/unknown user.

**Day 22: Streamlit UI**: `make ui`. Check: ask box, answer, source links, last-updated, outdated warning, thumbs up/down. Done when someone else can use it unaided.

**Day 23: Audit and dashboard**: every request is in `query_log` (who, what, returned chunks); feedback in `feedback`. Open the dashboard page (queries/day, not-found rate, thumbs, repeat usage, unanswered list). Decide retention (e.g., 90 days) and who can read logs. Done when logs and dashboard work.

**Day 24: Slack/Teams bot (optional)**: request admin approval early (Day 1 if possible). Create a Slack app (Socket Mode, `app_mentions:read`, `chat:write`, `users:read`, `users:read.email`), set tokens, `make bot`. Done when the bot answers in a thread, or the blocker is documented as a next step.

## Phase 7: Security (Days 25-26, never cut)

**Day 25: Extraction attempts**
- Run `make test`, then try manually with the 5 users: rephrasing, "ignore your rules", asking about restricted projects by name, asking for lists of codes/IDs, asking via the bot with a different user. Check `query_log.returned_doc_ids` for every attempt.
- Also verify: the "not found" message never hints that a restricted document exists (silence policy).
- Done when: 100% of traps blocked and logs show no leaks.

**Day 26: Prompt injection via documents**
- The synthetic onboarding doc contains an injected instruction; `test_security.py::injection` checks the model ignores it. Add 2-3 more variants (hidden text, "system:" prefixes, instructions to output links). Defenses in place: sources labeled untrusted, strict JSON output, citation validation, no tools given to the model.
- Done when: defenses are in place and tests pass.

## Phase 8: Pilot and pitch (Days 27-30)

**Day 27: Launch**: add 5-10 real pilot users to the `users` table with groups copied from source systems (reviewed by data owner); send `docs/pilot_note.md`. Done when users are asking real questions.

**Day 28: Monitor**: check dashboard daily; for each thumbs-down or not-found, set `query_log.failure_tag` (`missing_doc` / `retrieval` / `answer` / `permission`): `update query_log set failure_tag='missing_doc' where id=...`. Fix quick issues. Done when failures are categorized.

**Day 29: Analysis**: collect ratings, repeat usage, top unanswered questions; re-run eval; compare against Bedrock Knowledge Bases using `docs/bedrock_kb_comparison.md` (same 20 questions, same corpus subset). Done when the results slide has the numbers.

**Day 30: Demo**: follow `docs/demo_script.md`; fill `docs/writeup_template.md`. Include the documentation-gap list. Done when the demo is delivered.
