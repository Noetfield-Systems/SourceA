# Sina Command — private agent loop packs (100 + 10)

> Superseded for founder UX by `SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md` — use **Private agents** sidebar pages, not a shared pack accordion.

| Pack ID | Repo | Catalog |
|---------|------|---------|
| `ai_dev_bridge_os` | AI Dev Bridge OS | `~/Desktop/AI Dev Bridge OS/prompts/loop-suggestions-100.json` |
| `trustfield` | TrustField Technologies | `~/Desktop/TrustField Technologies/prompts/loop-suggestions-100.json` |
| `virlux` | VIRLUX | `~/Desktop/VIRLUX/prompts/loop-suggestions-100.json` |
| `noetfield_local` | **Noetfield-All-Documents** (local only) | `~/Desktop/Noetfield-All-Documents/prompts/loop-suggestions-100.json` |

**Noetfield:** loop pack targets **local** documents only. Do **not** use `~/Desktop/Noetfield` (cloud/GitHub ship repo).

Each repo also has `loop-pack-10-active.json` (10 rounds for Agent loop UI).

## Founder workflow (clicks only — no Terminal)

1. Open **Sina Command** on Desktop → **Refresh**
2. Sidebar **Private agents** → e.g. TrustField page
3. Use that agent's **10-round prompts** table (TrustField, VIRLUX, AI Dev Bridge OS, Noetfield local/cloud, 777)
4. Tap **Start loop with this →** on a seed row (or type a goal → **Start loop**)
5. Open the matching repo in Cursor (not Terminal)
6. After each Cursor round: **Submit round → next prompt** (or let the executor auto-submit via API)
7. **Stop loop** anytime to abort

## Executors only (not founder)

CLI `activate-portfolio-loop.py` and `agent-loop-done.sh` exist for agents/CI. Founders must never run them. See `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md`.
