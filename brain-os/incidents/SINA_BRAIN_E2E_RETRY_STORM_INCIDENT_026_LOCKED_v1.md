# Brain E2E retry storm — 30 min vs 2 min (INCIDENT-026 LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-INCIDENT-026  
**Classification:** MANDATORY READ — Brain · executor · Maintainer before “check e2e”  
**Window:** 2026-06-11 Brain session (~25–30 min shell on one ask)  
**Companion:** `~/.sina/brain/E2E_EXECUTOR_CHECKLIST_LOCKED_v1.md` · `factory_idle_gate_v1.py`

---

## 0. One sentence

> **Fast ladder is idle-unsafe — running it during open INBOX / ACT head is legal FAIL; six retries caused the marathon, not factory sickness.**

---

## Root cause (system bug — then agent amplification)

| Class | Truth |
|-------|--------|
| **Rule collision** | ASF “check e2e” + `agent-loop` executor + `smart-judgment` heal + no `AUDIT_CHEAP` branch in `brain_intent_gate` → Brain became healer-executor hybrid |
| **Intent gap** | `brain_intent_gate_v1.py` mapped “check e2e” → `OTHER` with **empty** allowed list — no machine STOP |
| **Guard contradiction** | `brain_session_guard` **allowed** fast ladder while `BRAIN_NO_FULL_E2E` forbade standard/full — split brain |
| **Legal DENIED** | `sourcea_execute --dry-run` fails when queue head = ACT or `WORKER_TURN_OPEN` |
| **SSOT drift loop** | INCIDENT-014 class — queue/factory-now/ACTIVE_NOW mismatch → repair → rebuild → ladder again |
| **Agent sin** | 6× ladder without idle gate · `tail` on logs · skipped rules loop |
| **False done** | INCIDENT-016 — Cursor todos green while factory still on sa-0787 VERIFY |

**System fix:** `BRAIN_RULE_COLLISION_MATRIX_LOCKED_v1.md` · `AUDIT_CHEAP_E2E` intent · guard forbids ladder · `factory_idle_gate` · `--require-idle`

---

## Fixes shipped (2026-06-11)

| Fix | Path |
|-----|------|
| Idle gate probe | `scripts/factory_idle_gate_v1.py` |
| Ladder `--require-idle` | `scripts/validate-e2e-fast-ladder-v1.sh` (exit 2 <5s) |
| Standard E2E wires idle | `scripts/validate-sourcea-e2e-standard-v1.sh` |
| Gatekeeper JSON exit 0 | `scripts/gatekeeper_v1.py` (`--json` always exit 0; read `status`) |
| Executor checklist | `~/.sina/brain/E2E_EXECUTOR_CHECKLIST_LOCKED_v1.md` |
| Self-upgrade 100 | `~/.sina/brain/AGENT_SELF_UPGRADE_100_PHASED_v1.md` |
| Agent-review | AR-994c360d72 (`--require-idle` on ladder) |

---

## Agent law (pointer — not duplicate prose)

1. Read `factory-now.line` + INBOX + `healthy-queue-state-v1.json` (60s).
2. If not idle → **preflight + fcb FAST only** → founder one tap: Worker inbox.
3. **Max ONE** fast ladder per turn.
4. Factory done = receipt + REGISTRY — not Cursor todos.

---

*End INCIDENT-026*
