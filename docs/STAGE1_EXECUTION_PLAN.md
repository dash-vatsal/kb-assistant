# Stage 1 execution plan (Lean MVP: 6 weeks, about 5 hours a day, solo)

Covers backlog tasks T-001 to T-004, T-006, T-010 to T-016, T-020, T-021, T-030 to T-032, T-040 to T-042, T-044, T-002, T-050 to T-052, T-054, T-060 to T-063, T-070, T-090.
Deferred to stage 2: T-005 (infrastructure as code; use docker-compose now), SSO, IdP group sync, bot, SharePoint/Drive.
Rule for every day: work on a branch, `make test` green before merge, commit message starts with the task ID.
Buffer: 20% of each week is slack. If you fall more than 3 days behind, cut in this order: T-054, T-063, T-052.

## Week 1: Foundations and access (T-001, T-002, T-003, T-004, T-006, T-012, T-020)
| Day | Do | Done when |
| --- | --- | --- |
| 1 | Fill docs/scope_template.md; list 1-2 NON-client Confluence spaces and 1 Jira project; send to data owner and security for approval (T-001). Start collecting 30 real questions (T-002) | Approval request sent; question list started |
| 2 | Start Ollama and pull models (`make up`, `make models`), then `make check` (T-003). Fill docs/data_handling_decision.md (T-006) | check_llm prints 1024 dims and valid JSON |
| 3 | Create git repo, push to GitHub/GitLab, confirm .github/workflows/ci.yml runs green (T-004). `make up && make init` | CI green on first push |
| 4 | Edit config/access_map.yaml for approved containers only (T-012). `make seed` (T-020). Read docs/permission_model.md and fill it | 5 synthetic users exist; access map reviewed |
| 5 | `make itest` (security tests on synthetic data). Fix anything red. Chase approval | All integration tests pass; approval status known |

Gate to continue: written approval for at least one space. Do not connect real data before this.

## Week 2: Ingestion (T-010, T-011, T-013, T-014, T-021)
| Day | Do | Done when |
| --- | --- | --- |
| 6 | Atlassian token in .env. Test Confluence connector on one space (print titles, URLs, restricted flag) (T-010) | Titles and links correct |
| 7 | Test Jira connector on one project (T-011). Run `pytest` chunking tests on real pages (T-013) | Issues print with comments; chunks look right |
| 8 | `python -m kb.sync confluence <SPACE>` (T-014). Check chunks have access groups (SQL in plan) | Index built, zero empty access groups |
| 9 | `python -m kb.sync jira <PROJECT>`. Inspect 10 random chunks for noise (macros, nav text); fix cleaning in connector | Clean text on sample |
| 10 | Add 5 trap cases for real containers to eval/security_traps.yaml (T-021); run `make itest` | Test users see only allowed chunks |

Check query: `select count(*) from chunks where cardinality(access_groups)=0;` must be 0.

## Week 3: Sync, retrieval, answering basics (T-015, T-016, T-030, T-031, T-042, T-002)
| Day | Do | Done when |
| --- | --- | --- |
| 11 | Test sync cases: edit page then re-sync (only it re-embeds); delete page (disappears); change group in access_map (updates without re-embed) (T-015) | All three behave |
| 12 | Break sync on purpose (wrong token). Confirm `sync_runs` shows failed and an alert fires (set ALERT_WEBHOOK_URL) (T-016). Schedule cron/Task Scheduler hourly | Failure alert received |
| 13 | Try 15 questions through hybrid_search; compare `USE_HYBRID=false` (T-030) | Good hits on 15 queries |
| 14 | Reranker on/off on hard questions (T-031). Verify old vs new page conflict handling with synthetic docs (T-042) | Rerank helps; conflicts flagged |
| 15 | Finish question list: 40 questions, 10 of them no-answer, with expected page URLs (T-002) | eval/questions.yaml has 40 items |

## Week 4: Answer quality and evaluation (T-032, T-040, T-041, T-044, T-050, T-051)
| Day | Do | Done when |
| --- | --- | --- |
| 16 | Run `answer_question` on 20 questions; check each claim has a valid citation (T-040) | Uncited answers become not found |
| 17 | `make calibrate` then set MIN_VECTOR_SIM in .env (T-041) | Off-topic refused, valid answered |
| 18 | Extend golden set to 60: 30 answerable with reference answers, 10 no-answer, 10 traps (T-050); second person reviews references | Set reviewed |
| 19 | `make eval` (T-051). Hand-score 10 answers; check LLM judge agrees (aim 8 of 10) | Scores run; judge validated |
| 20 | Tune chunk size/top-k against hit rate (T-032); add 5 prompt-injection documents to synthetic seed and re-run (T-044) | Baseline and tuned numbers saved |

## Week 5: Interface, logs, security, variants (T-052, T-054, T-060, T-061, T-062, T-063, T-070)
| Day | Do | Done when |
| --- | --- | --- |
| 21 | `make api`; test /ask with curl; check 401, 403, 429 behaviour (T-060) | API tests pass |
| 22 | `make ui`; ask 10 questions as 3 different users; check citations, dates, feedback (T-061) | Someone else can use it unaided |
| 23 | Confirm every request is in query_log; set retention (`make purge`); open the dashboard (T-062, T-063) | Logs and dashboard work |
| 24 | Security pack: rephrasing, "ignore your rules", cross-project, code-listing attacks, 20 total; review returned_doc_ids (T-070) | 100% blocked |
| 25 | `make compare` for the variants table (T-052). T-054 (Bedrock KB benchmark) is deferred until a company cloud account exists | Results table exists |

## Week 6: Pilot A and gate (T-090)
| Day | Do | Done when |
| --- | --- | --- |
| 26 | Import 5-10 pilot users with `scripts/import_users.py` (groups reviewed by data owner); send docs/pilot_note.md | Users asking real questions |
| 27 | Watch dashboard; tag failures: `update query_log set failure_tag='missing_doc' where id=...` | Failure tags set |
| 28 | Fix the top 3 issues; re-run `make eval` and `make itest` | No regressions |
| 29 | Fill docs/stage1_gate_report_template.md with real numbers; export dashboard screenshots | Report drafted |
| 30 | Demo using docs/demo_script.md; decision at Gate 1 | Go / no-go recorded |

## Gate 1 targets
100% access and injection tests; hit@5 at least 80%; correctness at least 75%; citation accuracy at least 85%; correct not-found at least 85%; pilot thumbs-up at least 60%; at least half of pilot users return on a second day. Adjust the thresholds with your manager before week 1 ends.
