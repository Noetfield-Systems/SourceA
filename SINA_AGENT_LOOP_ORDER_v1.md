# Sina Agent Loop — 10 rounds (LOCKED)

**Three layers:** See `SINA_PROMPT_FAST_LOOP_LOCKED_v1.md` — this doc is **factory / execution loop only**.  
**Meta (prompt-direction 10)** = planning queue in app. **Do not run both full 10×10** for one P0 without explicit orchestration sprint.  
**Auto-paste into Cursor is OFF** — `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md`.

## Roles

| Role | Who |
|------|-----|
| **Founder** | **Clicks only** in Sina Command — Start, Submit round, Stop, pack buttons |
| **Planner** | OpenRouter in hub — next prompt after each answer |
| **Executor** | Cursor coding agent — builds; may POST API response |
| **Hub** | `sina-command-server.py` — stores history; round text in **app + INBOX only** (no Cursor paste) |

## Founder flow (no Terminal)

1. Sina Command → **Refresh** → sidebar **Private agents** → agent page (or **Agent hub** for index)
2. On that agent's page: use **10-round prompts** (if pack) → **Start loop with this →**
3. Cursor works on `[SINA_LOOP n/10]`
4. **Submit round → next prompt** (gold card or sticky bar) — or executor auto-submits
5. Repeat until 10 — **Stop loop** anytime

See `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md`.

## Executor flow (Cursor agent — not founder)

When `[SINA_LOOP` or inbox active:

1. Read `.sina-loop/INBOX.md`
2. Do the work
3. POST response (preferred — founder does not paste):

```bash
curl -s -X POST http://127.0.0.1:13020/api/agent-loop \
  -H "Content-Type: application/json" \
  -d '{"action":"response","summary":"…","response":"…"}'
```

Or run `~/Desktop/SourceA/scripts/agent-loop-done.sh` (executor/CI only).

## Start loop (executor or API — not founder shell habit)

```bash
curl -s -X POST http://127.0.0.1:13020/api/agent-loop \
  -H "Content-Type: application/json" \
  -d '{"action":"start","goal":"YOUR GOAL","trigger_source":"cursor_chat","max_rounds":10}'
```

Founders use **Start loop** button instead.

Requires OpenRouter in vault. **No** Cursor inject by default — founder reads round in Private agents or opens INBOX when choosing to work in this chat.
