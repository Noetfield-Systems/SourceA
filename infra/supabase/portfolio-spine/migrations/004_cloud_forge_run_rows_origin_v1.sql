-- Cloud Forge Run row provenance — mac_replay vs railway-native sink
-- Saved: 2026-07-02T07:15:00Z

ALTER TABLE public.cloud_forge_run_rows
  ADD COLUMN IF NOT EXISTS origin TEXT;

CREATE INDEX IF NOT EXISTS idx_cloud_forge_run_rows_origin
  ON public.cloud_forge_run_rows (origin, batch_id);

COMMENT ON COLUMN public.cloud_forge_run_rows.origin IS
  'Provenance: railway | mac_replay | null — sink invariant uses railway_count + mac_replay_count';

NOTIFY pgrst, 'reload schema';
