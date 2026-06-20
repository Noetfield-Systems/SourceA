# sa-0523 — mergepack progress json non-blocking read

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T13:35Z · **Phase:** s5-P3 commercial · **Tier:** T0

## Problem

Mergepack `~/Desktop/mergepack/PROGRAM_PROGRESS.json` was read via ad-hoc `load_json()` in multiple scripts. Missing file behaved gracefully but was not machine-proven or documented.

## Fix

| Piece | Role |
|-------|------|
| `scripts/mergepack_progress_read_v1.py` → `read_mergepack_progress_safe()` | Never raises — returns `{ok, missing, data}` |
| `scripts/update-program-progress.py` | Uses safe read; **merges** `signals_auto` (preserves extended hooks on sync) |
| `scripts/build-sina-daily-bowl.py` | Uses safe read |
| `scripts/validate-mergepack-progress-nonblocking-v1.sh` | Negative probe — missing file must not fail update-program-progress or build_payload |
| `scripts/sina_command_lib.py` | Unchanged (edit lock) — already uses `load_json() or {}` equivalent |

## Machine proof

```bash
cd scripts && bash validate-mergepack-progress-read-program-progress-v1.sh
```

## PROGRAM_PROGRESS hook

`signals_auto.mergepack_progress_read` → this attachment + `read_mergepack_progress_safe`.

*End sa-0523*
