# Data handling decision (T-006), complete in week 1
- Sources indexed in stage 1 (non-client only): ________  approved by: ________ on ________
- Where data lives: local Postgres (laptop/dev VM) during stage 1; no copies outside company-controlled machines. Disk encryption on: yes / no
- Model processing: fully local (Ollama in Docker or desktop app on this machine); no document text is sent to any external service. Models: bge-m3 (embeddings), ________ (answers)
- Logs: stored in `query_log` (questions and answers are confidential). Retention ____ days (`make purge`). Readable by: ________
- Pilot users informed that queries are logged: yes / no (use docs/pilot_note.md)
- What must never be indexed: client-NDA projects without written data-owner approval; PHI; credentials/secrets pages
- If sensitive content is found in an indexed page: remove via access map, run sync (deletes it), tell the data owner, note it in the gate report
