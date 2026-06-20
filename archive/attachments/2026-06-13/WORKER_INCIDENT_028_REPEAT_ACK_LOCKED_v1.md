# Worker INCIDENT-028 repeat ack (LOCKED v1)

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13 · **Reporter:** SourceA Worker `fd67502f`  
**Authority:** ASF order — delete stale auto-send wording · disk-first close-line  
**Parent:** `brain-os/incidents/SINA_WORKER_STALE_PROMPT_FEED_AUTOSEND_INCIDENT_028_LOCKED_v1.md`

---

## What broke (this session)

Worker ended two substantive replies with:

> "Open Sina Command → Prompt feed — review the 10 steps and tap Confirm to auto-send 10 prompts."

That phrase is **dead law** since INCIDENT-024. Repeated after INCIDENT-028 remediation = **INCIDENT-028 repeat**.

**Root cause:** Stale Cursor injected workspace rule snapshot (pre-v3 `prompt-queue.mdc`) — disk file was already correct; agent parroted cached injection, not disk.

---

## Disk truth (reference — who wins)

| Role | Reference |
|------|-----------|
| **ASF** | Founder orders · Hub taps only |
| **Brain** | Routes `sa` · picks queue · does not build hub |
| **Maintainer 2** | Hub/form SHIP · anti-staleness validators |
| **Worker** | One `sa` turn · validators · **never** founder close-line with auto-send |
| **Form office** | M1 Canvas + `live-founder-decision-form-v1.json` |
| **Execution SSOT** | `run-inbox-disk-truth-v1.json` · `live-ongoing-prompts-next-10-v1.json` |

---

## Remediation shipped (2026-06-13)

| # | Fix |
|---|-----|
| 1 | `prompt-queue.mdc` v3 — explicit FORBIDDEN + CORRECT close-line blocks |
| 2 | `agent-skills/sourcea_worker/SKILL.md` — INCIDENT-028 mandatory read + close-line |
| 3 | `GOV_E2E_UNIFICATION_MANIFEST` §9 — forbidden row corrected |
| 4 | This ack receipt |

---

## Correct founder close-line (use forever)

**NEVER:** confirm auto-send · auto-send 10 prompts · review 10 steps tap Confirm

**CORRECT:**
- Live next 10 = machine queue on disk — Prompt feed **displays** only
- Optional: Hub → Prompt feed → **See big picture** (commentary)
- P0: Hub → **Safety check** (anti-staleness) · or M1 Canvas PICKs per form

---

*End WORKER_INCIDENT_028_REPEAT_ACK_LOCKED_v1*
