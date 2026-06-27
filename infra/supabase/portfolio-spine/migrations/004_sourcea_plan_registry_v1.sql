-- SourceA plan registry — 7000+ / backlog rows reachable by cloud systems
-- Saved: 2026-06-27T10:24:00Z
-- Apply: portfolio-spine SQL editor or DDL credentials from ~/.sourcea-secrets/portfolio-spine-db.env

CREATE TABLE IF NOT EXISTS public.sourcea_plan_registry (
  plan_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT,
  tier TEXT,
  lane TEXT,
  phase TEXT,
  workstream TEXT,
  priority TEXT,
  priority_rank INTEGER,
  source_registry TEXT,
  source_schema TEXT,
  prompt_path TEXT,
  source_path TEXT,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  search_text TEXT GENERATED ALWAYS AS (
    coalesce(plan_id, '') || ' ' ||
    coalesce(title, '') || ' ' ||
    coalesce(lane, '') || ' ' ||
    coalesce(phase, '') || ' ' ||
    coalesce(workstream, '') || ' ' ||
    coalesce(priority, '')
  ) STORED,
  imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sourcea_plan_registry_status
  ON public.sourcea_plan_registry (status);

CREATE INDEX IF NOT EXISTS idx_sourcea_plan_registry_lane_status
  ON public.sourcea_plan_registry (lane, status);

CREATE INDEX IF NOT EXISTS idx_sourcea_plan_registry_priority_rank
  ON public.sourcea_plan_registry (priority_rank);

CREATE INDEX IF NOT EXISTS idx_sourcea_plan_registry_source_registry
  ON public.sourcea_plan_registry (source_registry);

ALTER TABLE public.sourcea_plan_registry ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS sourcea_plan_registry_public_read ON public.sourcea_plan_registry;
CREATE POLICY sourcea_plan_registry_public_read ON public.sourcea_plan_registry
  FOR SELECT
  USING (true);

COMMENT ON TABLE public.sourcea_plan_registry IS
  'SourceA plan registry rows imported from disk SSOTs; writes are server/cloud only, reads are public-safe.';

NOTIFY pgrst, 'reload schema';
