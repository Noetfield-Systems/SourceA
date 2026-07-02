-- L17 session cost receipts — truth_log AGENT_SESSION_COST (mac_agent source)
-- Saved: 2026-07-02T22:30:00Z

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

COMMENT ON TABLE public.truth_log IS
  'Independent autonomy verifier — incl. L17 AGENT_SESSION_COST payload {agent_id,tier,model,tokens,usd_est,tasks}';
