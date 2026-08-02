-- NF-SOURCEA-N8N-ORCHESTRATOR-V1 — activation truth for Git-defined nodes/graphs
-- Does NOT replace executive_*/memory/evidence tables. graph_runs already exists (016).

CREATE TABLE IF NOT EXISTS node_registry (
  node_id TEXT NOT NULL,
  version TEXT NOT NULL,
  spec_hash TEXT NOT NULL,
  git_commit TEXT NOT NULL,
  runtime_kind TEXT NOT NULL CHECK (runtime_kind IN (
    'DETERMINISTIC', 'MODEL', 'EXECUTOR', 'GATE', 'SUBGRAPH'
  )),
  control_mode TEXT NOT NULL DEFAULT 'SINGLE' CHECK (control_mode IN (
    'SINGLE', 'MAP', 'FANOUT', 'JOIN', 'LOOP'
  )),
  status TEXT NOT NULL DEFAULT 'CANDIDATE' CHECK (status IN (
    'CANDIDATE', 'ACTIVE', 'RETIRED'
  )),
  spec_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  activated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (node_id, version)
);

CREATE UNIQUE INDEX IF NOT EXISTS node_registry_one_active
  ON node_registry (node_id)
  WHERE status = 'ACTIVE';

CREATE TABLE IF NOT EXISTS graph_registry (
  graph_id TEXT NOT NULL,
  version TEXT NOT NULL,
  graph_hash TEXT NOT NULL,
  git_commit TEXT NOT NULL,
  n8n_workflow_id TEXT,
  status TEXT NOT NULL DEFAULT 'CANDIDATE' CHECK (status IN (
    'CANDIDATE', 'ACTIVE', 'RETIRED'
  )),
  definition_ref TEXT NOT NULL,
  activated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (graph_id, version)
);

CREATE UNIQUE INDEX IF NOT EXISTS graph_registry_one_active
  ON graph_registry (graph_id)
  WHERE status = 'ACTIVE';

-- node_runs: per-step execution truth (refs only). graph_runs remains the run header.
CREATE TABLE IF NOT EXISTS node_runs (
  node_run_id TEXT PRIMARY KEY,
  graph_run_id TEXT NOT NULL REFERENCES graph_runs(run_id),
  node_id TEXT NOT NULL,
  node_version TEXT,
  status TEXT NOT NULL,
  envelope_ref TEXT,
  content_hash TEXT,
  usage_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS node_runs_graph_run_idx ON node_runs (graph_run_id);

COMMENT ON TABLE node_registry IS 'Activation truth for NodeSpecs (Git defines; Supabase activates)';
COMMENT ON TABLE graph_registry IS 'Activation truth for GraphSpecs / n8n workflow pointers';
COMMENT ON TABLE node_runs IS 'Execution truth step ledger — refs + hashes + usage only';
