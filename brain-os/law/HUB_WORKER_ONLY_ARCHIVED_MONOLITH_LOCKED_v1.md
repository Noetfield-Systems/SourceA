# Worker Hub only — monolith archived — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13  
**Authority:** Founder directive — heavy Sina Command hub is a blocker; archive it.

## What ships now

| Surface | URL | Role |
|---------|-----|------|
| **Worker Hub** (default) | `http://127.0.0.1:13020/` | Worker task · queue · Safety · policy links · light refresh |
| **Legacy monolith** (archived) | `http://127.0.0.1:13020/legacy/` | Old 10k-line panel — maintenance only, not daily use |

## Worker Hub does ONE job

1. Show **current worker task** (inbox + queue head)
2. Show **factory FREEZE / queue position**
3. **Safety check** one tap
4. **Light refresh** one tap (~1s, no rebuild)
5. **Policy links** open law docs logged (no embedded 9MB JSON)

Rules, commercial policy, governance systems stay on **disk + Actions in legacy** — not loaded into the default hub.

## Monolith archived (do not extend)

- `agent-control-panel/assets/app.js` (~480 KB) — frozen at `/legacy/`
- `command-data.json` (9.7 MB) — builder/worker only; Worker Hub never fetches it
- `build-sina-command-panel.py` — ASF strict-hub / legacy maintenance only

## API

- `GET /api/worker-hub/v1` — single ~2 KB payload (`scripts/worker_hub_v1.py`)
- `POST /refresh` `{mode:"light"}` — default
- `POST /api/action` `{id:"founder-ecosystem-safety"}` — no full rebuild on safety

## Commercial

PLAN-300 / 11.01–11.03 **not blocked** — execute from Worker + Cursor, not legacy hub tabs.

**Supersedes for daily use:** `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` · `HUB_LITE_REBUILD_PHASE0_LOCKED_v1.md`
