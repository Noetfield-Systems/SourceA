# sa-0823 — ENFORCE / shadow gate display on H2 maintainer slice only

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **Tier:** T0 · **Hub 2** `/machines/`

## Verdict (one line)

H2 `/api/machine-hub/v1` exposes `maintainer_enforce_slice` — cross-checked against disk `gate_mode` and `/api/packet-readiness-v1`; displayed on `/machines/` maintainer card only (not legacy Hub 1 monolith).

## Slice contract

| Field | Rule |
|-------|------|
| **Payload key** | `maintainer_enforce_slice` on machine-hub API |
| **Schema** | `h2-maintainer-enforce-slice-v1` |
| **Hub scope** | H2 only — `hub: H2` · `slice: maintainer_ship` |
| **Gate SSOT** | `model_dispatch.current_gate_mode()` → `~/.sina/gate_mode_v1.txt` |
| **Cross-check** | `packet_readiness_hub_payload()` — `cross_check_ok` when `gate_mode == packet_gate_mode` |
| **Display (enforce)** | `display_line` contains `ENFORCE live on planner` |
| **Display (shadow)** | `display_line` contains `SHADOW active` |
| **Display (off)** | `display_line` contains `Gate OFF` |
| **H1 forbidden** | Legacy monolith packet panel — no enforce slice on `/` |

## Required keys

`gate_mode` · `packet_gate_mode` · `gate_is_enforce` · `gate_is_shadow` · `display_line` · `shadow_note` · `packet_readiness_pct` · `packet_gate_eligible` · `cross_check_ok` · `pref_path`

## UI surface

`/machines/index.html` renders `#enforce-line` + `#enforce-sub` from `maintainer_enforce_slice` (maintainer card above Executor SHIP queue).

## Machine proof

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash validate-h2-enforce-shadow-maintainer-slice-v1.sh
bash validate-enforce-dispatch-policy-alignment-v1.sh
python3 machine_hub_v1.py --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('maintainer_enforce_slice',{}).get('schema')=='h2-maintainer-enforce-slice-v1'"
```

## Law

`SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md` slot **23** · `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` §2 · `h2_maintainer_enforce_slice_v1.py`

*End sa-0823*
