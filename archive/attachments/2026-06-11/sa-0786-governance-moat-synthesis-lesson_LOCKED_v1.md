# sa-0786 — Governance moat ~50% product (synthesis lesson)

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-11  
**SA:** sa-0786 · phase-s7-council-governance · T3  
**Law:** `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` · `strategic_synthesis_hub.py`

## Lesson

Governance is not a sidebar — it is roughly **half the product**:

1. **Council Room** — shared rules, mind share, essay discourse, unification engine, advisory votes.
2. **Rules in charge** — `agent_rules_loop_orchestrator.py` + `GET /api/agent-rules-in-charge-v1` feed hub + Council highlight list (`enrich_shared_rules_digest`).
3. **Fleet + scoreboard** — 8 agents, governance-fleet validators, honest progress (Valid YES + receipts).
4. **Factory drain** — CHECK→ACT→VERIFY per SA; broker closeout; no plan-todo ghost completion (INCIDENT-016).

Delivery and revenue lanes run in parallel; **governance moat** is what makes multi-agent coordination honest and founder-click-only.

## Machine proof

- `scripts/strategic_synthesis_hub.py` → `lessons[]` includes "Governance is ~50% of the product"
- Council `shared_rules` highlight count aligns with `in_charge_now` from rules loop orchestrator
- `find_critical_bugs.py` → hub_health + worker_health cross-check (sa-0240)

## WTM thread

Spine: STRATEGIC-SLICE · Council governance phase s7 · honest 600+/1000 Valid YES
