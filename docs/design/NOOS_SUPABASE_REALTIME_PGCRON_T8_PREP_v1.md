# NOOS — Supabase Realtime dashboard feed + pg_cron stale-lane detector (T8)

**Status:** FOUNDER_GATED prep — design only · NOOS repo implements  
**Saved at (UTC):** 2026-07-02T22:00:00Z  
**Spec ref:** NOETFIELD coherent system spec §1 T8 · §4 Supabase spine  
**Replaces (hand-rolled):** dashboard polling scripts · manual stale-lane founder glances · tribal “when did lane last tick?” knowledge

---

## T8 — Supabase-side nerve (gap today)

| Trigger ID | Kind | Target |
|---|---|---|
| NOOS-T8-pg-cron | schedule (pg_cron) | stale-lane detector inside portfolio-spine DB |
| NOOS-T8-realtime | event (Supabase Realtime) | dashboard read-only feed on truth_log + cycle receipts |

Register in NOOS `data/trigger-registry-v1.json` when implemented (L14 co-commit law).

---

## Architecture

```
portfolio-spine (Supabase)
  ├── truth_log / noetfield_truth_log  ──► Realtime channel: spine_events_v1
  ├── cycle receipts view              ──► Realtime channel: lane_cycles_v1
  └── pg_cron every 5m                 ──► stale_lane_nerve_v1()
            │
            ▼
      INSERT stale_lane_receipt
            │
            ▼
   Dashboard (read-only · STALE_DATA rule unchanged)
```

### Realtime feed (replaces polling)

- **Retired:** cron/JS interval fetching REST endpoints for dashboard tiles
- **Native:** Supabase Realtime `postgres_changes` on materialized lane status view
- **RLS:** dashboard service role read-only; no write via Realtime client

### pg_cron stale-lane detector (T8)

```sql
-- sketch only — NOOS migration lane
SELECT cron.schedule(
  'stale-lane-nerve-v1',
  '*/5 * * * *',
  $$SELECT noetfield_stale_lane_detect_v1()$$
);
```

Function logic:

1. For each lane in `autorun_lane_registry`, compare `max(receipt.at)` vs freshness window
2. If stale → insert `stale_lane_receipt` row (machine JSON, not prose)
3. If cross-lane stale pattern → optional `repository_dispatch` to NOOS motor (Phase 6 brain)

---

## Hand-rolled code retired

| Today | Platform-native |
|---|---|
| Dashboard fetch loop every N seconds | Supabase Realtime subscription |
| Agent “check if lane is stale” manual scripts | pg_cron `stale_lane_nerve_v1` receipt |
| Missing T8 in trigger registry | `NOOS-T8-pg-cron` + Realtime hook registered (L14) |

---

## NOOS deliverables (next Worker cycle — not SourceA code)

1. Migration: `infra/supabase/portfolio-spine/migrations/00X_stale_lane_nerve_v1.sql`
2. Dashboard: subscribe Realtime in NOOS dashboard app
3. Trigger registry entries + sweep probe for pg_cron job name
4. Proof receipt: `receipts/proof/noos-t8-stale-lane-nerve-v1.json`

---

## Rollback

- Disable pg_cron job: `cron.unschedule('stale-lane-nerve-v1')`
- Dashboard falls back to existing REST poll (keep legacy read path 30 days)

---

## Founder enables (UI)

- Supabase Realtime enabled on portfolio-spine project
- pg_cron extension (if not already) — Labs → Database → Extensions
- No GitHub environment approval required for T8 (DB-side only)
