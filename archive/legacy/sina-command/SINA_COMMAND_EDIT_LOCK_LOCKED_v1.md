# Sina Command edit lock (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 · **Supersession:** 2026-06-07 — see §Supersession below

## Law

**No agent may edit Sina Command application code** except:

1. **ASF** — human founder (direct edits, any tool)
2. **SourceA Worker chat** — sole implementation lane (`MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` · `WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md` §2)

## §Supersession (June 2026)

| Retired | Replacement |
|---------|-------------|
| **SinaaiDataBase Cursor chat** as Command maintainer | **Archive/broker only** — `SINAAIDB_ARCHIVE_RETIREMENT_HANDOFF_LOCKED_v1.md` — **no build assignments** |
| Separate FORGE builder chat | **Same SourceA Worker** edits `~/Desktop/forge/` when Brain routes FORGE tasks |

Historical references to “sinaai_maintainer” or “HQ maintainer” in older notices mean **SourceA Worker under Brain handoff** unless ASF reopens a dedicated maintainer chat in new LOCKED law.

This includes:

- `~/Desktop/SourceA/` (hub, panel, scripts, rules for Command)
- `agent-control-panel/` UI and assets
- `scripts/sina-command-server.py` and all loop/advisor/site-guide modules

## All other agents (every other Cursor chat, SEMEJ, portfolio repos, cloud agents)

- **READ** Sina Command behavior via the running app (`http://127.0.0.1:13020`) — do not patch code
- **REPORT** issues via API or Backlog UI:

```bash
curl -s -X POST http://127.0.0.1:13020/api/agent-review \
  -H "Content-Type: application/json" \
  -d '{
    "action": "submit",
    "title": "Short title",
    "detail": "What is wrong, where you saw it, steps",
    "severity": "high",
    "category": "bug",
    "workspace": "TrustField Technologies",
    "reporter": "cursor-agent-trustfield"
  }'
```

Founder does **not** run curl — use **Backlog → Agent reports** in Sina Command.

## Triage

- **Backlog** tab → **Agent reports** section
- ASF or maintainer chat marks: triaged → in progress → done / wontfix
- Only maintainer chat implements fixes in `SourceA`

## Manifest

Live lock file: `~/.sina/command-edit-lock.json`  
Reviews log: `~/.sina/agent-command-reviews.jsonl`
