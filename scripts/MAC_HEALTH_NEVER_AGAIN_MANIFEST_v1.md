# Mac Health Never Again — Permanent Guards (v3.2.1)

Ship date: 2026-06-17  
Prevents recurrence of Jun 2026 Mac incidents.

## Incidents locked out

| Incident | Guard |
|----------|--------|
| 699 GB `command-server.log` bomb | Log cap 50 MiB · tail-only fail snippet · never-again auto-truncate |
| 50+ `fbe_motor_delegate` storm | Motor soft cap 8 → pause autorun · hard cap 15 → SIGTERM · autorun guard wrapper |
| Hub /health urlparse crash | Fixed in `sina-command-server.py` |
| Playwright film heat | `commercial-film-render-frozen-v1.flag` + all entry points + never-again recreate if missing |
| Cursor 300% auto-stop gap | Emergency stop kills `fbe_motor`, `agent_rules_loop`, `anti_staleness` |
| Codex + Cursor dual GPU | Founder ops — Codex quit during focus; not auto-killed |
| Cursor from DMG | Never-again probe warns on every live pulse |

## New files

- `scripts/mac_health_never_again_v1.py` — log cap, motor reaper, film default freeze, Cursor DMG detect
- `scripts/autorun_worker_guard_v1.sh` — launchd exits 0 when pause flag present
- `scripts/validate-mac-health-never-again-v1.sh` — gate

## Modified

- `mac_health_log_shield_v1.py` — motor surge 8, never-again wired every pulse
- `mac_health_emergency_stop_v1.py` — expanded kill patterns
- `mac_focus_freeze_v1.py` — respects emergency-active flag
- `anti_staleness_auto_wire_v1.py` — always skips on focus freeze
- `agent_rules_loop_orchestrator.py` — all phases skip on focus freeze
- `auto_start_worker_batch_on_hub_v1.sh` — exits when paused
- `com.sourcea.autorun-worker.plist` — uses guard wrapper
- `mac_health_version_v1.py` → **3.3.0** · `founder_glance`

## Receipt

`~/.sina/mac-health/never-again-latest-v1.json` — updated every live pulse (side effects on).

## Config (optional)

`~/.sina/config/mac-health-never-again-v1.json` — override caps.

## Re-enable factory

```bash
rm ~/.sina/auto-run-disabled-v1.flag
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.sourcea.autorun-worker.plist
```

## Unfreeze film (after Screen Studio + critic PASS only)

```bash
bash ~/Desktop/SourceA/sourcea-commercial-film-ship.sh
```

## Agent mandates (Mac Law — mandatory)

**Law:** `~/Desktop/MacLaw/MAC_HEALTH_AGENT_MANDATES_LOCKED.md`  
**Enforce:** `scripts/mac_health_agent_mandates_v1.py` (every live pulse via never-again)  
**Gate:** `bash scripts/validate-mac-health-agent-mandates-v1.sh`  
**Cursor rule:** `.cursor/rules/mac-health-agent-mandates.mdc` (alwaysApply)

Agents MUST NOT: re-enable sounds · unfreeze film · bootstrap autorun/panic · read multi-GB hub logs.
