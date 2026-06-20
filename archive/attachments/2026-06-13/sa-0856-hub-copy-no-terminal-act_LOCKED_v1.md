# sa-0856 ACT — Cross-check SINA_COMMAND_NO_TERMINAL_FOUNDER law in hub copy

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T23:40Z · **Turn:** ACT · **Worker:** SourceA

## Shipped (scripts only)

| Piece | Action |
|-------|--------|
| `scripts/validate-hub-copy-no-terminal-v1.sh` | **NEW** — law in read chain · hub copy · worker-hub policy |
| `scripts/noetfield_unified_guide.py` | **HEAL** — `mac_actions` hints → one-tap / Actions tab copy (no shell) |
| Chains | `validate-founder-docs-no-terminal-v1.sh` |

## Healed violation

**Before:** Essentials `mac_actions` showed `cd` / `python3` / `.sh` commands to founder.

**After:**

| Label | Hint |
|-------|------|
| Sync mirror | Actions tab → one tap |
| Rebuild notices | Actions tab → agents run build |
| Hub / refresh | Worker Hub → Safety / Light refresh |

## No `app.js` diff

Worker scope — legacy panel title unchanged; payload heal drives Essentials render on hub refresh.

## Duplicate chain

Also satisfies **sa-0806** T0 · **sa-0830** T1 · **sa-0881** T3.

## Validators (ACT)

| Validator | Result |
|-----------|--------|
| validate-hub-copy-no-terminal-v1 | PASS |
| validate-founder-docs-no-terminal-v1 | PASS |
| worker_verify_fast_v1 | PASS |

*End sa-0856 ACT*
