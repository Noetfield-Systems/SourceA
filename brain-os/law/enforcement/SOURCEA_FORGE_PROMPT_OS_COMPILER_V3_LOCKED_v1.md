# SourceA Forge Prompt OS Compiler v3 (LOCKED)

**Saved:** 2026-06-25T14:00:00Z  
**Version:** 3.0 — LOCKED (autonomous runtime supersedes compile-only path for execution)  
**Parent:** `SOURCEA_FORGE_PROMPT_OS_COMPILER_V2_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md`

---

## One law

> **Prompt OS v3 MUST execute compiled specs autonomously — prompt → compile → kernel/swarm → deployment hint → learn — without requiring Cursor in the loop.**

---

## Modules

| Resource | Address |
|----------|---------|
| v3 autonomous runtime | `scripts/forge_prompt_os_compiler_v3.py` |
| v2 adaptive layer | `scripts/forge_prompt_os_compiler_v2.py` |
| v1 core | `scripts/forge_prompt_os_compiler_v1.py` |
| Runtime receipt | `~/.sina/forge-prompt-os-runtime-latest-v3.json` |
| Runtime queue | `~/.sina/forge-prompt-os-runtime-queue-v3.json` |
| Schema | `forge-prompt-os-runtime-v3` |

---

## v3 upgrades over v2

| Capability | Behavior |
|------------|----------|
| Autonomous execute | `autonomous_execute()` — full compile → route → run → learn loop |
| Stack routing | L1–L2 → `agent_dev_loop` · L3–L4 → patch-aware dev · L5–L6 → swarm · L7 → cloud deploy |
| Deployment phase | L7/deployment intents get cloud dispatch + deployment receipt |
| Runtime queue | Last 100 autonomous runs in queue JSON |
| No Cursor required | Mission compiled and executed via Forge kernels directly |

---

## Pipeline

```
raw intent → v2 adaptive compile
          → route_execution (stack → executor)
          → agent_dev_loop | run_swarm_loop | dispatch_swarm_cloud
          → deployment_phase (L7)
          → record_execution_outcome
```

---

## API

```json
POST /api/forge-terminal/v1
{ "action": "autonomous_run", "text": "add auth module", "workspace_path": "...", "dry_run": true }

{ "action": "compile_prompt", "text": "...", "adaptive": true }
```

`compile_prompt` returns v3 envelope with `suggested_route`. `autonomous_run` executes end-to-end.

---

## Mac rule

`dry_run=true` default on Mac founder session. L7 cloud deploy queues to cloud body — never Mac heavy execution.

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```

E2E must include v3 schema, autonomous_run API, and runtime receipt.
