---
description: Verify a task, update the board, propose a commit
argument-hint: T-010
---
Task: $ARGUMENTS

1. Run `make test` (and `make itest` if the task touches access control, retrieval, answering or ingestion and the database is up). Run `ruff check kb scripts eval tests --select E9,F63,F7,F82`.
2. Use the `security-reviewer` subagent on the current `git diff`. Report every finding; fix high ones.
3. Check each line of "Done when" in `docs/tasks/$ARGUMENTS.md` and say pass/fail with evidence (test names, command output).
4. If all pass: tick the task in `TASKS.md` and write a one-line note of what changed. If not, list what is left.
5. Propose a commit message beginning with `$ARGUMENTS:`. Do not push.
