> **ARCHIVED 2026-07-05T13:00:00Z** — lineage only. See `docs/archive/superseded-law-v1/`.

# SourceA Forge Prompt OS Compiler v2 (LOCKED)

**Saved:** 2026-06-25T12:00:00Z  
**Version:** 2.0 — LOCKED (supersedes v1 routing for live compile path)  
**Parent:** `SOURCEA_FORGE_PROMPT_OS_COMPILER_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md`

---

## One law

> **Prompt OS v2 MUST learn from successful Forge executions — adaptive stack routing, evolved constraints, and outcome recording on every advisor/swarm completion.**

---

## Modules

| Resource | Address |
|----------|---------|
| v2 adaptive layer | `scripts/forge_prompt_os_compiler_v2.py` |
| v1 core (unchanged) | `scripts/forge_prompt_os_compiler_v1.py` |
| Compile receipt | `~/.sina/forge-prompt-os-compiler-latest-v2.json` |
| Learning store | `~/.sina/forge-prompt-os-learning-v2.json` |
| Schema | `forge-prompt-os-compiler-v2` |

---

## v2 upgrades over v1

| Capability | Behavior |
|------------|----------|
| Adaptive stack routing | Baseline v1 `select_stack` + learned override when intent/stack has ≥3 samples and higher success rate |
| Evolved constraints | Top 3 constraints with ≥70% success rate auto-injected per intent |
| Outcome recording | `record_execution_outcome()` after advisor_run / swarm completion |
| Stack bias | ±0.05 on success/fail per stack level (clamped ±0.5) |
| Complexity nudge | High complexity (>0.75) may bump stack when learned data supports next level |

---

## Pipeline

```
raw intent → v1 parseIntent + complexity
          → select_stack_adaptive (learning store)
          → generate_constraints_adaptive
          → buildPrompt → toForgeTask → cursor_mission
          → [execution] → record_execution_outcome
```

---

## API

```json
POST /api/forge-terminal/v1
{ "action": "compile_prompt", "text": "...", "adaptive": true }

{ "action": "advisor_run", "goal": "...", "compile": true }
```

`adaptive: false` falls back to v1-static routing inside v2 module.

---

## Mac rule

Learning store writes are light JSON — safe on Mac founder session. No LLM required for compile.

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```

E2E must include v2 schema, adaptive routing meta, and outcome recording.
