> **ARCHIVED 2026-07-05T13:00:00Z** — lineage only. See `docs/archive/superseded-law-v1/`.

# SourceA Forge Governance Kernel (LOCKED v1)

**Superseded by:** `SOURCEA_FORGE_GOVERNANCE_KERNEL_V2_LOCKED_v1.md` (economy-aware v2)

**Saved:** 2026-06-25T05:00:00Z  
**Version:** 1.0 — LOCKED  
**Parent:** `SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_V4_CIVILIZATION_LOCKED_v1.md`

---

## One law

> **Every agent tool action MUST pass `forge_governance_kernel_v1.govern()` before execution — ALLOW / DENY / MODIFY. No bypass.**

---

## Module

| Resource | Address |
|----------|---------|
| Governance kernel | `~/Desktop/SourceA/scripts/forge_governance_kernel_v1.py` |
| Violations log | `~/.sina/forge-governance-violations-v1.jsonl` |
| Latest decision | `~/.sina/forge-governance-latest-v1.json` |

---

## Decision pipeline

```
Agent action → check_permission → validate_memory_write (if memory_write)
            → execution_firewall → ALLOW | DENY
```

---

## Role permissions

| Role | Tools |
|------|-------|
| planner | read_file, list_files, search_code, search_semantic, repo_index |
| builder | read/write/patch, apply_git_patch, run_shell, search_*, repo_index |
| critic | read_file, list_files, search_code, run_shell |
| repair | read_file, list_files, search_code, patch_file |
| optimizer | read_file, list_files, search_code |
| deployer | deploy (requires approval flag) |

---

## Immutable rules

1. No agent may exceed assigned permissions  
2. No destructive system commands  
3. No memory overwrite without validation  
4. All deployments must pass firewall  
5. All patches must be verifiable  

---

## Integration

Wired in:

- `ForgeAgentTools.execute()` — `scripts/forge_agent_kernel_v1.py`
- `ForgeSwarmTools.execute()` — `scripts/forge_agent_kernel_v3_swarm.py`

---

## v6 world simulation (stub only)

**Not production geopolitics.** Stub: `scripts/forge_world_state_v1.py` · `~/.sina/forge-world-state-v1.json`

Three seed nations: SourceA Mac · Cloud Forge Railway · Labs Sandbox.

Full v6 multi-nation conflict/trade = cloud simulation only when founder arms.

---

## Proof

```bash
python3 -m py_compile scripts/forge_governance_kernel_v1.py
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```

E2E must include governance kernel module check.
