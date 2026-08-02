-- NF-EXECUTIVE-MESH-V1 — executive run SSOT tables (portfolio-spine)
-- Canonical authority for Executive Mesh. Durable Object is coordinator cache only.

CREATE TABLE IF NOT EXISTS canonical_state_versions (
  organization_id TEXT NOT NULL DEFAULT 'sourcea',
  state_version BIGINT NOT NULL,
  state_hash TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (organization_id)
);

CREATE TABLE IF NOT EXISTS executive_runs (
  run_id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL DEFAULT 'sourcea',
  correlation_id TEXT NOT NULL,
  causation_id TEXT,
  idempotency_key TEXT NOT NULL,
  snapshot_version BIGINT NOT NULL,
  status TEXT NOT NULL,
  event_type TEXT NOT NULL,
  decision_class TEXT,
  goal_id TEXT,
  terminal TEXT,
  digest_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (organization_id, idempotency_key)
);

CREATE TABLE IF NOT EXISTS role_runs (
  role_run_id TEXT PRIMARY KEY,
  executive_run_id TEXT NOT NULL REFERENCES executive_runs(run_id),
  role TEXT NOT NULL,
  blueprint_version TEXT NOT NULL,
  deliberation_level TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS role_decision_packets (
  packet_id TEXT PRIMARY KEY,
  role_run_id TEXT NOT NULL REFERENCES role_runs(role_run_id),
  executive_run_id TEXT NOT NULL REFERENCES executive_runs(run_id),
  snapshot_version BIGINT NOT NULL,
  conclusion TEXT NOT NULL,
  packet_hash TEXT NOT NULL,
  body_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mesh_decisions (
  decision_id TEXT PRIMARY KEY,
  executive_run_id TEXT NOT NULL REFERENCES executive_runs(run_id),
  zone TEXT NOT NULL,
  status TEXT NOT NULL,
  policy_version TEXT,
  decision_hash TEXT NOT NULL,
  body_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mesh_commitments (
  commitment_id TEXT PRIMARY KEY,
  executive_run_id TEXT NOT NULL REFERENCES executive_runs(run_id),
  decision_id TEXT NOT NULL,
  required_artifact TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mesh_work_packets (
  action_id TEXT PRIMARY KEY,
  executive_run_id TEXT NOT NULL REFERENCES executive_runs(run_id),
  decision_id TEXT NOT NULL,
  executor_class TEXT NOT NULL,
  status TEXT NOT NULL,
  body_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mesh_evidence_receipts (
  evidence_id TEXT PRIMARY KEY,
  executive_run_id TEXT NOT NULL REFERENCES executive_runs(run_id),
  work_packet_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  valid BOOLEAN NOT NULL,
  detail TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mesh_outbox_events (
  outbox_id TEXT PRIMARY KEY,
  executive_run_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json JSONB NOT NULL,
  payload_hash TEXT NOT NULL,
  delivered BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE canonical_state_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE executive_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_decision_packets ENABLE ROW LEVEL SECURITY;
ALTER TABLE mesh_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE mesh_commitments ENABLE ROW LEVEL SECURITY;
ALTER TABLE mesh_work_packets ENABLE ROW LEVEL SECURITY;
ALTER TABLE mesh_evidence_receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE mesh_outbox_events ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
  CREATE POLICY executive_runs_public_read ON executive_runs FOR SELECT USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY mesh_decisions_public_read ON mesh_decisions FOR SELECT USING (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
