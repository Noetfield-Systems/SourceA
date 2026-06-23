---
name: hub-pro-mac-security
description: >-
  Mac Security Guard for Hub apps — Gatekeeper, codesign, notarization, TCC
  privacy, SIP, and why macOS may block agent scripts, .app launches, and
  machine actions. Use when Console shows crashes or activities are rejected.
---

# Hub Pro — Mac Security Guard

**Law:** `brain-os/law/enforcement/SINA_MAC_HEALTH_GUARD_LOCKED_v1.md`  
**Control plane:** `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md`

## What "Security Guard" means on your Mac

macOS layers that **reject or kill** agent/factory activity:

| Layer | What it blocks | Founder signal |
|-------|----------------|----------------|
| **Gatekeeper** | Unsigned / quarantined apps | "app is damaged" · won't open |
| **Codesign** | Tampered .app bundles | Crash on launch · Console EXC_BREAKPOINT |
| **TCC (Privacy)** | Accessibility, Full Disk, Automation | Script silently fails |
| **SIP** | System file edits | Operation not permitted |
| **Sandbox (Cursor)** | Network/shell limits | curl empty · tool rejected |
| **Launch Services** | Stale .app registration | Old icon · wrong binary runs |

## Desktop .app build protocol

```bash
# After build scripts (Worker Hub, Mac Health, etc.)
xattr -cr ~/Desktop/"Worker Hub.app"
codesign --force --deep --sign - ~/Desktop/"Worker Hub.app"
bash scripts/trust-portfolio-desktop-apps-v1.sh
```

Build scripts: `scripts/build-*-standalone-app-v1.sh` — sign + ditto to Desktop + Applications.

## Console crash reports — how to read

Path: `~/Library/Logs/DiagnosticReports/*.ips`

| Process | Usually means | Action |
|---------|---------------|--------|
| **WorkerHubShell** | Desktop Worker Hub.app crashed on launch | Rebuild app · single-instance · check log `~/.sina/worker-hub-app-launch.log` |
| **node** | n8n or dev Node process | Check which script spawned it |
| **railway** | Railway **CLI** crashed | Not cloud API — update CLI or use Hub proceed |
| **GoogleUpdater** | Chrome update | Ignore for SourceA |

**SIGTRAP / EXC_BREAKPOINT in SinaStandaloneShell.run** — often old .app build or double `NSApp.run()`. Rebuild from current `brand/macos-apps/*.swift`.

## TCC — agents need these for full automation

| Permission | Used for |
|------------|----------|
| Accessibility | Panic hotkey · menu bar stop |
| Full Disk Access | Log shield · large log scan |
| Automation (Apple Events) | Restart Cursor native action |

Scripts: `scripts/open-mac-health-panic-accessibility-v1.sh` · `install-mac-health-panic-hotkey-v1.sh`

## Form / agent submit guard (INCIDENT-037)

Flag: `~/.sina/form-agent-submit-forbidden-v1.flag`  
Only `hub_browser` / `m1_canvas` channels may write §ANSWERED. CLI spoof blocked.

## Mac Health "Security Guard" app vs macOS security

- **Mac Health Guard.app** = machine pressure monitor (:13024) — not Apple Gatekeeper
- **Gatekeeper** = macOS verifying app signatures
- Do not confuse UI "OFFLINE" with security block — check JS errors first

## When machines/agents are rejected

1. Read Console + `~/.sina/*-receipt*.json`
2. Check quarantine: `xattr -l /path/to/app`
3. Re-sign Desktop .app
4. For hub API: ensure `com.sourcea.hub` launchagent running
5. For Cursor sandbox: request `all` or `full_network` only when needed

## Founder session — do NOT run as security "proof"

- No `validate-all-e2e` on Mac body
- No 11+ min validator chains (INCIDENT-039 P0)
- Use Hub API Station + receipts instead
