# INCIDENT-030 — Worker YAML-only closeout fake green (report pointer)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**LOCKED body:** `brain-os/incidents/SINA_WORKER_YAML_ONLY_CLOSEOUT_FAKE_GREEN_INCIDENT_030_LOCKED_v1.md`  
**Date:** 2026-06-13 · **Severity:** Critical (repeat INCIDENT-006/007 class)

## Who owns the mistake

| Who | Verdict |
|-----|---------|
| **Worker (agent)** | **Main fault** — skipped broker submit on VERIFY; closed REGISTRY/attachments without `receipts/sa-XXXX-receipt.json` |
| **Broker** | **Not broken** — only writes receipts when VERIFY is submitted correctly; it wasn’t fed |
| **System / machine** | **Design gap** — allowed “done” in REGISTRY/chat without blocking until broker + receipt exist |
| **Governance / rules** | **On paper, not enforced at runtime** — laws existed; no hard stop on YAML-only closeout until 2026-06-13 fix |
| **Founder (ASF)** | **Not the mistake** — saw fake green correctly |

## One line

REGISTRY `done` without broker receipt = fake green. Permanent fix: `worker_verify_fast_v1.sh` + `validate-broker-receipt-cycle-v1.sh` + `worker_verify_closeout_v1.sh`.

Read full body for chronology, affected sa, and mandatory VERIFY order.
