# Agent Pro v1

**Standalone agent surface.** Does not read, import, or copy from the legacy Sina Command hub or any SourceA disk payloads.

## UX patterns

| Surface | Purpose |
|---------|---------|
| **Composer** | Delegate work in natural language |
| **Inbox** | Delegated tasks — you stay accountable, agent executes |
| **Session** | Planner tab + output log, live step stream |

Not consumer apps. Not the legacy hub.

## Run

```bash
python3 /Users/sinakazemnezhad/Desktop/SourceA/agent-pro-v1/server.py
```

Open: **http://127.0.0.1:13050**

## Live by default

- **SSE** `/api/events` — every plan step and inbox change pushes to the UI automatically
- No 2.7MB JSON, no 45 tabs, no factory-drain jargon

## Wire real agents later

Replace in-memory `_run_session()` in `server.py` with your chosen agent backend. UI stays the same.

## Legacy hub

`:13020` Sina Command is **frozen**. Do not use it as the product surface.
