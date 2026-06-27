# SourceA — Cloud Forge Run full-pack pattern (LOCKED)

**Saved:** 2026-06-23 · **UTC:** 2026-06-23T11:05:00Z  
**Incident:** INCIDENT-042 · **Vocabulary:** INCIDENT-043 · **SSOT:** `data/cloud-forge-run-full-pack-pattern-v1.json`  
**Pair:** `data/hub-cloud-forge-run-proceed-v1.json` · `data/cloud-auto-runtime-v1.json` · `data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json`

---

## One law (ASF 2026-06-23 — same as batch 2)

> **One external trigger (~10 min) moves 100 queue rows down inside one Railway HTTP request — 100 is the mandatory quota per turn (NOT “up to 100”). `full_pack` is the internal-loop mode flag (INCIDENT-043).**

| Field | Value |
|-------|--------|
| `full_pack` | `true` |
| `max_advance` | `100` |
| Trigger | Cloudflare cron `*/10` **or** Cloud Workers Proceed (`hub_proceed_pack`) |
| Motor plane | Railway FBE headless only |
| Mac | Cloud Workers.app `:13027` glance · **never** Mac FORGE motor for CLOUD-SEC |

---

## Chain (do not reorder)

```text
Cloudflare sourcea-cloud-auto-runtime-tick-v1 (cron */10)
  → POST https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/auto-tick/v1
      { trigger_source: cloudflare_cron, full_pack: true, max_advance: 100, auto_tick: true }
  → run_cloud_auto_tick (Railway)
  → PROVE (living_system_chain_validate_v1)
  → contract gate
  → run_auto_runtime_pack — internal while advanced < 100
       → proceed_on_cloud (_pack_internal: true) per CLOUD-SEC row
       → advance_on_pass on Railway volume phase-observed-v1.json
  → one cycle receipt · one observer row per trigger
```

**Cloud Workers.app** Proceed proxies the same body with `trigger_source: hub_proceed_pack`.

---

## Forbidden (instant fail — INCIDENT-042 class)

| Forbidden | Why |
|-----------|-----|
| One CLOUD-SEC per cron tick as the design | Breaks batch 2 ASF pattern |
| `boot_heal` / `activate_batch` on every `read_head()` | Corrupts pack loop mid-batch |
| Fake `SHIP PASS` when `advanced === 0` | Green theater in observer |
| Deploy new Railway image **without** Dockerfile COPY for active `queue_path` | `no_cloud_plans_in_active_queue` |
| Say “single cycle” when founder means **full pack** | Vocabulary poison |
| Say “up to 100” or “up to 100 rows” | INCIDENT-043 instant fail — 100 is mandatory minimum |
| Require Worker Hub `:13020` for Proceed | Trashed cockpit (INCIDENT-041 class) |
| Mac `portfolio__forge_dispatch_v1.py --full-motor` for CLOUD-SEC | INCIDENT-038 |

---

## Batch handoff (after 100/100 only)

1. `queue_batch_complete: true` at last CLOUD-SEC of batch (e.g. CLOUD-SEC-200, CLOUD-SEC-300).
2. Generate + lock next batch JSON on disk (`scripts/generate_secondary_cloud_forge_run_batch_v1.py`).
3. Update `data/cloud-forge-run-queue-active-v1.json` pointer + Dockerfile COPY + redeploy Railway.
4. `activate_batch` or boot heal arms head to first CLOUD-SEC of new batch.
5. **Optional:** pre-lock batch N+1 as `next_batch.ready_locked` for `swap_to_next_batch` on `advance_on_pass` at_end.

**Never** swap batch pointer **during** an active `run_auto_runtime_pack`.

---

## Proof (real progress only)

| Check | PASS |
|-------|------|
| `GET …/api/cloud-forge-run/queue/v1` | `cloud_forge_run_head` advances · ends at batch last CLOUD-SEC |
| Batch complete | `queue_batch_complete: true` · `cloud_forge_run_last_completed` = last id |
| Observer | One row per trigger · `advanced: 100` in pack receipt (not 100 observer rows) |
| Mac | Read receipt · do not validator-marathon (INCIDENT-039) |

---

## Related

- `brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_HUNDRED_ROWS_PER_TURN_TERMINOLOGY_LOCKED_v1.md`
- `brain-os/incidents/SINA_CLOUD_FORGE_RUN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_LOCKED_v1.md`
- `brain-os/incidents/SINA_CLOUD_FORGE_RUN_BATCH3_RAILWAY_CHAIN_INCIDENT_042_LOCKED_v1.md`
- `cloud/workers/cloud-auto-runtime-tick-v1/src/index.js`
- `scripts/cloud_auto_runtime_v1.py` → `run_auto_runtime_pack`
- `cloud/Dockerfile.fbe-runner` — batch JSON COPY lines

**LOCKED v1.0**
