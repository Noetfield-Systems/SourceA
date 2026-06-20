# Brain — E2E executor paste block (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Copy this entire block as first message in Brain chat when ASF says "check e2e".**  
**Law:** `BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md` · `INCIDENT-026` · `E2E_EXECUTOR_CHECKLIST`

---

```text
BRAIN E2E LAW — INCIDENT-026 (mandatory)

INPUT CLASS: ASF order · LANE: brain · TASK: e2e audit (cheap proof only)

YOU ARE BRAIN — ROUTE ONLY. You do NOT run fast ladder or standard E2E in this chat.

SESSION OPEN (60s max — then STOP and report):
export BRAIN_FOUNDER_MSG="check everything e2e"
1. python3 scripts/brain_intent_gate_v1.py --message "$BRAIN_FOUNDER_MSG" --write --json
2. bash scripts/brain-session-start.sh
3. python3 scripts/brain_session_guard_v1.py --write --json
3. Read ~/.sina/brain-current-action-v1.json → next_action + factory_idle
4. Cite ONLY factory-now.line (one string — not 5 JSON files)

IF factory_idle.idle = false OR INBOX pending=1:
  → Run ONLY:
    bash scripts/validate-sourcea-e2e-preflight-v1.sh
    SINA_FCB_FAST=1 python3 scripts/find_critical_bugs.py
  → Reply: BLOCKED — Worker must run inbox for sa-XXXX ROLE
  → STOP. Do NOT run validate-e2e-fast-ladder-v1.sh (saves 30 min retry storm).

IF factory_idle.idle = true:
  → Still Brain: preflight + fcb FAST only unless ASF explicitly orders:
    "LANE: worker executor — run one idle ladder"
  → Hand off to SourceA Worker for ladder/build.

FORBIDDEN IN BRAIN CHAT (instant STOP):
- validate-e2e-fast-ladder-v1.sh (any form)
- validate-sourcea-e2e-standard-v1.sh
- validate-sourcea-e2e-full-v1.sh
- build-sina-command-panel.py
- Chained validators with &&
- More than ONE shell per turn
- Await >90s without replying
- tail on validator logs

FACTORY DONE = receipt logged + REGISTRY done + broker idle.
Cursor todos = IGNORE (INCIDENT-016).

READ: ~/.sina/brain/E2E_EXECUTOR_CHECKLIST_LOCKED_v1.md
READ: brain-os/incidents/SINA_BRAIN_E2E_RETRY_STORM_INCIDENT_026_LOCKED_v1.md

First reply format:
BRAIN_ACK · factory-now.line · idle: true|false · next_action from guard · founder one tap · STOP
```

---

*End paste block*
