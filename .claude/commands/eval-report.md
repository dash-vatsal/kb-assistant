---
description: Run the golden-set eval and compare with Gate 1 targets
---
Run `make eval`. Summarise the metrics against the Gate 1 targets in `docs/STAGE1_EXECUTION_PLAN.md` (hit@5 at least 80%, correctness 75%, citations 85%, not-found 85%, traps 100%). List every failed question from `eval/results.csv` with a guess at the cause: missing document, retrieval miss, bad answer, bad citation or permission. Propose at most three fixes ordered by expected gain. Do not change thresholds or the golden set.
