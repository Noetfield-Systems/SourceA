# sa-0790 ACT — important_docs_index governance section completeness crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (CHECK + validators green)

## Task scope

Audit Doc library index (`scripts/important_docs_index.py` → `important_docs_payload()`) for phase-s7 council/ecosystem governance law coverage vs disk + hub essentials read chain.

## Index structure (12 sections)

| Section id | Governance relevance |
|------------|---------------------|
| `agent_session` | 4 items tagged `governance` |
| `command_app` | 1 item tagged `governance` (`TRUST_LEDGER_SCHEMA_LOCKED_v1.md`) |
| `ecosystem_law` | Registry chronology — not council-room slice |
| *(others)* | No `governance` tag |

**Finding:** No dedicated `governance` or `council_governance` section. Governance laws are scattered under `agent_session` / `command_app` tags only.

## Governance-tagged rows today (5)

| Path | Section | Priority |
|------|---------|----------|
| `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` | `agent_session` | P0 |
| `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md` | `agent_session` | P0 |
| `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` | `agent_session` | P0 |
| `SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md` | `agent_session` | P1 |
| `TRUST_LEDGER_SCHEMA_LOCKED_v1.md` | `command_app` | P1 |

## Phase-s7 council laws — disk vs index vs essentials

| Law | Doc library index | hub_essentials READ_CHAIN |
|-----|-------------------|---------------------------|
| `AGENT_MIND_SHARE_LOCKED_v1.md` | **MISSING** | IN |
| `AGENT_COUNCIL_ROOM_LOCKED_v1.md` | **MISSING** | IN |
| `AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md` | **MISSING** | IN |
| `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` | **MISSING** | **MISSING** |
| `AGENT_RULES_IN_CHARGE_LOCKED_v1.md` | **MISSING** | IN |
| `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` | **MISSING** | IN |
| `AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md` | **MISSING** | IN |
| `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md` | **MISSING** | IN |
| `AGENT_SCOREBOARD_LOCKED_v1.md` | **MISSING** | IN |
| `AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md` | **MISSING** | IN |

**Count:** 10 missing from Doc library index · 9/10 in essentials · 1 missing from both (`GOVERNANCE_UNIFICATION_ENGINE`).

## Authority pointers

| Doc | Clause |
|-----|--------|
| `ECOSYSTEM_IMPORTANT_DOCS_INDEX_LOCKED_v1.md` | Doc library sections SSOT — rebuild from Python index |
| `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` | Hub-visible governance items should receive index rows |
| `AGENT_COUNCIL_ROOM_LOCKED_v1.md` | Council slice parent laws |

## Distinct surfaces (not a gap)

| Surface | Purpose |
|---------|---------|
| Doc library (`important_docs_index.py`) | Founder/agent browse panel in Sina Command |
| Essentials read chain (`hub_essentials_index.py`) | Session-start mandatory reads for agents |

Council laws are wired in essentials + council room payload; Doc library index lags for discoverability only — not a runtime validator failure.

## Prior tier proof

- sa-0715 (T0) · sa-0740 (T1) · sa-0765 (T2) — same task title; queue compaction to T3 sa-0790

## Recommendation (informational — ASF order required for index edit)

1. Add `council_governance` section **or** extend `agent_session` with 10 council law rows (P0/P1, tag `governance`).
2. Add `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` to **both** index and essentials read chain.
3. Rebuild Doc library panel after `important_docs_index.py` change.

## Validators (ACT)

- `validate-governance-fleet-v1.sh` — PASS

## OPEN (informational)

1. **OPEN-1:** No dedicated governance section — tag scatter only.
2. **OPEN-2:** 10 council/ecosystem laws absent from Doc library index.
3. **OPEN-3:** `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` absent from essentials read chain.
