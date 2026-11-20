CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY,
  name TEXT,
  email TEXT UNIQUE,
  groups TEXT[] NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS documents (
  doc_id TEXT PRIMARY KEY,           -- e.g. confluence:12345, jira:ALPHA-42
  source TEXT NOT NULL,
  container TEXT NOT NULL,           -- space key / project key / folder
  title TEXT,
  url TEXT,
  owner TEXT,
  last_updated TIMESTAMPTZ,
  content_hash TEXT NOT NULL,
  access_groups TEXT[] NOT NULL,
  synced_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
  chunk_id BIGSERIAL PRIMARY KEY,
  doc_id TEXT NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
  ord INT NOT NULL,
  heading_path TEXT,
  text TEXT NOT NULL,
  embedding vector(1024) NOT NULL,
  access_groups TEXT[] NOT NULL,     -- denormalised so the filter is one WHERE clause
  tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED
);
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING GIN (tsv);
CREATE INDEX IF NOT EXISTS chunks_acl_idx ON chunks USING GIN (access_groups);
CREATE INDEX IF NOT EXISTS chunks_emb_idx ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS query_log (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ DEFAULT now(),
  user_id TEXT,
  question TEXT,
  returned_chunk_ids BIGINT[],
  returned_doc_ids TEXT[],
  answer TEXT,
  found BOOLEAN,
  latency_ms INT,
  failure_tag TEXT                   -- Day 28: missing_doc | retrieval | answer | permission
);

CREATE TABLE IF NOT EXISTS feedback (
  id BIGSERIAL PRIMARY KEY,
  query_id BIGINT REFERENCES query_log(id),
  rating INT NOT NULL,               -- 1 = up, -1 = down
  comment TEXT,
  ts TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sync_runs (
  id BIGSERIAL PRIMARY KEY,
  source TEXT NOT NULL,
  container TEXT NOT NULL,
  started_at TIMESTAMPTZ DEFAULT now(),
  finished_at TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'running',   -- running | ok | failed
  stats JSONB,
  error TEXT
);
