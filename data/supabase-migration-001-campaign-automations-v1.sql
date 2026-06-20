-- SourceA video-ad factory — campaign schema v1
-- SSOT: data/supabase-migration-001-campaign-automations-v1.sql
-- Apply: supabase db push (when WORK names project)
-- Saved: 2026-06-19T06:40:50Z

-- profiles — multi-tenant + StoreKit hook (Phase 2)
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE,
  tier TEXT NOT NULL DEFAULT 'BRONZE' CHECK (tier IN ('BRONZE', 'GOLD', 'PLATINUM', 'MARKET_READY')),
  credits_remaining INT NOT NULL DEFAULT 0,
  storekit_original_transaction_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- campaign_automations — brief → render loop
CREATE TABLE IF NOT EXISTS campaign_automations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  creator_id UUID NOT NULL REFERENCES profiles(id),
  raw_brief TEXT NOT NULL,
  refined_script TEXT,
  voice_clone_id TEXT,
  video_prompt_loop JSONB,
  current_step TEXT NOT NULL DEFAULT 'BRIEF_ANALYSIS' CHECK (
    current_step IN (
      'BRIEF_ANALYSIS',
      'AUDIO_READY',
      'VIDEO_RENDERING',
      'HUMAN_APPROVAL_REQUIRED',
      'DISPATCHED'
    )
  ),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_campaign_automations_creator ON campaign_automations(creator_id);
CREATE INDEX IF NOT EXISTS idx_campaign_automations_step ON campaign_automations(current_step);

-- resource_logs — API cost telemetry (Phase 3 analytics)
CREATE TABLE IF NOT EXISTS resource_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID REFERENCES campaign_automations(id),
  provider TEXT NOT NULL,
  operation TEXT NOT NULL,
  units NUMERIC,
  cost_usd NUMERIC(12, 4),
  receipt JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_resource_logs_campaign ON resource_logs(campaign_id);

-- Storage bucket policy placeholder (apply in Supabase dashboard)
-- generated_assets_bucket — campaigns/{id}/voice_narration.mp3
