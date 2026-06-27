-- Cloud Forge Run — per-plan shipped rows (portfolio-spine · WitnessBC competitive registry)
-- Saved: 2026-06-24T09:45:00Z
-- Apply: supabase db push (portfolio-spine) — founder/CI or scripts/apply_cloud_forge_run_supabase_migration_v1.py

CREATE TABLE IF NOT EXISTS public.cloud_forge_run_rows (
  plan_id TEXT PRIMARY KEY,
  status TEXT NOT NULL CHECK (status IN ('PASS', 'FAIL')),
  validator_result TEXT,
  evidence_source TEXT,
  proof_tier TEXT,
  sellable BOOLEAN NOT NULL DEFAULT false,
  maps_registry TEXT,
  workstream TEXT,
  competitor TEXT,
  source_url TEXT,
  http_status INTEGER,
  artifact_path TEXT NOT NULL,
  dispatch_receipt_url TEXT,
  evidence_snippets JSONB NOT NULL DEFAULT '[]'::jsonb,
  artifact JSONB,
  shipped_at TIMESTAMPTZ NOT NULL,
  batch_id INTEGER,
  trigger_source TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cloud_forge_run_rows_shipped_at
  ON public.cloud_forge_run_rows (shipped_at DESC);

CREATE INDEX IF NOT EXISTS idx_cloud_forge_run_rows_proof_tier
  ON public.cloud_forge_run_rows (proof_tier, shipped_at DESC);

CREATE INDEX IF NOT EXISTS idx_cloud_forge_run_rows_maps_registry
  ON public.cloud_forge_run_rows (maps_registry);

ALTER TABLE public.cloud_forge_run_rows ENABLE ROW LEVEL SECURITY;

CREATE POLICY cloud_forge_run_rows_public_read ON public.cloud_forge_run_rows
  FOR SELECT
  USING (true);

COMMENT ON TABLE public.cloud_forge_run_rows IS
  'Cloud Forge Run autorun — one row per shipped plan_id; INSERT via service_role on Railway only';

NOTIFY pgrst, 'reload schema';
