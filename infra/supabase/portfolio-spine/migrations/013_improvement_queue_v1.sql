-- Migration 0013 — improvement_queue (Kaizen) + nerve probe receipts + nf intake
-- Saved: 2026-07-05T16:05:00Z

CREATE TABLE IF NOT EXISTS public.improvement_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finding TEXT NOT NULL,
  source TEXT NOT NULL,
  expected_roi NUMERIC(12, 4),
  machine_safe BOOLEAN NOT NULL DEFAULT false,
  status TEXT NOT NULL DEFAULT 'open' CHECK (
    status IN ('open', 'in_progress', 'done', 'wont_fix', 'founder_gated')
  )
);

CREATE INDEX IF NOT EXISTS idx_improvement_queue_status_roi
  ON public.improvement_queue (status, expected_roi DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_improvement_queue_source
  ON public.improvement_queue (source, created_at DESC);

CREATE TABLE IF NOT EXISTS public.nf_intake_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  intake_id TEXT NOT NULL UNIQUE,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  channel TEXT NOT NULL DEFAULT 'cloudflare_worker',
  probe BOOLEAN NOT NULL DEFAULT false,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  telegram_notified BOOLEAN NOT NULL DEFAULT false,
  telegram_message_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_nf_intake_submissions_probe_recorded
  ON public.nf_intake_submissions (probe, recorded_at DESC);

CREATE TABLE IF NOT EXISTS public.nerve_probe_receipts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  run_id TEXT NOT NULL,
  probe_id TEXT NOT NULL,
  verdict TEXT NOT NULL CHECK (verdict IN ('PASS', 'FAIL')),
  execution_plane TEXT NOT NULL DEFAULT 'cloudflare_cron',
  evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
  telegram_sent BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_nerve_probe_receipts_run
  ON public.nerve_probe_receipts (run_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_nerve_probe_receipts_probe_verdict
  ON public.nerve_probe_receipts (probe_id, verdict, recorded_at DESC);

ALTER TABLE public.improvement_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nf_intake_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nerve_probe_receipts ENABLE ROW LEVEL SECURITY;

CREATE POLICY improvement_queue_public_read ON public.improvement_queue
  FOR SELECT USING (true);

CREATE POLICY nf_intake_submissions_public_read ON public.nf_intake_submissions
  FOR SELECT USING (true);

CREATE POLICY nerve_probe_receipts_public_read ON public.nerve_probe_receipts
  FOR SELECT USING (true);

COMMENT ON TABLE public.improvement_queue IS
  'Kaizen backlog — finding, source, expected_roi, machine_safe flag, status';
COMMENT ON TABLE public.nf_intake_submissions IS
  'Noetfield intelligence intake + probe rows — nf_intake_e2e read-back target';
COMMENT ON TABLE public.nerve_probe_receipts IS
  'Nerve probe cycle receipts — written by noetfield-nerve-probe-v1 CF worker';
