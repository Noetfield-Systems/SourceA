# ASF Agent Desk — start here

**Organized entry:** `brain-os/law/entry/START_HERE_LOCKED_v1.md` · `brain-os/law/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md`

**Daily ops law:** `SINA_COMMAND_DEACTIVATED_INCIDENT_READ_POLICY_LOCKED_v1.md`  
**Hub:** Worker Hub only `http://127.0.0.1:13020/` · Sina Command / museum **deleted** (ASF 2026-06-23)

## Daily founder path (2026-06-14)

1. **Cursor Worker chat** — say **RUN INBOX** (one sa per turn)
2. **Optional glance:** Worker Hub → Next steps · Safety (`http://127.0.0.1:13020/`)
3. **Quote disk:** `factory_now_line` from `~/.sina/agent-live-surfaces-v1.json` — chat transcript is not SSOT

**Session start (agents):** `python3 scripts/agent_session_gate_run_v1.py --role <role> --json`

## Refresh fleet progress (executor only)

```bash
cd ~/Desktop/SourceA && ./scripts/update-program-progress.sh
```

## Legacy monolith (deleted — git history only)

Sina Command museum removed 2026-06-23 · `scripts/uninstall-sina-command-v1.sh` · law `ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md`

Morning brief: `./scripts/sina-morning-brief.sh`

## Registry

`data/agent_fleet/AGENT_FLEET_REGISTRY.json`

## Goal 1 factory (current law)

**Cursor AUTO-RUN / Hub ▶ START WORKER BATCH = STALE.** Execution = **RUN INBOX** in Worker chat when Brain routes and kill flag allows.

1. Open **Cursor** → workspace `~/Desktop/SourceA` → **SourceA Worker** chat
2. Founder says **RUN INBOX** (or bounded `ASF: Cloud Forge Run — max 1`)
3. Executor runs one CHECK/ACT/VERIFY turn · broker-submit · STOP

**Law:** `ACTIVE_NOW.md` · `brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` · INCIDENT-028/031

## For agents

1. Session gate + truth bundle — not incident compendium
2. Lane brief from disk / `scripts/lane_briefs.py` when repo-specific
3. One thread per chat (`ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md`)
4. End session with VERIFY per `AGENT_OUTPUT_CONTRACT_v1.yaml`
