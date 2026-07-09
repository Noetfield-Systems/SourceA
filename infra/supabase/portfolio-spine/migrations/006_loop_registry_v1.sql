-- loop_registry — dead-man liveness for 24/7 CF motors (portfolio-spine)
-- Saved: 2026-07-06T06:55:00Z

CREATE TABLE IF NOT EXISTS public.loop_registry (
  loop_id TEXT PRIMARY KEY,
  trigger_host TEXT NOT NULL,
  schedule_cron TEXT,
  interval_minutes INTEGER NOT NULL CHECK (interval_minutes > 0),
  last_fired_at TIMESTAMPTZ,
  last_ok BOOLEAN,
  last_error TEXT,
  last_receipt JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_loop_registry_last_fired
  ON public.loop_registry (last_fired_at DESC NULLS LAST);

ALTER TABLE public.loop_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY loop_registry_public_read ON public.loop_registry
  FOR SELECT USING (true);

COMMENT ON TABLE public.loop_registry IS
  'Scheduled loop liveness — deadman checks stale rows (2x interval). Service role upserts from CF workers.';
