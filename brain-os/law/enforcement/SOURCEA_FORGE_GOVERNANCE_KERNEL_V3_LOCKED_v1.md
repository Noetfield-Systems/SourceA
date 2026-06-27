# SourceA Forge Governance Kernel v3 (LOCKED)

**Saved:** 2026-06-25T16:00:00Z  
**Version:** 3.0 — LOCKED (legal arbitration supersedes v2 first-deny on conflicts)  
**Parent:** `SOURCEA_FORGE_GOVERNANCE_KERNEL_V2_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md`

---

## One law

> **When governance rules conflict, Forge MUST judge via legal arbitration — cases, multi-judge panels, precedent, and appeals — not blind first-deny enforcement.**

---

## Modules

| Resource | Address |
|----------|---------|
| Governance kernel v3 | `scripts/forge_governance_kernel_v1.py` (GOVERNANCE_VERSION=v3) |
| Legal arbitration | `scripts/forge_governance_legal_v3.py` |
| Economy / credits | `scripts/forge_economy_v1.py` |
| Cases | `~/.sina/forge-governance-cases-v3.json` |
| Precedent DB | `~/.sina/forge-governance-precedent-v3.json` |
| Latest judgment | `~/.sina/forge-governance-judgment-latest-v3.json` |
| Violations | `~/.sina/forge-governance-violations-v1.jsonl` |

---

## v3 upgrades over v2

| Capability | Behavior |
|------------|----------|
| Rule conflict detection | ALLOW + DENY across checks → mandatory arbitration |
| Case engine | Every conflict becomes a `LegalCase` with evidence |
| Judge panel | constitutional · economic · security · precedent |
| Constitutional court | Escalation when judges split |
| Precedent system | Rulings stored; influence future decisions |
| Appeals | Agents with reputation ≥ 0.6 may re-arbitrate |
| Enforcement | Judgment applies credits + reputation + permissions |

---

## Decision schema

`forge-governance-decision-v3` — fields: status, reason, legal (case + judgment), judgment_verdict

---

## Mac rule

Judges use deterministic stubs (no LLM) during founder session. `dry_run=true` skips penalty enforcement.

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```

E2E must pass governance v3 schema + legal case/arbitration checks.
