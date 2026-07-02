# SourceA — Cloudflare Durable Object queue-head + CF Queue row dispatch

**Status:** FOUNDER_GATED — design only · no implementation until founder approves  
**Saved at (UTC):** 2026-07-02T22:00:00Z  
**Replaces (hand-rolled):** Railway queue head JSON + FBE motor CAS scripts + idempotency_key collision handling in Python reconciler  
**Platform-native:** Cloudflare Durable Object (single writer per queue-head cell · D2) + Cloudflare Queue (at-least-once row dispatch · D1 with consumer ack)

---

## Problem today

| Concern | Hand-rolled today | Risk |
|---|---|---|
| D2 single writer | `cloud_forge_run_head` row + Python CAS in Railway motor | Race under parallel cron / manual dispatch |
| D1 idempotency | `idempotency_key` + sink upsert partial | Dupe rows on retry without native queue dedupe |
| Dispatch | HTTP POST batch to Railway from CF cron | No platform backpressure; poison retries manual |

---

## Target architecture

```
CF cron (loop-specialist / auto-runtime)
        │
        ▼
┌───────────────────────┐
│ Durable Object        │  queue-head-v1 (ONE writer per blueprint_id)
│  · head pointer       │  compare-and-swap advance
│  · batch_id CAS       │  reject illegal transitions (D4)
└───────────┬───────────┘
            │ enqueue row op_keys
            ▼
┌───────────────────────┐
│ Cloudflare Queue      │  forge-run-rows-v1
│  · at-least-once      │  consumer idempotency via op_key
└───────────┬───────────┘
            │
            ▼
   Railway FBE consumer (existing motor body)
            │
            ▼
   Supabase sink ack → DO advance allowed (D4)
```

### Durable Object responsibilities (D2 native)

- Own `cloud_forge_run_head` state cell for `MAC-CTL-002`
- Expose `POST /advance` only after sink ack receipt (D4)
- Emit cycle receipt stub with `mission_id` before enqueue
- Reject concurrent writers — DO is sole mutator for head pointer

### CF Queue responsibilities (D1 native)

- One message per row `op_key` (deterministic body)
- Consumer uses existing `idempotency_key` upsert — queue retry ≠ duplicate row when sink honors op_key
- Dead-letter queue for poison rows (founder_gated inspect)

---

## Migration phases (rollback at each gate)

| Phase | Action | Rollback |
|---|---|---|
| M0 | Shadow-read DO mirror head; Railway remains writer | Disable DO route; ignore mirror |
| M1 | Dual-write: Railway writes + DO validates match | Flip flag `DO_HEAD_VERIFY_ONLY=false` |
| M2 | DO becomes writer; Railway reads head via DO API | `HEAD_WRITER=railway` env revert |
| M3 | Enqueue rows to CF Queue; Railway consumer pulls | Drain queue; revert to HTTP batch POST |
| M4 | Remove hand-rolled CAS Python in motor | Redeploy previous Railway SHA |

**Founder gate:** each phase requires green 24h window + external-verify PASS on deploy chain.

---

## Files touched (future — not in this commit)

| Path | Change |
|---|---|
| `cloud/workers/cloud-forge-run-head-do-v1/` | New DO worker |
| `cloud/workers/cloud-auto-runtime-tick-v1/src/index.js` | Route head ops to DO |
| `scripts/cloud_auto_runtime_v1.py` | Consumer ack → DO advance |
| `data/trigger-registry-v1.json` | Register DO + queue consumer triggers (L14) |

---

## Success criteria

- D2 metric `silent_overwrites = 0` under parallel tick simulation
- D1 metric `dupe_rate = 0` on queue redelivery test
- No regression on M2 factory-24-7 mission receipts

---

## Explicitly out of scope until founder approves

- Deleting Railway motor
- Changing L4 external-verify recipes
- Tier 1 parallel sandboxes (W-LBA-010)
