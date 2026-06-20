# sa-0525 — commercial lane G3 vault conditional evidence

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T13:46Z · **Phase:** s5-P3 commercial · **Tier:** T0

## Problem

Commercial lane wire G3 proof had disk status (`g3_tailscale=pending`) and vault deposits, but no machine contract to **append SOURCEA-PRIORITY evidence only when G3 becomes visible** in workspace vault.

## Fix

| Piece | Role |
|-------|------|
| `scripts/commercial_lane_g3_vault_v1.py` | `probe_g3_vault_visibility()` scans wire/trustfield/sourcea vaults for G3 keywords; `append_priority_g3_evidence_if_visible()` appends PRIORITY row only when visible |
| `scripts/validate-commercial-lane-g3-vault-evidence-v1.sh` | Negative probe — G3 not visible → no PRIORITY append (non-blocking) |
| `WIRE_LANE_PROGRESS.md` | G3 still open in the repository — append deferred until vault/disk pass |

## Visibility rule

G3 **visible** when:

1. Workspace vault document matches G3 keywords (`g3`, `tailscale`, `wire-g3`, `proof:g3`, …), **or**
2. `locked_plan.json` / `PROGRAM_PROGRESS.signals_auto.wire.g3_tailscale` is `pass`/`done`.

## Machine proof (current disk — G3 pending)

```bash
cd scripts && bash validate-commercial-lane-g3-vault-evidence-v1.sh
```

## PROGRAM_PROGRESS hook

`signals_auto.commercial_lane_g3_vault` → this attachment + probe/append fns.

*End sa-0525*
