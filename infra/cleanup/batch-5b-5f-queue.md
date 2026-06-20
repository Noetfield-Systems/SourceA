# Batch 5b–5f — queue (after 5a)

**Saved:** 2026-06-20T22:00:00Z  
**Root after 5f:** **2** files (`START_HERE.md`, `ACTIVE_NOW.md`)  
**Receipt:** `data/cleanup-track-progress-v1.json`

## Completed

| Batch | Files | Result |
|-------|------:|--------|
| **5a** | 69 | `SOURCEA_*` → `brain-os/law/` · executed 2026-06-20 |
| **5b** | 10 | `WORLD_*` stubs → `archive/root-stubs/` · executed 2026-06-20 |
| **5c** | 7 | `FOUNDER_*` → `brain-os/law/enforcement/` · executed 2026-06-20 |
| **5d** | 5 | `CURSOR_*` → law + archive · executed 2026-06-20 |
| **5e** | 51 | `SINA_*` → law + incidents · executed 2026-06-20 |
| **5f** | 86 | `OTHER` → law / system / archive · executed 2026-06-20 |

**Batch 5 track complete.** Root sprawl: **328 → 2**.

## keep-root (never move)

- `START_HERE.md`
- `ACTIVE_NOW.md`

## Per sub-batch checklist (Mac founder session)

1. Grep consumers · patch pointers (before execute)
2. Manifest rows + critic packet · ASF APPROVED
3. **Execute only (one command):** `python3 infra/cleanup/execute_batch_python_v1.py --batch 5X`
4. Refresh inventory + `python3 scripts/cleanup_track_sync_v1.py --json`
5. One git commit per sub-batch

**Mac Law — do NOT run validator chains after execute.** See `data/cleanup-mac-execute-only-v1.json`.

Legacy bash wrapper (`execute-batch-v1.sh`) delegates to Python — avoids xargs/sandbox hang.
