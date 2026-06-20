# Monitor disk live wire (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 LOCKED · **2026-06-10**

## Law

`:13021/monitor` is **disk-wired** — founder never sends an agent to refresh progress.

| Layer | Mechanism |
|-------|-----------|
| **Background** | `monitor_live_sync_v1.py` in dashboard server — 5s disk signature watch |
| **API** | `/api/validator-list?live=1` syncs then reads fresh `audit_monitor` |
| **Pulse** | `/api/monitor-pulse` lightweight disk sync |
| **UI** | `monitor.html` polls every **5s** · `Cache-Control: no-store` |
| **Sidecar** | `~/.sina/monitor-live-v1.json` last sync timestamp |

## Watched paths

`healthy-queue-*` · `worker-prompt-inbox` · `factory-*` · `REGISTRY.json` · receipts · broker events

## Always-on

Install: `cp scripts/com.sourcea.dashboard.plist ~/Library/LaunchAgents/ && launchctl load -w ~/Library/LaunchAgents/com.sourcea.dashboard.plist`

Or: `bash scripts/start-sourcea.sh`

## Founder respect

Scroll position preserved — see INCIDENT-018. Live data does not steal focus.
