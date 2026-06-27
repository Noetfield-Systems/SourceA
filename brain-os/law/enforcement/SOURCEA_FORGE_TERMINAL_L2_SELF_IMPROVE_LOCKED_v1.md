# SourceA Forge Terminal L2 Self-Improve (LOCKED v1)

**Saved:** 2026-06-25T20:00:00Z  
**Version:** 1.0 — LOCKED  
**App version:** 2.9.1+ · port **13029**  
**Parent:** `SOURCEA_FORGE_TERMINAL_LIVING_DESKTOP_E2E_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_QUALITY_ENGINE_E2E_LOCKED_v1.md`

---

## One law

> **L2 self-improve runs patch-only agent repair when quality gate is REVISE or REJECT, re-gates up to 2 rounds on Mac, and writes receipt `~/.sina/forge-agent-self-improve-latest-v1.json` before any execute/cloud action.**

---

## Contract

| Field | Rule |
|-------|------|
| Trigger | Quality `verdict` ∈ {REVISE, REJECT} and `execution_allowed=false` |
| Auto-trigger | UI checkbox `opt-self-improve-l2` + post-`chat_turn` |
| Manual | Exec strip **Self-heal** button or `action: agent_self_improve` |
| Patch policy | `patch_file` preferred; `write_file` blocked when `patch_only=true` |
| Max rounds | 2 repair rounds (`MAX_REPAIR_ROUNDS`) |
| Re-gate | `quality_rerun` after each round when `run_id` present |
| Skip | Already PASS → `{skipped: true, reason: already_pass}` |

---

## Receipt schema: `forge-agent-self-improve-v1`

Path: `~/.sina/forge-agent-self-improve-latest-v1.json`

Required keys: `schema`, `level` (`L2`), `run_id`, `improved`, `repair_rounds`, `final_quality_gate`, `initial_verdict`, `final_verdict`, `at`.

Each `repair_rounds[]` entry: `round`, `agent_run_id`, `agent_steps`, `quality_before`, `quality_after`.

---

## API

```json
POST /api/forge-terminal/v1
{ "action": "agent_self_improve", "run_id": "ft-…", "dry_run": false }
```

Or inline: `{ "action": "agent_self_improve", "quality_gate": {…}, "text": "…" }`

---

## Mac control plane

- L2 runs on Mac (bounded tools, workspace-only paths).
- L3 cloud dispatch is separate law — default off on Mac founder session.
- No validator marathon — living E2E static + light harness only (INCIDENT-039).

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
python3 scripts/forge_terminal_ui_e2e_verify_v1.py
```

Receipt: `~/.sina/forge-terminal-living-ui-e2e-v1.json` must include `agent_self_improve` HTTP check when server live.
