# Brain — no full E2E shell (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 · **Locked:** 2026-06-10  
**Law:** Brain chat is **routing only**. E2E proof is **scripted**, not Brain-improvised.  
**Incident:** INCIDENT-026 — validator recursion blocking

---

## Forbidden in Brain chat (6+ min stall class)

```bash
# NEVER in Brain chat unless ASF explicitly orders in this message:
bash scripts/validate-sourcea-e2e-full-v1.sh
bash scripts/validate-sourcea-e2e-standard-v1.sh
cd scripts && SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py
```

## Forbidden in Brain chat (validator recursion — 2–25 min class)

```bash
# Worker/daemon only — INCIDENT-026:
bash scripts/validate-live-prompt-feed-e2e-v1.sh
python3 scripts/live-prompt-lane-score-v1.py --strict
python3 scripts/live_prompt_lane_audit_v1.py
python3 scripts/cross-plan-readiness-v1.py          # without --fast
# Chained shells: cmd1 && cmd2 && … combining any validator above
```

**Conduct:** max **one** shell per Brain turn · max **90s** wall · reply **<30s** then STOP · never `Await` **>60s** without replying.

## Allowed in Brain (≤90s — cheap proof only)

```bash
python3 scripts/brain_session_guard_v1.py --write --json
python3 scripts/factory_idle_gate_v1.py --json
bash scripts/validate-sourcea-e2e-preflight-v1.sh
SINA_FCB_FAST=1 python3 scripts/find_critical_bugs.py
python3 scripts/brain_validate_goal1_v1.py --write-receipt
bash scripts/validate-closeout-receipt-only-v1.sh
```

## Forbidden in Brain (was allowed — caused 30 min storm)

```bash
bash scripts/validate-e2e-fast-ladder-v1.sh   # Worker/maintainer only · --require-idle
bash scripts/validate-sourcea-e2e-standard-v1.sh
```

**Paste block:** `brain-os/contract/BRAIN_E2E_EXECUTOR_PASTE_LOCKED_v1.md`

## Allowed closeout in Brain (≤5s — receipt read only)

```bash
python3 scripts/live-prompt-worker-closeout-v1.py --json
python3 scripts/cross-plan-readiness-v1.py --fast --json
```

## When INBOX pending

- `chain.activate` = **READY** or **WAIT** → **not broken**
- Brain says: **RUN INBOX / START AUTO RUN** — Worker executes
- Brain does **not** re-run E2E to “unstick”

## Disk SSOT

`~/.sina/brain-current-action-v1.json` — read every Brain turn after `brain-session-start.sh`

## Full debugger playbook (Worker / Maintainer)

`SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md` — Rules 0–7, sa-0042 class, logging, golden lanes.

---

*End BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1*
