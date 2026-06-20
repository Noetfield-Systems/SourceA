# Permanent factory evidence fix (2026-06-13)

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Law:** `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` · INCIDENT-006/007

## Problem

Agents marked REGISTRY `done` with YAML/attachments only — no `receipts/sa-XXXX-receipt.json` or broker `WORKER_SUBMIT` cycle. Monitor correctly showed **Receipt NO** (fake-green).

## Permanent mechanical fix (shipped)

| Layer | Script | Effect |
|-------|--------|--------|
| Auto-revert | `validate-registry-honest-gate-v1.sh` | Reverts `done` without receipt on every run |
| Broker cycle | `validate-broker-receipt-cycle-v1.sh` | **NEW** — all done rows must be receipt + broker PASS |
| Fast verify | `worker_verify_fast_v1.sh` | **Wired** — chains both gates above |
| Closeout gate | `closeout_gate_v1.py` | **Hardened** — receipt path requires broker PASS |
| Canonical closeout | `worker_verify_closeout_v1.sh` | **NEW** — only approved VERIFY closeout path |
| FCB critical | `find_critical_bugs.py` | **Wired** — broker-receipt cycle validator |
| Agent law | `098-worker-full-round-evidence.mdc` · `WORKER_NO_SLOW_VERIFY` · `agent_turn_context_v1.py` | VERIFY role text updated |

## VERIFY order (mandatory)

1. Task validator PASS  
2. `WORKER_ROUND_REPORT` + `goal1_lane_broker.py worker-submit --stdin`  
3. `bash worker_verify_closeout_v1.sh --sa sa-XXXX --evidence "..."`  
4. `bash worker_verify_fast_v1.sh`

## Proof

```bash
bash scripts/validate-broker-receipt-cycle-v1.sh
bash scripts/worker_verify_fast_v1.sh
bash scripts/validate-monitor-honesty-v1.sh
```

*End permanent fix*
