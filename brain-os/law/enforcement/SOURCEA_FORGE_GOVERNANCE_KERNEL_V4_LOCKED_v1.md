# SourceA Forge Governance Kernel v4 (LOCKED)

**Saved:** 2026-06-25T18:00:00Z  
**Version:** 4.0 — LOCKED (geopolitical legal world layer)  
**Parent:** `SOURCEA_FORGE_GOVERNANCE_KERNEL_V3_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md`

---

## One law

> **Forge nations are legal systems — cross-border actions require treaties; violations trigger sanctions; disputes resolve via international court with treaty + precedent influence.**

---

## Modules

| Resource | Address |
|----------|---------|
| Governance kernel v4 | `scripts/forge_governance_kernel_v1.py` (GOVERNANCE_VERSION=v4) |
| Geopolitical legal | `scripts/forge_geopolitical_legal_v4.py` |
| Legal arbitration v3 | `scripts/forge_governance_legal_v3.py` |
| World state | `scripts/forge_world_state_v1.py` |
| Geo legal store | `~/.sina/forge-geopolitical-legal-v4.json` |
| Geo receipt | `~/.sina/forge-geopolitical-legal-latest-v4.json` |
| World state | `~/.sina/forge-world-state-v1.json` |

---

## Nations as legal systems

| Nation | Constitution | Jurisdiction |
|--------|--------------|--------------|
| nation-sourcea | controlled_automation | Mac control plane |
| nation-cloudforge | execution_body | Cloud execution |
| nation-labs | experimentation | Labs sandbox |

---

## v4 capabilities

| Feature | Behavior |
|---------|----------|
| Cross-border check | Agent home nation vs target nation |
| Treaties | Bilateral allowed_actions between nations |
| Sanctions | Block cross-border actions; severity decay on tick |
| International court | v3 arbitration + treaty moderation |
| Geo legal tick | Sync diplomacy graph to world state |

---

## API

```json
{ "action": "geo_sign_treaty", "party_a": "nation-sourcea", "party_b": "nation-labs", "terms": ["read_access"] }
{ "action": "geo_impose_sanction", "issuer": "nation-sourcea", "target": "nation-labs", "reason": "..." }
{ "action": "geo_legal_tick", "dry_run": true }
```

`govern()` runs geopolitical check first; cross-border DENY may escalate to international court.

---

## Mac rule

All geo operations are JSON-light stubs — safe on Mac founder session. `dry_run=true` default.

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```
