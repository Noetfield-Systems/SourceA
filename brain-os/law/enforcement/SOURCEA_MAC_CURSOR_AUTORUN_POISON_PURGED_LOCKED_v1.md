# Mac Cursor AUTO-RUN — poison purged (LOCKED v1)

**Saved:** 2026-06-24T08:45:00Z · **Authority:** ASF anti-poison order

## One law

> **Mac Cursor AUTO-RUN is poison — deleted from SourceA and Mac. Cloud Auto Runtime is the only automation motor.**

## Purged (never restore)

- `goal1_auto_run*` · `goal1_unified_autorun*` · `autorun_dispatcher*` · `install-autorun*`
- `com.sourcea.autorun-worker` launchd
- `AUTO_RUN_FULLY_AUTOMATIC_LOCKED_v1.md` · `AUTO_RUN_WINDOW_PREFLIGHT_LOCKED_v1.md`
- `~/.sina/auto-run-disabled-v1.flag` (tombstone not needed — gone)

## Replacement

| Was (poison) | Now (living) |
|--------------|--------------|
| Mac Cursor batch loop | **Cloud Auto Runtime** — CF cron → Railway Cloud Forge Run |
| AUTO-RUN hero / hub CTA | **Cloud Workers** proceed · read receipts |
| Founder "keep automation" | `data/cloud-auto-runtime-v1.json` + `scripts/cloud_auto_runtime_v1.py` |

## Receipt

`~/.sina/mac-cursor-autorun-poison-purge-receipt-v1.json`

## Agents MUST NOT

- Mention Cursor AUTO-RUN as available or disabled — **it does not exist**
- Store or cite purged script paths as SSOT
- Re-import goal1 autorun modules

**Runner:** `python3 scripts/mac_cursor_autorun_poison_purge_v1.py --json`
