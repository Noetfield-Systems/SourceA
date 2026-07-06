-- Migration 0014 — workflow_census (judging layer · advisor WORKFLOW_CENSUS_v1)
-- Saved: 2026-07-06T10:00:00Z

CREATE TABLE IF NOT EXISTS public.workflow_census (
  loop_key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  trigger_host TEXT NOT NULL,
  schedule_cron TEXT,
  invocations_per_day NUMERIC(12, 4),
  cost_usd_monthly NUMERIC(12, 4),
  last_receipt_at TIMESTAMPTZ,
  last_receipt_kind TEXT,
  last_receipt_ref JSONB NOT NULL DEFAULT '{}'::jsonb,
  value_class TEXT NOT NULL CHECK (
    value_class IN ('REVENUE', 'GUARD', 'META', 'NONE')
  ),
  receipt_named BOOLEAN NOT NULL DEFAULT false,
  audit_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
  census_run_id TEXT NOT NULL,
  census_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_workflow_census_value_class
  ON public.workflow_census (value_class, census_at DESC);

CREATE INDEX IF NOT EXISTS idx_workflow_census_run
  ON public.workflow_census (census_run_id, census_at DESC);

ALTER TABLE public.workflow_census ENABLE ROW LEVEL SECURITY;

CREATE POLICY workflow_census_public_read ON public.workflow_census
  FOR SELECT USING (true);

COMMENT ON TABLE public.workflow_census IS
  'Weekly loop census — name, host, schedule, invocations, cost, last receipt, value_class (REVENUE/GUARD/META/NONE)';
