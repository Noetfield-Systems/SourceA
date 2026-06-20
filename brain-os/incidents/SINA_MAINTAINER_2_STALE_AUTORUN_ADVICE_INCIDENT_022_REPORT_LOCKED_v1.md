# INCIDENT-022 — Maintainer 2 stale AUTO-RUN advice (pointer)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Classification:** High · Maintainer conduct / hub latch gap  
**LOCKED body:** `brain-os/incidents/SINA_MAINTAINER_2_STALE_AUTORUN_ADVICE_INCIDENT_022_LOCKED_v1.md`  
**Archive mirror:** `archive/attachments/2026-06-10/INCIDENT-022-maintainer-2-stale-autorun-advice_LOCKED_REPORT_v1.md`

## One screen

Maintainer 2 wrote founder **reject Cursor AUTO-RUN** law (2026-06-10) but **kept advising and leaving Hub `p0.next_action` on `Goal 1 auto-run`** until ASF said *"WE REJECT AUTO RUN WE CURSOR"*. Audit critical #1 (`sina_command_lib.py`) **listed, not fixed**. Plan created; **not executed**.

## Disk proof

- `command-data.json` (2026-06-10T11:41Z): `p0.next_action` still contains `Goal 1 auto-run:`
- `sina_command_lib.py` L648–650, L724: still `▶ START AUTO RUN` templates
- `ACTIVE_NOW.md`: **FREEZE** · autorun forbidden
- Missing: `founder_p0_next_action_v1.py`, `validate-hub-p0-no-autorun-v1.sh`

## Fix (Maintainer P0)

Ship Hub P0 copy module + validator per plan `hub_p0_no_autorun` — rebuild command-data.

**Do not** tell founder to run Terminal.
