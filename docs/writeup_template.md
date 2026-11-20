# Internal Knowledge Assistant: POC write-up
1. Summary and recommendation
2. Scope and approvals
3. Architecture (diagram) and why access control is enforced in retrieval
4. Evaluation: test set, metrics table, variant comparison (rerank on/off, hybrid vs vector, chunk sizes)
5. Security testing: traps run, pass rate, prompt-injection tests, findings and fixes
6. Pilot results: users, queries, ratings, repeat usage, failure categories
7. Documentation gaps: top unanswered questions
8. Build vs buy: custom core vs Bedrock Knowledge Bases (see comparison)
9. Cost: Bedrock tokens per query, hosting, ops effort; projected at 200 users
10. Risks, limits, and recommended next steps (SSO, IdP group sync, more sources, bot rollout)
