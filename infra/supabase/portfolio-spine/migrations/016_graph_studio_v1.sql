-- NF-GRAPH-STUDIO-V1 — blueprint / plan / run SSOT (portfolio-spine)
-- Layout is stored separately from semantic graph. Compiled plans are immutable by plan_hash.

CREATE TABLE IF NOT EXISTS graph_node_manifests (
  kind TEXT NOT NULL,
  version TEXT NOT NULL,
  manifest_json JSONB NOT NULL,
  manifest_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (kind, version)
);

CREATE TABLE IF NOT EXISTS graph_blueprints (
  org TEXT NOT NULL DEFAULT 'sourcea',
  blueprint_id TEXT NOT NULL,
  version TEXT NOT NULL,
  title TEXT NOT NULL,
  graph_json JSONB NOT NULL,
  layout_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (org, blueprint_id, version)
);

CREATE TABLE IF NOT EXISTS graph_compiled_plans (
  plan_hash TEXT PRIMARY KEY,
  blueprint_id TEXT NOT NULL,
  blueprint_version TEXT NOT NULL,
  plan_json JSONB NOT NULL,
  frozen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  immutable BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS graph_runs (
  run_id TEXT PRIMARY KEY,
  org TEXT NOT NULL DEFAULT 'sourcea',
  plan_hash TEXT NOT NULL REFERENCES graph_compiled_plans(plan_hash),
  mesh_run_id TEXT,
  status TEXT NOT NULL,
  terminal TEXT,
  run_graph_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  event_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS graph_runs_plan_hash_idx ON graph_runs (plan_hash);
CREATE INDEX IF NOT EXISTS graph_runs_mesh_run_id_idx ON graph_runs (mesh_run_id);
CREATE INDEX IF NOT EXISTS graph_compiled_plans_blueprint_idx ON graph_compiled_plans (blueprint_id, blueprint_version);

COMMENT ON TABLE graph_compiled_plans IS 'Immutable compiled execution plans keyed by plan_hash (NF-GRAPH-STUDIO-V1)';
COMMENT ON COLUMN graph_blueprints.layout_json IS 'Studio-only layout; never enters plan_hash';
COMMENT ON COLUMN graph_blueprints.graph_json IS 'Semantic Blueprint Graph only';
