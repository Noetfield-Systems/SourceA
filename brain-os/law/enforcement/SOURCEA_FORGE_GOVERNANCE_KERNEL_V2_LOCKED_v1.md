# SourceA Forge Governance Kernel v2 (LOCKED)

**Saved:** 2026-06-25T06:00:00Z  
**Version:** 2.0 — LOCKED (supersedes v1 law)  
**Parent:** `SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_V4_CIVILIZATION_LOCKED_v1.md`

---

## One law

> **Governance v2 is economy-aware: every allowed action debits FORGE credits; violations incur penalties; reputation tiers dynamically restrict tools.**

---

## Modules

| Resource | Address |
|----------|---------|
| Governance kernel v2 | `scripts/forge_governance_kernel_v1.py` (GOVERNANCE_VERSION=v2) |
| Economy / credits | `scripts/forge_economy_v1.py` |
| Credit accounts | `~/.sina/forge-economy-v1.json` |
| Violations | `~/.sina/forge-governance-violations-v1.jsonl` |
| Latest decision | `~/.sina/forge-governance-latest-v1.json` |

---

## Reputation tiers

| Tier | Reputation | Tool access |
|------|------------|-------------|
| trusted | ≥ 0.7 | Full role permissions |
| standard | 0.4 – 0.69 | No deploy |
| probation | 0.25 – 0.39 | read, list, search only |
| restricted | < 0.25 | read_file, list_files only |

Agent `status` synced: active · probation · restricted

---

## Economy

- Currency: **FORGE_CREDITS** (default balance 100 per agent)
- Nation tax: 5% on each action debit
- Violation penalty: 2.0 credits + reputation −0.15
- Swarm success reward: +1.0 credit to top agents

Action costs (examples): read_file 0.05 · patch_file 0.4 · run_shell 1.0 · deploy 5.0

---

## Decision schema

`forge-governance-decision-v2` — fields: status, reason, reputation_tier, economy (charge row)

---

## Mac rule

`dry_run=true` skips credit charge; reputation checks still apply unless testing with explicit dry_run in govern().

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```

E2E must pass governance v2 + economy checks.
