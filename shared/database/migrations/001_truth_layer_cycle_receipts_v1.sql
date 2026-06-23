-- Truth Layer Loop v1 — mirror of infra/supabase/portfolio-spine/migrations/001_truth_layer_cycle_receipts_v1.sql
-- Saved: 2026-06-22T19:45:00Z

CREATE TABLE IF NOT EXISTS public.cycle_receipts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cycle_id TEXT NOT NULL UNIQUE,
  execution_id TEXT NOT NULL,
  queue_head_before TEXT NOT NULL,
  queue_head_after TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ NOT NULL,
  duration_ms INTEGER NOT NULL CHECK (duration_ms >= 0),
  trigger_source TEXT NOT NULL DEFAULT 'unknown',
  verdict TEXT NOT NULL CHECK (verdict IN ('GREEN', 'FAIL')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cycle_receipts_created_at ON public.cycle_receipts (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cycle_receipts_execution_id ON public.cycle_receipts (execution_id);
CREATE INDEX IF NOT EXISTS idx_cycle_receipts_verdict_created ON public.cycle_receipts (verdict, created_at DESC);

ALTER TABLE public.cycle_receipts ENABLE ROW LEVEL SECURITY;
