# sa-0792 ACT — blueprint navigator inclusive vs exclusive scopes crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (CHECK + validators green)

## Task scope

Validate Council Room **Application blueprint navigator** splits `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md` sections into **inclusive (overall)** vs **exclusive (particular per-agent)** per ASF terminology.

## Law ↔ machine contract

| Term (blueprint § ASF terminology) | Meaning | Navigator mapping |
|----------------------------------|---------|-------------------|
| **Inclusive** | Whole app, all 8 agents, shared laws, overall session flow | All `## N.` sections **except** §4 |
| **Exclusive** | Particular per-agent roster, roles, repos, forbidden paths | **§4 only** — "Registered agents — full roster" |

Parent law: `AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md` — D-UI-01 blueprint navigator **SHIPPED** (inclusive + exclusive § buttons).

## Backend (`scripts/agent_council_room.py`)

`_blueprint_nav_sections()`:

```python
"scope": "exclusive" if n == 4 else "inclusive"
```

Live parse (**23** sections):

| Scope | Count | Sections |
|-------|-------|----------|
| inclusive | **22** | §0–§3, §5–§22 |
| exclusive | **1** | §4 Registered agents — full roster |

`council_room_payload()["blueprint_nav"]` === `_blueprint_nav_sections()` on disk.

## UI (`agent-control-panel/assets/app.js`)

Council Room card **Application blueprint navigator**:

| Row | Filter | Button style | Purpose |
|-----|--------|--------------|---------|
| Inclusive | `scope !== "exclusive"` | `sc-btn-ghost` | Overall app coverage buttons |
| Exclusive | `scope === "exclusive"` | `sc-btn-gold` | Particular per-agent §4 |

Copy: *"Inclusive (overall): whole app coverage. Exclusive (particular): per-agent §4 roster."*

`sc-open-gov-doc` opens `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md` in Doc editor.

## Alignment verdict

| Check | Result |
|-------|--------|
| Law § terminology vs backend scope rule | **PASS** |
| Backend payload vs UI filter split | **PASS** |
| §4 title matches law ("Registered agents — full roster") | **PASS** |
| Dedicated validator script | **OPEN** — none; fleet + manual crosswalk only |

## Distinct from rules-in-charge panel

| Surface | Inclusive | Exclusive |
|---------|-----------|-----------|
| Blueprint navigator | All blueprint § except §4 | §4 agent roster |
| Rules in charge (`agent_rules_in_charge.py`) | Full inclusive index (all rules) | Highlights "in charge NOW" |

Same ASF terminology pattern — different docs.

## Validators (ACT)

- `validate-governance-fleet-v1.sh` — PASS

## Prior proof

- sa-0717 / sa-0742 / sa-0767 — same task title (queue compaction to T3 sa-0792)

## OPEN (informational)

1. **OPEN-1:** Add `validate-blueprint-navigator-v1.sh` asserting §4 exclusive + count ≥ 20 inclusive (hardening only).
