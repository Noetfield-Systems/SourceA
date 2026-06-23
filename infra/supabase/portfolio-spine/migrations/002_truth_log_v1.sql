-- Truth Layer v2 — independent TRUTH_LOG (cloud writers only · Cursor cannot insert)
-- Saved: 2026-06-22T22:15:00Z
-- Apply: supabase db push (portfolio-spine) — founder/CI only

CREATE TABLE IF NOT EXISTS public.truth_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  source TEXT NOT NULL CHECK (
    source IN ('cloudflare_cron', 'cloudflare_worker', 'railway_runtime')
  ),
  event TEXT NOT NULL CHECK (
    event IN (
      'CRON_FIRED',
      'JOB_STARTED',
      'JOB_COMPLETED',
      'JOB_FAILED',
      'QUEUE_ADVANCED'
    )
  ),
  deployment_id TEXT,
  queue_head TEXT,
  old_queue_head TEXT,
  receipt_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_truth_log_recorded_at ON public.truth_log (recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_truth_log_event_recorded ON public.truth_log (event, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_truth_log_source_recorded ON public.truth_log (source, recorded_at DESC);

ALTER TABLE public.truth_log ENABLE ROW LEVEL SECURITY;

-- Read-only for dashboard / /truth observers (insert blocked — service_role only)
CREATE POLICY truth_log_public_read ON public.truth_log
  FOR SELECT
  USING (true);

COMMENT ON TABLE public.truth_log IS
  'Independent autonomy verifier — INSERT via service_role on Railway/CF only; Mac/Cursor blocked by RLS';
