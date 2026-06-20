# Founder-only: Actions enqueue eval spine bridge (canonical sa-0404)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **ASF-only row** · T1/T2/T3 echo: sa-0429 · sa-0454 · sa-0479

## Founder steps (hub only — no Terminal)

1. Open Sina Command → **Actions** tab
2. Tap **Enqueue eval spine bridge** (label in `sync_founder_missed_actions_v1.py`)
3. Tap **Refresh hub** (maintainer/agent runs `hub_self_refresh_v1.py` — founder clicks only)
4. Confirm `validate-spine-bridge-founder-v1.sh` PASS when `eval_1b_gate_ok` open

## Machine proof

- `scripts/validate-spine-bridge-founder-v1.sh`
- `scripts/sync_founder_missed_actions_v1.py` — action id + label wired

*End founder spine bridge guide*
