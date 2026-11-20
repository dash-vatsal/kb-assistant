---
description: Read a task spec and propose a plan (no code yet)
argument-hint: T-010
---
Task: $ARGUMENTS

1. Read `CLAUDE.md`, `docs/tasks/$ARGUMENTS.md`, and the requirement IDs it lists in `docs/frd.md`.
2. Read only the files the task lists under "Files". Check the current state of the starter code against the task's "Done when".
3. Reply with a short plan: what already exists, what is missing, files to change, the tests you will write first (name each test), risks to access control, and anything that needs a human decision.
4. Do NOT write or change code yet. End by asking me to approve the plan.
