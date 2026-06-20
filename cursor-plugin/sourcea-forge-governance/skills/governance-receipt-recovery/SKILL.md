---
name: governance-receipt-recovery
description: >-
  Recover lost thread context from receipts and disk pointers before acting.
  Use when the user says missed it, lost link, prove from disk, or after
  context summarization on governance or audit topics.
---

# Governance receipt recovery

**Chat is leaf. Receipts and indexed disk win.**

## Recovery loop

```
1. PAUSE — no tail-summary-only replies
2. SEARCH — prior receipts, registry JSON, README paths
3. FOUND | NOT FOUND — name exact path or search scope
4. PROVE — verify_run or emit_receipt_readonly on candidate
5. WIRE — one pointer; no duplicate law prose
6. REPLY — verdict first, then next tap
```

## When to run

| Trigger | Action |
|---------|--------|
| User correction / "you missed" | Full loop |
| Context summarized mid-audit | Re-read receipt + registry |
| Before new governance doc | Check existing registry row |
| MOCK_ONLY verdict questioned | Explain stdio vs cloud tier honestly |

## Tools

- **`verify_run`** — Load receipt by id or validate inline witness
- **`emit_receipt_readonly`** — Check schema before citing a receipt as proof
- **`factory_status`** — Read-only queue glance when relevant

## Reply shape

```
FOUND — <path or receipt_id>
VERDICT — PASS|FAIL|MOCK_ONLY
USE — what it enables
NEXT — one founder tap
```

## Law

- Never invent receipt ids — use disk or MOCK_ONLY honestly.
- Do not claim enterprise-safe federation until cloud bucket is live.
- Recovery is routine, not heroics.
