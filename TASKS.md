# Task board

Tick a task only after `/finish-task`. Stage 1 order follows docs/STAGE1_EXECUTION_PLAN.md. Specs: `docs/tasks/T-xxx.md`.

## Stage 1, week 1
- [ ] **T-001** Write scope; pick pilot group; get data-owner and security approval  (Foundations, 2d)
- [ ] **T-003** Local model setup: Ollama running, models pulled, smoke test passes  (Foundations, 1d)
- [ ] **T-004** Repo, branching, CI (lint, unit tests), dev/stage/prod environments  (Foundations, 3d)
- [ ] **T-006** Decide log retention, data classification and who can read logs  (Foundations, 1d)
- [ ] **T-012** Access map and default-deny guard in ingestion  (Ingestion, 2d)
- [ ] **T-020** Permission model; 5 synthetic users; canary documents  (Access, 2d)
- [ ] **T-002** Collect 30 real questions from users (golden set v0)  (Foundations, 2d)

## Stage 1, week 2
- [ ] **T-010** Confluence connector: pages, pagination, restrictions, structured text  (Ingestion, 3d)
- [ ] **T-011** Jira connector: issues, comments, resolution, token pagination  (Ingestion, 3d)
- [ ] **T-013** Heading-aware chunking with unit tests  (Ingestion, 2d)
- [ ] **T-014** Schema, migrations, embedding and indexing pipeline  (Ingestion, 3d)
- [ ] **T-021** ACL-filtered retrieval in SQL with integration tests  (Access, 3d)

## Stage 1, week 3
- [ ] **T-015** Incremental sync: hash skip, deletions, safe-delete guard, scheduler  (Ingestion, 4d)
- [ ] **T-016** Sync status, retries with backoff, failure alerts  (Ingestion, 2d)
- [ ] **T-030** Vector and keyword search with rank fusion  (Retrieval, 3d)
- [ ] **T-031** Reranker with safe fallback  (Retrieval, 2d)
- [ ] **T-042** Stale and conflicting source handling  (Answering, 2d)

## Stage 1, week 4
- [ ] **T-040** Grounded prompt, JSON output, server-side citation validation  (Answering, 3d)
- [ ] **T-041** Not-found logic (threshold plus sufficiency) and calibration  (Answering, 3d)
- [x] **T-044** Prompt-injection defenses and injection suite v1  (Answering, 3d)
  - Retrieved chunks are redacted before rerank and answering and escaped in the prompt; answers containing an image or an uncited URL/link return not-found; 4 new injection docs + traps.
- [ ] **T-050** Golden set v1: 60 questions incl. 10 no-answer and 10 traps  (Evaluation, 4d)
- [ ] **T-051** Eval runner, LLM judge, human calibration sample  (Evaluation, 4d)
- [ ] **T-032** Tune chunk size, top-k and thresholds on the golden set  (Retrieval, 4d)

## Stage 1, week 5
- [ ] **T-060** Backend API: ask, feedback, history; validation; rate limits  (Interface, 4d)
- [ ] **T-061** Web app: ask, answer, citations, feedback, history  (Interface, 6d)
- [ ] **T-062** Audit logging and retention job  (Interface, 3d)
- [ ] **T-063** Usage, quality and cost dashboard  (Interface, 3d)
- [ ] **T-070** Trap and extraction test pack (rephrasing, cross-project, code listing)  (Security, 3d)
- [ ] **T-052** Variant comparison: rerank, hybrid, chunk sizes  (Evaluation, 2d)
- [ ] **T-054** Benchmark managed option (Bedrock KB) on same corpus - deferred  (Evaluation, 3d)

## Stage 1, week 6
- [ ] **T-090** Pilot A: onboarding note, 5-10 users, feedback collection  (Pilot, 3d)

## Deferred: T-005 (infrastructure as code) - use docker-compose in stage 1
- [ ] **T-005** Infrastructure as code: network, Aurora PostgreSQL with pgvector, ECS, secrets

## Stage 2: hardened pilot
- [ ] **T-017** Webhook handlers for page and issue updates  (Ingestion, 3d)
- [ ] **T-018** SharePoint or Drive connector with docx and pdf parsing  (Ingestion, 5d)
- [ ] **T-022** SSO (OIDC) in API and web app  (Access, 4d)
- [ ] **T-023** Identity-provider group sync with cache; failure means deny  (Access, 4d)
- [ ] **T-024** Source permission sync (spaces, projects to groups) and ACL change propagation  (Access, 5d)
- [ ] **T-025** Admin access-map editing with approval and change history  (Access, 3d)
- [ ] **T-026** Per-source kill switch  (Access, 1d)
- [ ] **T-033** Follow-up question rewriting under the same permissions  (Retrieval, 3d)
- [ ] **T-043** Streaming, timeouts and graceful errors  (Answering, 3d)
- [ ] **T-053** CI quality gate on golden set and traps  (Evaluation, 3d)
- [ ] **T-064** Review queue with failure tags  (Interface, 3d)
- [ ] **T-065** Documentation-gap and staleness report  (Interface, 3d)
- [ ] **T-071** Threat-model workshop and actions  (Security, 2d)
- [ ] **T-072** Independent security review, pen test support, fixes  (Security, 6d)
- [ ] **T-073** Injection suite v2 (hidden text, role prefixes, link exfiltration)  (Security, 2d)
- [ ] **T-074** Least-privilege IAM, private endpoints, encryption review  (Security, 3d)
- [ ] **T-080** Observability: logs, metrics, traces, alarms  (Platform, 4d)
- [ ] **T-081** Backups, point-in-time restore, index rebuild procedure  (Platform, 3d)
- [ ] **T-082** Load and cost tests; token budgets  (Platform, 3d)
- [ ] **T-083** High availability, autoscaling, health checks  (Platform, 3d)
- [ ] **T-091** Pilot B: 30-50 users, weekly failure triage  (Pilot, 5d)
- [ ] **T-092** One-page business case from pilot data  (Pilot, 2d)

## Stage 3: production rollout
- [ ] **T-019** Duplicate and near-duplicate detection report  (Ingestion, 2d)
- [ ] **T-027** Monthly access report (groups, members, reachable sources)  (Access, 2d)
- [ ] **T-034** Filters by source, space and date  (Retrieval, 2d)
- [ ] **T-084** Runbook, on-call and support model  (Platform, 3d)
- [ ] **T-085** Disaster-recovery drill  (Platform, 1d)
- [ ] **T-093** Rollout plan, training and communications  (Pilot, 3d)
- [ ] **T-094** Go-live review and sign-offs  (Pilot, 2d)
- [ ] **T-100** Slack or Teams bot: identity mapping, threads, feedback  (Adoption, 6d)
- [ ] **T-101** Bot security review for shared channels  (Adoption, 2d)
- [ ] **T-102** Admin approval and app installation  (Adoption, 1d)
