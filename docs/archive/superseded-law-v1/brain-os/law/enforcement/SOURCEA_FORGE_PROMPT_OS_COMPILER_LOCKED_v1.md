> **ARCHIVED 2026-07-05T13:00:00Z** — lineage only. See `docs/archive/superseded-law-v1/`.

# SourceA Forge Prompt OS Compiler (LOCKED v1)

**Saved:** 2026-06-25T07:00:00Z  
**Version:** 1.0 — LOCKED  
**Parent:** `SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md`

---

## One law

> **Raw founder intent MUST pass through Prompt OS Compiler before Forge kernel/swarm execution — structured task, stack level L1–L7, constraints, and execution spec.**

---

## Module

| Resource | Address |
|----------|---------|
| Compiler | `scripts/forge_prompt_os_compiler_v1.py` |
| Receipt | `~/.sina/forge-prompt-os-compiler-latest-v1.json` |
| Schema | `forge-prompt-os-compiler-v1` |

---

## Pipeline

```
raw intent → parseIntent → selectStack (L1–L7)
          → resolveContext (Forge state) → generateConstraints
          → buildPrompt → toForgeTask → cursor_mission
```

---

## Stack levels

| Level | Typical intent | Execution |
|-------|----------------|-----------|
| L1 | general_build | single / read intelligence |
| L2 | feature_addition | agent_dev_loop |
| L3 | transformation, repair | L2/L3 kernel |
| L4 | optimization | kernel + optimizer |
| L5 | system_design | swarm |
| L6 | swarm, high complexity | parallel swarm |
| L7 | deployment | cloud swarm dispatch |

---

## API

```json
POST /api/forge-terminal/v1
{ "action": "compile_prompt", "text": "add auth to forge terminal", "workspace_path": "..." }
```

Optional on advisor_run: `"compile": true` prepends compiler spec.

---

## Mac rule

Compiler always runs on Mac (light, no LLM required). Execution follows stack routing with `dry_run=true` default.

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```

E2E must include `compile_prompt` action check.
