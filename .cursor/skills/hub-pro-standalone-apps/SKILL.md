---
name: hub-pro-standalone-apps
description: >-
  Hub Pro standalone desktop apps — Worker Hub.app, Mac Health Guard.app, Chat
  Unify, n8n Integration. WKWebView shell, embedded Python server, build/sync
  protocol, single-instance launch.
---

# Hub Pro — Standalone desktop apps

## Architecture

```text
Double-click .app
  → Swift shell (MacHealthShell / WorkerHubShell)
  → start embedded Python server if health fails
  → WKWebView loads http://127.0.0.1:<port>/
```

| App | Swift | Server | Port | Bundle path |
|-----|-------|--------|------|-------------|
| Worker Hub | `WorkerHubShell.swift` | `sina-command-server.py` | 13020 | `worker-hub-bundle/` |
| Mac Health | `MacHealthShell.swift` | `mac-health-guard-server.py` | 13024 | `mac-health-bundle/` |
| Chat Unify | `ChatUnifyShell.swift` | chat unify server | 13023 | `chat-unify-bundle/` |
| n8n | `N8nIntegrationShell.swift` | n8n glue server | 13026 | `n8n-integration-bundle/` |

## Build commands

```bash
bash scripts/build-worker-hub-standalone-app-v1.sh      # → Desktop/Worker Hub.app
bash scripts/build-mac-health-standalone-app-v1.sh    # heavy gate — ship window only
bash scripts/build-chat-unify-standalone-app-v1.sh
bash scripts/build-n8n-integration-standalone-app-v1.sh
```

## SSOT vs bundle sync

| Edit target | Serves live when |
|-------------|------------------|
| `scripts/mac-health-standalone/` | Server uses SourceA path (dev) |
| `brand/.../mac-health-bundle/app/` | Desktop .app only |
| `agent-control-panel/` | Hub :13020 (after kickstart) |

**Always copy or rebuild** after standalone edits if founder uses Desktop .app.

## Single-instance (Worker Hub crash fix Jun 2026)

```swift
SinaStandaloneShell.prepareApp(bundleId: "com.sina.workerhub.standalone")
```

Second double-click activates existing window — prevents 7× crash loop in Console.

## Logs

| App | Log |
|-----|-----|
| Worker Hub | `~/.sina/worker-hub-app-launch.log` |
| Mac Health | `~/.sina/mac-health-app-launch.log` |
| Mac Health server | `~/.sina/mac-health-guard-server.log` |

## Native bridge (Mac Health only)

Swift `NativeBridge` handles actions web cannot do:
- `restart_cursor` — detached Python
- `emergency_stop` — panic flag
- Menu: ⛔ Stop agents · Restart Cursor

## SinaAppRouter

Shared cross-app navigation in WKWebView — `brand/macos-apps/SinaAppRouter.swift`. Rebuild all apps after router changes: `scripts/build-sina-apps-router-v1.sh` (if exists) or individual build scripts.

## Checklist before ship

- [ ] Cold-start: health OK within 15s
- [ ] Window loads UI (not "Heart failed")
- [ ] codesign PASS
- [ ] Desktop + Applications copies ditto'd
- [ ] Append `hub-pro-app-experience-log` entry
