# Outbound Execution Hardening — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T00:51:00Z · **Authority:** EDIT ALLOWED investigation fix
**Path:** `~/Desktop/SourceA/docs/OUTBOUND_EXECUTION_HARDENING_PLAN_LOCKED_v1.md`

## Problem (absolute truth — disk-verified)

1. **Receipt collision** — `receipts/{sa_id}-receipt.json` allowed U031 proof on `sa-1100` to block/overwrite U001.
2. **False done rows** — U027/U028/U029 marked `done` with `shipped_evidence` only; no upgrade-matched receipt.
3. **Bay theater** — signed work-order showed `outbound-fdg-icp` while active said `unmapped` for `linter_oqg` head.
4. **Loop auto blocked local work** — U001 (`linter_oqg`) never reached Worker INBOX while loop auto ON.
5. **Honesty theater** — `execution · 6/6 honest` passed while head unimplemented and collision present.
6. **Commercial still RED** — L3 25% · `w3_sina_read` · `w3_mail_from` · `w3_send_ready` blocked.
7. **B0503 planned** — no cloud consumer for non-local bays.
8. **FORM 79 rows** — gathering complete; founder UNIFY picks still open.

## Shipped fixes (this session)

| Fix | Script / artifact | Status |
|-----|-------------------|--------|
| Canonical receipt law | `scripts/outbound_receipt_path_v1.py` | **DONE** |
| Migrate 8 receipts + plan paths | `scripts/outbound_receipt_migrate_v1.py` | **DONE** |
| `mark_done` uses canonical path | `scripts/mark_outbound_upgrade_done_v1.py` | **DONE** |
| Queue prompts canonical receipt | `scripts/outbound_factory_queue_assign_v1.py` | **DONE** |
| Local-worker lane routing | `scripts/brain_outbound_work_order_v1.py` | **DONE** |
| Local lane → RUN INBOX deliver | `deliver_head()` in queue assign | **DONE** |
| Honesty: 8 checks + collision | `scripts/execution_plane_honesty_v1.py` | **DONE** |
| Plan proof validator | `scripts/validate_outbound_plan_execution_proof_v1.py` | **DONE** |
| Receipt path validator | `scripts/validate_outbound_receipt_path_v1.py` | **DONE** |
| Reset false-done U027–U029 | `scripts/outbound_plan_proof_backfill_v1.py` | **DONE** |
| Queue regen 92 pending | `healthy-queue-30-active.json` | **DONE** |

### Receipt law (SSOT)

```text
receipts/{upgrade_id}-{sa_id}-receipt.json
```

Legacy `receipts/{sa_id}-receipt.json` — read-only fallback; **never write** on closeout.

### Local-worker lanes (no cloud bay required)

`linter_oqg` · `telemetry` · `rrl_intelligence` · `research_ingest` · `sina_founder` · `anti_template` · `deferred_volume`

## Remainder plan (ordered)

### P0 — Ship U001 (Worker chat)

1. RUN INBOX — head **U001** · bay `sourcea-local-linter` · `execution_mode=local_worker`
2. Close with `receipts/U001-sa-1100-receipt.json` via `mark_outbound_upgrade_done_v1.py`
3. Verify: `validate_outbound_plan_execution_proof_v1.py` · `best_loop_oqg_score_v1.py` acceptance

### P0 — B0503 cloud consumer

1. Worker consumes `brain-outbound-work-order-active-v1.json` for non-local bays
2. `fdg_icp` / `icp4_one_product_line` → `outbound-fdg-icp` bay execute path
3. Mark B0503 `done` in `brain-cloud-reasoning-1000-upgrade-plan-v1.json`

### P1 — Commercial L3 (founder-owned)

| Gate | Action |
|------|--------|
| `w3_sina_read` | `python3 scripts/w3_founder_review_v1.py --show` · fundmore + ocree |
| `w3_mail_from` | Configure mail-from in commercial-command pulse accounts |
| `w3_send_ready` | Founder confirm-sent after read PASS |

### P1 — FORM UNIFY (M1 Canvas)

Founder picks on **Pending confirmations** view:

- **Q-FINAL-05 A** — authorize UNIFY compress of 79 rows
- **Q-FINAL-01** — north star: outbound 92-queue vs FBE catalog
- **Q-FINAL-02** — U001 bay: Worker WORK (now wired)

### P2 — Legacy receipt archive

1. Add `receipts/legacy/` README pointer — do not delete legacy files yet
2. Hub shows canonical path on closeout cards
3. Remove legacy write paths from `goal1_lane_broker.py` hints (cosmetic)

### P2 — Full-stack + outbound sync

- `sourcea-full-stack-100-fix-plan-v1.json` — align F001–F010 with receipt law row
- Re-run `outbound_factory_upgrade_pulse_v1.py` after each ship

## Validators (run after every ship)

```bash
python3 scripts/validate_outbound_receipt_path_v1.py --json
python3 scripts/validate_outbound_plan_execution_proof_v1.py --json
bash scripts/validate-form-official-e2e-v1.sh
python3 scripts/outbound_factory_upgrade_pulse_v1.py --json
```

## Current disk truth (post-fix)

| Surface | Value |
|---------|-------|
| Queue head | **U001** · sa-1100 · 1/92 |
| Plan done | **8/100** verified with canonical receipts |
| Receipt law | `receipts/{upgrade_id}-{sa_id}-receipt.json` |
| Execution mode | `local_worker` for U001 |
| Commercial L3 | 25% RED |
| B0503 | planned |

## One next tap

**Worker chat → RUN INBOX** — ship U001 skeleton detector with canonical receipt closeout.
