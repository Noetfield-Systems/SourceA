# Mac Daily Cleanup — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T21:00:00Z · **Authority:** Founder — Mac + Cursor hygiene  
**Orchestrator:** `scripts/mac_daily_cleanup_v1.py` · **Shell:** `scripts/mac-daily-cleanup-v1.sh`  
**Cursor module:** `scripts/cursor_session_relief_v1.py`  
**Receipt:** `~/.sina/mac-daily-cleanup-latest-v1.json`

---

## Problem

Heavy agent days bloat **Cursor RAM** (renderer 2–4 GB · 6+ extension-hosts) and **Mac factory junk** (motors · playwright · logs). Mac Health handles body pressure; Cursor needs its own daily reset.

---

## Tiers (agents run — founder taps only when sluggish)

| Tier | When | What |
|------|------|------|
| **morning** | Start work | Log caps · Cursor trim · never-again salvage |
| **mid** | Every 2h / before exhaustion | Factory hog kill · prevention · Mac cool down · Cursor trim |
| **night** | End of day | mid + Cursor restart if bloated |
| **full** | After huge day | night hard · control plane enter |

---

## Founder commands (Hub Actions / one script)

```bash
bash ~/Desktop/SourceA/scripts/mac-daily-cleanup-v1.sh --morning
bash ~/Desktop/SourceA/scripts/mac-daily-cleanup-v1.sh --mid
bash ~/Desktop/SourceA/scripts/mac-daily-cleanup-v1.sh --night --restart-cursor
bash ~/Desktop/SourceA/scripts/cursor-day-relief-v1.sh --restart
bash ~/Desktop/SourceA/scripts/founder-mac-reset-v1.sh --hard
```

---

## Auto restart thresholds (Cursor)

- Renderer **> 2.8 GB**, or total Cursor **> 5.5 GB**, or **4+ extension-hosts**

---

## Wired into

| Surface | Wire |
|---------|------|
| Mac Health live pulse | `cursor_session` probe on every pulse |
| Mac Health prevention | auto Cursor **trim** when `cursor_busy` (never auto restart) |
| Founder work mode | `enter-mac-control-plane-v1.sh` → morning tier |
| LaunchAgent | `install-mac-daily-cleanup-launchagent-v1.sh` → mid every 2h |
| `founder-mac-reset-v1.sh` | full night / hard path |

---

## One-time fix

Install Cursor to `/Applications/Cursor.app` — not DMG volume.
