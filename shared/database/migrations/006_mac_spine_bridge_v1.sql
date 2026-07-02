-- Mirror: infra/supabase/portfolio-spine/migrations/006_mac_spine_bridge_v1.sql

CREATE TABLE IF NOT EXISTS public.mac_agent_heartbeat (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL,
  repo TEXT NOT NULL,
  sha TEXT NOT NULL,
  dirty_count INTEGER NOT NULL DEFAULT 0 CHECK (dirty_count >= 0),
  at TIMESTAMPTZ NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_mac_agent_heartbeat_agent_at
  ON public.mac_agent_heartbeat (agent_id, at DESC);
CREATE INDEX IF NOT EXISTS idx_mac_agent_heartbeat_recorded
  ON public.mac_agent_heartbeat (recorded_at DESC);

ALTER TABLE public.mac_agent_heartbeat ENABLE ROW LEVEL SECURITY;

CREATE POLICY mac_agent_heartbeat_public_read ON public.mac_agent_heartbeat
  FOR SELECT
  USING (true);

CREATE TABLE IF NOT EXISTS public.worker_inbox (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status TEXT NOT NULL CHECK (
    status IN ('pending', 'delivered', 'acked', 'founder_blocked', 'cleared')
  ),
  lane TEXT NOT NULL DEFAULT 'sourcea_worker',
  source TEXT NOT NULL DEFAULT 'hub',
  prompt TEXT NOT NULL DEFAULT '',
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  sa_id TEXT,
  queue_pos INTEGER,
  queue_total INTEGER,
  queue_role TEXT,
  mission_id TEXT,
  founder_blocked BOOLEAN NOT NULL DEFAULT false,
  delivered_at TIMESTAMPTZ,
  acked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  op_key TEXT UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_worker_inbox_status_created
  ON public.worker_inbox (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_worker_inbox_sa_id
  ON public.worker_inbox (sa_id);
CREATE INDEX IF NOT EXISTS idx_worker_inbox_founder_blocked
  ON public.worker_inbox (founder_blocked, created_at DESC)
  WHERE founder_blocked = true;

ALTER TABLE public.worker_inbox ENABLE ROW LEVEL SECURITY;

CREATE POLICY worker_inbox_public_read ON public.worker_inbox
  FOR SELECT
  USING (true);

ALTER TABLE public.truth_log DROP CONSTRAINT IF EXISTS truth_log_source_check;
ALTER TABLE public.truth_log ADD CONSTRAINT truth_log_source_check CHECK (
  source IN (
    'cloudflare_cron',
    'cloudflare_worker',
    'railway_runtime',
    'github_actions',
    'mac_agent'
  )
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
    'FOUNDER_PROOF_15_FAIL',
    'MAC_AGENT_HEARTBEAT',
    'MAC_FRESH_MAIN_SYNC',
    'MAC_RECEIPT_MIRROR',
    'MAC_SESSION_GATE'
  )
);

CREATE INDEX IF NOT EXISTS idx_truth_log_mac_agent
  ON public.truth_log (source, event, recorded_at DESC)
  WHERE source = 'mac_agent';
