# SourceA Forge Self-Building Stack (LOCKED v1–v6)

**Saved:** 2026-06-25T20:00:00Z  
**Version:** 1.0 — LOCKED  
**Parent:** `SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md`

---

## One law

> **Forge self-building MUST be controlled recursion — introspect → gap → generate → prove → integrate — with governance + legal layers immutable and `dry_run=true` default on Mac.**

---

## Stack modules

| Layer | Module | Receipt |
|-------|--------|---------|
| v1 Self-build | `scripts/forge_self_build_v1.py` | `~/.sina/forge-self-build-latest-v1.json` |
| v2 Safe proof compiler | `scripts/forge_self_build_v2.py` | `~/.sina/forge-self-build-proof-latest-v2.json` |
| v3 Swarm evolution | `scripts/forge_self_build_v3.py` | `~/.sina/forge-self-build-swarm-latest-v3.json` |
| v4 Civ code evolution | `scripts/forge_civilization_code_v4.py` | `~/.sina/forge-civilization-code-tick-latest-v4.json` |
| v5 Digital nation OS | `scripts/forge_digital_nation_v5.py` | `~/.sina/forge-digital-nation-tick-latest-v5.json` |
| v6 World system | `scripts/forge_world_system_v6.py` | `~/.sina/forge-world-system-tick-latest-v6.json` |

Registry: `~/.sina/forge-self-build-registry-v1.json` · Rollback: `~/.sina/forge-self-build-rollback-v2.json`

---

## Safety (all versions)

- Max recursion depth = 10
- No `system_override` / destructive patterns in generated code
- v2+: proof confidence ≥ 0.85 required
- Governance v4 + legal v3 remain immutable gates
- Mac: dry_run stubs only — cloud for live LLM generation

---

## API

```json
{ "action": "self_build_tick", "dry_run": true }
{ "action": "self_build_safe_evolve", "dry_run": true }
{ "action": "self_build_swarm_evolve", "dry_run": true }
{ "action": "civilization_code_tick", "dry_run": true }
{ "action": "world_system_tick", "dry_run": true }
```

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```
