# Agent Conflict Room — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Authority:** `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` (ACE v3)  
**Companion:** Incident Room · Private agent workspaces

## Purpose

One place for **all agents** to report clashes, asks, and “which law wins?” questions. An **intermediary ACE auto-triage** (rule-based in the hub) classifies and answers when possible.

## Non-negotiable workflow

1. **Report** in Sina Command → **Conflict Room** (or API).
2. **Read ACE guidance** on the same screen.
3. **Return to work** — next `plan.json` task that is not gated by this clash.
4. **Never** freeze the whole project waiting for ASF or another agent’s reply.

| ACE type | Meaning | Agent behavior |
|----------|---------|----------------|
| **A** | Informational drift | Tag planes [DESIGN]/[EXECUTION]/[DELIVERY]; continue |
| **B** | Structural | Check GLOBAL_BLOCKERS / alignment docs; continue non-gated work |
| **C** | Boundary | Agent report only; never edit forbidden roots; continue repo work |

## Storage

| What | Path |
|------|------|
| All cases | `~/.sina/conflict-room/cases.jsonl` |
| Per-agent copy | `~/.sina/agent-workspaces/<id>/conflict-reports.jsonl` |

## API

- `GET /api/conflict-room?agent_id=...`
- `POST /api/conflict-room` — `submit`, `close`, `list`

## Auto-triage (intermediary)

Implemented in `scripts/agent_conflict_room.py` → `ace_auto_triage()`.  
Re-reads ACE v3 types; does **not** block `continue_work`.

When ACE cannot fully resolve → status `queued_asf` (ASF reviews when convenient). Agent still continues.

## Founder

One-tap **GLOBAL_BLOCKERS** and **Backlog** from Actions — no Terminal.
