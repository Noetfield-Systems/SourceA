# REGISTRY DRAIN PROCESS — LOCKED

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## The only valid cycle

CHECK → ACT (only if gap found) → VERIFY → receipts/sa-XXXX-receipt.json → REGISTRY done

## What counts as done

- receipts/sa-XXXX-receipt.json exists logged
- receipt.status = DONE / PASS / VERIFIED / CHECK_PASSED
- receipt.source set (goal1_lane_broker / worker_inbox / api / maintainer_executor)
- critical_bugs: 0 at closeout

## What does NOT count

- YAML closeout alone
- Batch pack stamp
- Chat claim
- Overnight mark without receipt
- verify-only without receipt file

## Anti-fake guards (always active)

- closeout_sa_task.py: blocks done without receipt
- validate-registry-honest-gate-v1.sh: auto-reverts ghost done
- validate-closeout-gate-v1.sh: blocks batch evidence strings
- 495 YAMLs in QUARANTINE_BATCH_YAML/: dead as proof

## Receipt source field (required)

Always one of: goal1_lane_broker / restore-broker-proven-v1 / worker_inbox / api / maintainer_executor

## Queue discipline

- One sa per turn
- No batch close
- No UNATTENDED BATCH
- INBOX delivers next task — Worker executes only that

## Progress SSOT

honest_done = count of receipts/sa-XXXX-receipt.json logged

NOT: REGISTRY counter / YAML count / hub % / chat claim
