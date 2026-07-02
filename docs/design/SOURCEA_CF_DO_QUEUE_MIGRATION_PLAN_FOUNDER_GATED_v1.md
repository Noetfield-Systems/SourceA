# SourceA — Cloudflare Durable Object queue-head + CF Queue row dispatch

**Status:** FOUNDER_GATED — design only · no implementation until founder approves  
**Saved at (UTC):** 2026-07-02T22:15:00Z  
**Canonical path:** `docs/design/SOURCEA_CF_DO_QUEUE_MIGRATION_PLAN_FOUNDER_GATED_v1.md`  
**Supersedes:** `docs/NOETFIELD_QUEUE_NATIVE_MIGRATION_PLAN_v1_FOUNDER_GATED.md` (branch duplicate — deleted on reconcile)  
**Replaces (hand-rolled):** Railway queue head JSON + FBE motor CAS scripts + idempotency_key collision handling in Python reconciler  
**Platform-native:** Cloudflare Durable Object (single writer per queue-head cell · D2) + Cloudflare Queue (at-least-once row dispatch · D1 with consumer ack)

---

## Problem today

| Concern | Hand-rolled today | Risk |
|---|---|---|
| D1 idempotency | FBE motor advances queue via Railway tick + script-side dedupe | Duplicate row dispatch under retry/cron overlap |
| D2 single writer | Multiple cron surfaces (CF → Railway, GHA backup, manual dispatch) race queue head | Silent overwrites, double advance |
| Dispatch | HTTP POST batch to Railway from CF cron | No platform backpressure; poison retries manual |

---

## Target architecture

```
CF cron (loop-specialist / auto-runtime)
        │
        ▼
┌─────────────────────────────┐
│ Durable Object: QueueHeadDO │  ← sole writer for head cursor + lease (D2)
└──────────────┬──────────────┘
               │ enqueue(batch_id, op_key, row_ids[])
               ▼
┌─────────────────────────────┐
│ Cloudflare Queue: fbe-rows  │  ← at-least-once delivery, ack = commit (D1)
└──────────────┬──────────────┘
               │ consumer worker
               ▼
   Railway FBE consumer (existing motor body)
               │
               ▼
   Supabase truth_log / cycle_receipts (sink — existing)
```

**Brain / spine unchanged:** DO emits desired-state; reconciler remains sole executor in SourceA sandbox (L1).

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

| Phase | Action | Done when | Rollback |
|---|---|---|---|
| M0 | Shadow mode: DO mirrors head read-only; CF Queue receives copies, consumer no-ops | 7d zero head divergence vs script head | Disable queue consumer binding |
| M1 | DO owns lease; script head becomes read-only observer | D2 CAS test green (1 winner / 1 REJECTED) | `QUEUE_HEAD_WRITER=script` env |
| M2 | Enqueue path: DO → CF Queue messages (row payload hash) | D1 dupe_rate = 0 under fault inject | Drain queue; revert to direct Railway dispatch |
| M3 | Consumer executes row work; Railway tick becomes queue consumer only | 24h cycles + external-verify 15/15 | Re-enable Railway direct tick |
| M4 | Retire hand-rolled head mutex in `cloud_auto_runtime_v1.py` | No script CAS head in hot path | Restore code from tag |

**Founder gate:** each phase requires green 24h window + external-verify PASS on deploy chain.

---

## Rollback law (always available)

1. **Immediate (<5 min):** Set worker env `FBE_QUEUE_MODE=legacy` → bypass DO/Queue; Railway tick uses current script path.
2. **Queue drain:** Pause CF Queue consumer; snapshot message IDs to `receipts/queue-rollback/`.
3. **DO reset:** Export DO storage to JSON artifact; restore from last green checkpoint receipt.
4. **Spine safety:** Supabase sink idempotent by `(factory_id, cycle_number)` — rollback never deletes spine rows.

Rollback receipt schema: `sourcea-queue-native-rollback-v1` → truth_log event `queue_native_rollback`.

---

## Founder decisions required (before M0 code)

- [ ] Approve CF Queue + DO billing lane
- [ ] Approve 7d shadow window calendar
- [ ] Approve retire list for script mutex functions after M4
- [ ] Assign required reviewer on `production` environment (P4) before M2 enqueue goes live

---

## Hand-rolled code retired (post-M4)

| File / pattern | Retired by |
|---|---|
| Script-side queue head CAS in hot tick path | Durable Object lease |
| Retry loops guessing idempotency from row counts | CF Queue ack/nack + message ID |
| Deploy→verify timing sleep/poll | GHA `workflow_run` chain (PN-001) |
| Manual double-tick guards in autonomous drain backup | Concurrency group + DO single writer |

---

## Files touched (future — not until founder unlocks)

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

## Out of scope

- NOOS inbox queue (see NOOS T8 pg_cron prep doc)
- Brain routing (spec P5–P6)
- Verifier / laws edits (L5)

**Until founder unlocks:** this document is the only admissible artifact for queue-native migration.
