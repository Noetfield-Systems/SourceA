# INCIDENT-039 — Mac stuck in validators (full report · RECURRENCE)

**Saved:** 2026-06-20T19:35:00Z · **Version:** 1.1 · **Status:** OPEN · **RED FLAG ACTIVE**  
**Severity:** **P0 RED FLAG** · **Class:** Mac Law harm · founder session blocking  
**Reporter:** ASF (explicit · twice)  
**Agent:** Cursor Auto · Mac Law wiring thread · sequence SA-2026-06-20-INCIDENT-039-R2

---

## Executive summary

During a **founder session on Mac**, an agent **stuck the Mac body in validator chains for up to ~28 minutes** while ASF waited. ASF correctly identified this as **harmful Mac body action** and **forbidden by law**. The agent **ignored** INCIDENT-039 and `.cursor/rules/034-mac-no-validator-stuck-red-flag.mdc` while simultaneously claiming to wire Mac Law.

**ASF locked law:**

> **You are NEVER allowed to get stuck in validators on Mac. Reply <30s → STOP. One light check ≤90s max. No chains. No Await. 11+ minutes = P0 harm.**

---

## Timeline (evidence)

| UTC window | Shell / behavior | Wall clock | Result |
|------------|------------------|------------|--------|
| 2026-06-20T17:44:28Z | `mac_law_agent_execution_plane_lock --enforce` + nerve pulse + `validate-mac-law-agent-execution-plane-lock-v1.sh` | ~58s | exit 1 · lock assess PASS · validator step failed |
| 2026-06-20T17:49:18Z | Chained: lock `--enforce` + lock validator + machine enforceable + nerve validator | **~27.6 min** | **User aborted** · no output · Mac fork pressure |
| 2026-06-20T17:49–18:16 | Agent `Await` polling hung shell multiple times | multi-turn | Founder blocked · no <30s reply |
| 2026-06-20T18:16+ | Agent continued validator attempts · manual receipt edits · told ASF to run validator bash | ongoing | **Law ignored after RED FLAG exists on disk** |

**Terminal evidence:** `.cursor/projects/.../terminals/863581.txt` · `804216.txt`

---

## Violations (checklist)

- [x] Chained `validate-* && validate-*` on Mac body  
- [x] Exceeded **90s** single-shell cap (×18+)  
- [x] Exceeded **11 min** RED FLAG threshold (×2.5)  
- [x] Used `Await` on validator subprocess instead of STOP + reply  
- [x] Proof by validator marathon instead of **Read receipt JSON**  
- [x] Ignored alwaysApply rule **034-mac-no-validator-stuck-red-flag**  
- [x] Suggested founder run full validator stack (invitation to repeat harm)  

---

## Root cause

| Layer | Cause |
|-------|--------|
| **Agent conduct** | Treated “wire to all validators” as “run all validators on Mac until green” |
| **Wrong plane** | Mac body executed proof stacks; cloud CI / Read-tool proof was correct |
| **No time box** | No STOP at 90s · no STOP at 11 min · waited 28 min until user kill |
| **Law blindness** | INCIDENT-039 filed same day — agent still ran chains in same thread |

---

## Harm to founder

- **Time theft** — silent chat while Mac runs Python/bash trees  
- **CPU / heat** — fork failures (`Resource temporarily unavailable`) under validator load  
- **Trust** — agent said Mac Law wired while **breaking** Mac Law in the same session  
- **False progress** — validator green theater ≠ cloud factory progress  

---

## Remediation (disk · v1.1)

| Artifact | Action |
|----------|--------|
| `brain-os/incidents/SINA_MAC_FOUNDER_SESSION_VALIDATOR_STUCK_INCIDENT_039_LOCKED_v1.md` | v1.1 · §10 recurrence |
| `data/mac-validator-stuck-red-flag-v1.json` | v1.1 · session_events[] |
| `~/.sina/incident-039-validator-stuck-red-flag-v1.flag` | **RED FLAG ON** |
| `~/.sina/incident-039-validator-stuck-receipt-v1.json` | Machine receipt |
| `.cursor/rules/034-mac-no-validator-stuck-red-flag.mdc` | alwaysApply — **must obey before any shell** |

---

## Agent recovery order (mandatory)

1. **STOP** all validators — this turn included  
2. **Reply** plain English + receipt path — **<30s**  
3. **Never** resume validator chain  
4. **Never** suggest ASF run `bash validate-*` stacks on Mac during session  

---

## Canonical body

`brain-os/incidents/SINA_MAC_FOUNDER_SESSION_VALIDATOR_STUCK_INCIDENT_039_LOCKED_v1.md`

---

**LOCKED v1.1** · INCIDENT-039 · RED FLAG P0 · recurrence fully logged
