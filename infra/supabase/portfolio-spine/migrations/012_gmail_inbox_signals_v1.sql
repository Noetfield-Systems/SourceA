-- Migration 0012 — Gmail inbox signals (sweep + triage queue)
-- Saved: 2026-07-05T16:35:00Z

CREATE TABLE IF NOT EXISTS public.gmail_inbox_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  gmail_message_id TEXT NOT NULL,
  mailbox TEXT NOT NULL,
  thread_id TEXT,
  subject TEXT,
  from_addr TEXT,
  snippet TEXT,
  body_text TEXT,
  received_at TIMESTAMPTZ,
  swept_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  sweep_source TEXT NOT NULL DEFAULT 'gmail_api',
  processed BOOLEAN NOT NULL DEFAULT false,
  triage_at TIMESTAMPTZ,
  triage_verdict TEXT CHECK (
    triage_verdict IS NULL OR triage_verdict IN ('PASS', 'FAIL', 'ROUTE', 'MONITOR', 'ARCHIVE', 'DEFER')
  ),
  signal_factory_decision TEXT,
  signal_factory_classification TEXT,
  triage_report JSONB NOT NULL DEFAULT '{}'::jsonb,
  telegram_notified BOOLEAN NOT NULL DEFAULT false,
  UNIQUE (gmail_message_id, mailbox)
);

CREATE INDEX IF NOT EXISTS idx_gmail_inbox_signals_unprocessed
  ON public.gmail_inbox_signals (processed, swept_at DESC)
  WHERE processed = false;

CREATE INDEX IF NOT EXISTS idx_gmail_inbox_signals_mailbox_swept
  ON public.gmail_inbox_signals (mailbox, swept_at DESC);

ALTER TABLE public.gmail_inbox_signals ENABLE ROW LEVEL SECURITY;

CREATE POLICY gmail_inbox_signals_public_read ON public.gmail_inbox_signals
  FOR SELECT USING (true);

COMMENT ON TABLE public.gmail_inbox_signals IS
  'Gmail sweep rows — unprocessed until Signal Factory triage + Telegram verdict';
