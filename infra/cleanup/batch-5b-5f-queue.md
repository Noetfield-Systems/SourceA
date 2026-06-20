# Batch 5b–5f — queue (after 5a)

**Saved:** 2026-06-20T17:34:00Z  
**Root after 5a:** **158** files  
**Receipt:** `data/cleanup-track-progress-v1.json`

## Completed

| Batch | Files | Result |
|-------|------:|--------|
| **5a** | 69 | `SOURCEA_*` → `brain-os/law/` · executed 2026-06-20 |

## Next (same manifest workflow each)

| Batch | Theme | ~files | Destination | Status |
|-------|-------|-------:|-------------|--------|
| **5b** | `WORLD_*` | 10 | `brain-os/wtm/` | **NEXT** — grep · manifest · critic · approve · execute |
| **5c** | `FOUNDER_*` | 7 | `brain-os/law/enforcement/` | queued |
| **5d** | `CURSOR_*` | 5 | `docs/archive/` or `brain-os/law/` | queued |
| **5e** | `SINA_*` | 48 | `brain-os/law/` (+ stubs) | queued · Path 2 |
| **5f** | `OTHER` | 77 | row-by-row | queued |

## Per sub-batch checklist

1. `bash infra/cleanup/generate-inventory-v1.sh`
2. Grep consumers for that bucket
3. Patch pointers (`governance_paths_v1.py` if script consumers)
4. Add manifest rows with batch id `5b` … `5f` (exact filenames)
5. `infra/cleanup/batch-5X-diff-for-critics.md`
6. ASF APPROVED → `execute-batch-v1.sh --batch 5X`
7. One git commit per sub-batch

## keep-root (never move)

- `START_HERE.md`
- `ACTIVE_NOW.md`
