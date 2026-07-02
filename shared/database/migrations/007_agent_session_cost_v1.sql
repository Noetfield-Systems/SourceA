-- Mirror: infra/supabase/portfolio-spine/migrations/007_agent_session_cost_v1.sql

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
    'FOUNDER_PROOF_15_FAIL',
    'MAC_AGENT_HEARTBEAT',
    'MAC_FRESH_MAIN_SYNC',
    'MAC_RECEIPT_MIRROR',
    'MAC_SESSION_GATE',
    'AGENT_SESSION_COST',
    'TIER_ESCALATION'
  )
);
