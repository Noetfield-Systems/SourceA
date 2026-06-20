# Mac read paths only — surfaces / mirror / nerve (LOCKED v1)

**Saved:** 2026-06-20T23:00:00Z  
**Incidents:** INCIDENT-039 · INCIDENT-040 · **INCIDENT-041**

## One law

> **Mac founder session: read gate receipt + truth bundle once — never audit-of-audit loops.**

## Read on Mac (once per chat start)

| Path | Use |
|------|-----|
| `~/.sina/agent_session_gate_receipt_v1.json` | Session inject + conduct |
| `~/.sina/last-truth-bundle-v1.json` | factory-now · queue · inject |
| `~/.sina/agent-live-surfaces-v1.json` | `factory_now_line` glance only |

## Deprecate on Mac body (ship window / cloud CI only)

| Layer | Mac | Cloud |
|-------|-----|-------|
| **surfaces** | read JSON line | write/sync |
| **mirror** | read inject | full sync on law ship |
| **nerve** | read receipt if present | pulse on ship |
| **queue unify** | read `queue_sa` | heal on ship |
| **governance full tier** | **FORBIDDEN** | maintainer only |
| **poison scrub** | `--validate` on session gate | `--all` on law ship |

## Forbidden forever (INCIDENT-041)

- Agents spawning a second audit to verify the first audit passed  
- `governance_zero_drift_live_wire_v1.py --tier full` during founder Mac chat  
- Chained `validate-*` after session gate on Mac  

**Machine:** `scripts/agent_mirror_poison_scrub_v1.py --validate` · `data/agent-memory-mirror-poison-law-v1.json`
