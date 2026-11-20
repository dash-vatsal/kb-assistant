# Gate 1 report
Date: ____   Build/commit: ____   Corpus: ____ pages, ____ issues, ____ chunks

## Results (from `make eval`, same golden set)
| Metric | Target | Actual |
| --- | --- | --- |
| Access / trap tests (`make itest` and eval traps) | 100% | |
| Retrieval hit@5 | at least 80% | |
| Answer correctness | at least 75% | |
| Citation accuracy | at least 85% | |
| Correct not-found | at least 85% | |
| p95 latency | under 10 s | |
| Pilot users / queries / thumbs-up | 5-10 / ____ / at least 60% | |
| Repeat users (2+ days) | at least 50% | |

## Variants (`make compare`)
(paste table)

## Bedrock Knowledge Bases benchmark
hit@5 custom vs managed; permission-filter support; effort; cost.

## Failures by category (query_log.failure_tag)
missing_doc ____  retrieval ____  answer ____  permission ____

## Documentation gaps (top unanswered questions)
1.  2.  3.

## Security
Trap tests: ____ run, ____ passed. Injection tests: ____ run, ____ passed. Findings and fixes:

## Cost
Bedrock tokens per query: ____  Estimated monthly cost at 50 users: ____

## Recommendation
Go / No-go / Go with changes:
