# Trust ledger schema (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Date:** 2026-06-06  
**Path:** `~/.sina/agent-governance-events.jsonl`  
**Producer:** `scripts/agent_governance_events.py`

---

## Row schema

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `schema` | string | yes | `agent-governance-event-v1` |
| `id` | string | yes | `GOV-{uuid}` |
| `at` | ISO8601 | yes | UTC timestamp |
| `event_type` | string | yes | e.g. `session_report`, `essay_submitted`, `scoreboard_verified` |
| `workspace_id` | string | yes | Agent workspace id |
| `detail` | string | no | Short human summary |
| `extra` | object | no | Structured payload |
| `source` | string | no | `scoreboard`, `essay_discourse`, `hub` |

---

## Event types (v1)

- `session_report` — Scoreboard report filed
- `scoreboard_verified` — ASF verify column ✓
- `essay_submitted` — Essay discourse post
- `essay_best_marked` — Best essay selected for subject
- `council_attest` — Council brief attested
- `vault_deposit` — Document deposited to agent vault

---

## Consumers

- Governance drift engine
- Event bus (`governance.event` topic)
- TrustField lane attestations

---

## Forbidden

- PII or secrets in `detail`
- Mutating historical rows — append-only ledger
