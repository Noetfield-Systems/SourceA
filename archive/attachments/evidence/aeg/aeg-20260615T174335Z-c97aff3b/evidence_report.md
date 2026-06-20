# Proof Narrative — System Blocked

**Saved:** 2026-06-15T17:43:35Z · **Retrofit:** doc-datetime-law batch retrofit
**Header:** System Blocked: 2026-06-15T12:00:00Z | Reason: synthetic test blocker

**Evidence ID:** `aeg-20260615T174335Z-c97aff3b`

Forensic bundle — terminal capture, UI state, critic_boot receipt. Buyer-clickable proof link.

## Critic boot checks

| Check | Status | Reason |
|---|---|---|
| ssot_brief | BLOCK | synthetic test blocker |

## Terminal evidence

- Terminal transcript from boot receipt (honest snapshot, no re-run)

## UI evidence

- UI capture skipped: unavailable

## Verdict (JSON)

```json
{
  "schema": "critic-boot-v1",
  "at": "2026-06-15T12:00:00Z",
  "verdict": "BLOCK",
  "ok": false,
  "blockers": [
    "synthetic test blocker"
  ],
  "checks": [
    {
      "name": "ssot_brief",
      "ok": false,
      "reason": "synthetic test blocker"
    }
  ]
}
```
