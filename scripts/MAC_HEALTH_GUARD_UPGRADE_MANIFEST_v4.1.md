# Mac Health Guard Upgrade Manifest — v4.1.0 addendum

**Saved:** 2026-07-06T06:00:00Z  
**Version SSOT:** `scripts/mac_health_version_v1.py` → **4.1.0**

## W2 wave summary

| Plan | Focus |
|------|--------|
| M111-112 | SourceA path resolution SSOT (`resolve_sourcea_root_v1.sh`) |
| M111-113 | Desktop `.app` v4.1 rebuild + bundle parity |
| M111-114 | Cloud glance read-only — Railway · CF cron · Mac control plane flag |
| M111-115 | LaunchAgent heart reliability + PID file |
| M111-116 | Log Shield UI + disk relief |
| M111-117 | Panic hotkey + emergency stop drill |
| M111-118 | Founder glance UI contract 4.1 |
| M111-119 | Prevention + Cursor hot tiers |
| M111-120 | Native Swift bridge parity |
| M111-121 | W2 ship gate |

## v4.1.0 shipped

- **Path fix:** All launchers source `resolve_sourcea_root_v1.sh` — real repo `~/Desktop/Noetfield-Systems/SourceA`.
- **Cloud glance:** `mac_health_cloud_glance_v1.py` probes Railway, CF loop cron, Hub `:13020`, `~/.sina/mac-control-plane-v1.flag`.
- **UI:** `cloud-glance-strip` truncate + title; click = read-only refresh (no cloud dispatch POST).
- **LaunchAgent:** Wrapper health-check before restart; `ThrottleInterval` 30s; PID file synced.
- **Validators:** `validate-mac-health-path-ssot-v1.sh`, extended `validate-mac-health-cloud-glance-v1.sh`.
- **Ledger:** `UP-MH-004` — W2 Mac Health hardening shipped.

## Founder session law

Mac founder session: `bash scripts/validate-mac-health-ship-fast-v1.sh` only. Full e2e: `SOURCEA_CI=1 bash scripts/validate-mac-health-e2e-v1.sh` on cloud CI.

## Open heart

```bash
bash scripts/serve-mac-health-guard.sh
open http://127.0.0.1:13024/
```
