-- Truth Layer v2.1 — GitHub Actions external verify + founder proof receipts
-- Saved: 2026-07-02T12:30:00Z

ALTER TABLE public.truth_log
  ADD COLUMN IF NOT EXISTS payload JSONB;

ALTER TABLE public.truth_log DROP CONSTRAINT IF EXISTS truth_log_source_check;
ALTER TABLE public.truth_log ADD CONSTRAINT truth_log_source_check CHECK (
  source IN ('cloudflare_cron', 'cloudflare_worker', 'railway_runtime', 'github_actions')
);

ALTER TABLE public.truth_log DROP CONSTRAINT IF EXISTS truth_log_event_check;
ALTER TABLE public.truth_log ADD CONSTRAINT truth_log_event_check CHECK (
  event IN (
    'CRON_FIRED',
    'JOB_STARTED',
    'JOB_COMPLETED',
    'JOB_FAILED',
    'QUEUE_ADVANCED',
    'EXTERNAL_VERIFY_PASS',
    'EXTERNAL_VERIFY_FAIL',
    'FOUNDER_PROOF_15_PASS',
    'FOUNDER_PROOF_15_FAIL'
  )
);

CREATE INDEX IF NOT EXISTS idx_truth_log_payload_gin ON public.truth_log USING gin (payload);
CREATE INDEX IF NOT EXISTS idx_truth_log_github_run ON public.truth_log ((payload->>'github_run_id'));

COMMENT ON COLUMN public.truth_log.payload IS
  'External verify / founder-proof receipt JSON — written by github_actions source only';
