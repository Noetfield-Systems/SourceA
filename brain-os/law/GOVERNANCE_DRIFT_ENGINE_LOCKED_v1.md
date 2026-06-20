# Governance Drift Engine (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Machine:** `scripts/governance_drift_engine.py`  
**Validator:** `scripts/validate-governance-drift-v1.sh`  
**API:** `GET/POST /api/governance-drift`  
**SSOT:** `~/.sina/governance_drift_report_v1.json`

---

## 0. Law

**Governance drift is measured by running existing audit sensors and aggregating a founder-visible score on Today + Council path.**

---

## 1. Sensors

| ID | Source |
|----|--------|
| GD-DOC | `audit_hub_source_alignment.py` |
| GD-FLEET | `audit_agent_governance_e2e.py` |
| GD-NAV | `audit_essentials_nav.py` |
| GD-PAGES | `audit_private_agent_pages.py` |
| GD-BOWL | `sina-bowl/DRIFT.json` item count |
| GD-OPS | Hub `:13020` liveness |

**Aggregate score:** 0–100 (mean of sensor scores).

---

## 2. Hub surfaces

- **Today** tab — score stat + sensor list + Refresh drift report
- **POST** `/api/governance-drift` `{ "action": "run" }` — rebuild report + refresh payload

---

**END · LOCKED**
