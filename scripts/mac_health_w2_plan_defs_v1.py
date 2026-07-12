"""Mac Health W2 — 10 upgrade plans × 10 steps (M111-112..121)."""
from __future__ import annotations

from typing import Any

from mac_health_edition_v1 import IS_PERSONAL

# (plan_id, title, epic, steps: list of (title, wired_to, acceptance))
W2_PLAN_SPECS: list[tuple[str, str, str, list[tuple[str, str, str]]]] = [
    (
        "M111-112",
        "SourceA path resolution SSOT",
        "E01",
        [
            ("Wire resolve_sourcea_root into install-mac-health-launchagent-v1.sh", "scripts/install-mac-health-launchagent-v1.sh", "start-mac-health-heart.sh sources resolver"),
            ("Wire resolver into panic hotkey + listener plists", "scripts/install-mac-health-panic-hotkey-v1.sh", "SINA_SOURCEA uses Noetfield path"),
            ("Bundle copy list includes cloud glance + resolver deps", "scripts/build-mac-health-standalone-app-v1.sh", "bundle has resolve_sourcea_root_v1.sh"),
            ("MacHealthShell.swift CFBundleShortVersionString 4.1.0", "brand/macos-apps/MacHealthShell.swift", "plist version 4.1.0"),
            ("validate-mac-health-path-ssot-v1.sh PASS", "scripts/validate-mac-health-path-ssot-v1.sh", "no stale Desktop/SourceA default"),
            ("Log resolved root on server start", "scripts/mac-health-guard-server.py", "log line has sourcea_root"),
            ("Law doc mentions resolve_sourcea_root_v1.sh", "brain-os/law/SINA_MAC_HEALTH_GUARD_LOCKED_v1.md", "resolve_sourcea_root cited"),
            ("LaunchAgent install uses resolver", "scripts/install-mac-health-launchagent-v1.sh", ":13024/health ok"),
            ("Receipt mac-health-path-ssot-receipt-v1.json", "~/.sina/mac-health-path-ssot-receipt-v1.json", "ok:true"),
            ("M111-112 pulse 10/10 steps", "scripts/ecosystem_mac_health_111_plan_pulse_v1.py", "w2 plan done"),
        ],
    ),
    (
        "M111-113",
        "Desktop .app v4.1 rebuild",
        "E01",
        [
            ("sync-standalone-apps-to-bundles-v1.sh fresh", "scripts/sync-standalone-apps-to-bundles-v1.sh", "bundle dir synced"),
            ("run-mac-health-recipe ship-fast pre-build", "scripts/run-mac-health-recipe-v1.sh", "ship-fast PASS"),
            ("build-mac-health-standalone-app-v1.sh", "scripts/build-mac-health-standalone-app-v1.sh", "Mac Health Guard.app exists"),
            ("validate-mac-health-bundle-parity-v1.sh", "scripts/validate-mac-health-bundle-parity-v1.sh", "SSOT == bundle"),
            ("Bundle MAC_HEALTH_BUNDLE_ROOT offline start", "brand/macos-apps/MacHealthShell.swift", "bundle fallback works"),
            ("Native Restart Cursor smoke", "brand/macos-apps/MacHealthShell.swift", "__mhgNativeDone fires"),
            ("codesign verify on .app", "scripts/build-mac-health-standalone-app-v1.sh", "codesign ok"),
            ("lsregister refresh", "scripts/build-mac-health-standalone-app-v1.sh", "Finder icon ok"),
            ("Copy to ~/Applications", "scripts/build-mac-health-standalone-app-v1.sh", "both paths same version"),
            ("bundle parity receipt + UP-MH-004 partial", "data/ui-upgrade-ledgers/mac_health-v1.json", "version 4.1.0"),
        ],
    ),
    (
        "M111-114",
        "Cloud glance v4.1 read-only",
        "E01",
        [
            ("validate-mac-health-cloud-glance cf_loop + control plane", "scripts/validate-mac-health-cloud-glance-v1.sh", "cf_loop_ok probed"),
            ("cloud glance probes timeout ≤5s fail soft", "scripts/mac_health_cloud_glance_v1.py", "/health never hangs"),
            ("ui_contract cloud_glance_strip_id stable", "scripts/mac_health_founder_glance_ui_v1.py", "strip id in contract"),
            ("paintCloudGlance truncate + title attr", "scripts/mac-health-standalone/app.js", "no layout break"),
            ("Click strip read-only refresh only", "scripts/mac-health-standalone/app.js", "no cloud dispatch POST"),
            ("Receipt on manual refresh", "scripts/mac_health_cloud_glance_v1.py", "mac-health-cloud-glance-v1.json updates"),
            ("Hub OK in founder_line when :13020 up", "scripts/mac_health_cloud_glance_v1.py", "Hub OK in line"),
            ("Amber strip when control plane flag missing", "scripts/mac-health-standalone/app.js", "warn class when flag absent"),
            ("CLI --json schema field", "scripts/mac_health_cloud_glance_v1.py", "schema present"),
            ("MAC_HEALTH_GUARD_UPGRADE_MANIFEST v4.1 addendum", "scripts/MAC_HEALTH_GUARD_UPGRADE_MANIFEST_v4.1.md", "CF glance documented"),
        ],
    ),
    (
        "M111-115",
        "LaunchAgent heart reliability",
        "E01",
        [
            ("LaunchAgent wrapper health check before start", "scripts/install-mac-health-launchagent-v1.sh", "no duplicate PIDs"),
            ("PID file synced in serve-mac-health-guard.sh", "scripts/serve-mac-health-guard.sh", "pid matches listener"),
            ("Stale port kill uses resolver path", "scripts/serve-mac-health-guard.sh", "correct python script"),
            ("ThrottleInterval 30s plist", "scripts/install-mac-health-launchagent-v1.sh", "throttle present"),
            ("launchctl kickstart health 200", "scripts/install-mac-health-launchagent-v1.sh", "health within 20s"),
            ("RunAtLoad on login", "scripts/install-mac-health-launchagent-v1.sh", "RunAtLoad true"),
            ("Quiet flag respected in pulse", "scripts/mac-health-guard-server.py", "no sound when quiet"),
            ("write_h1_bridge when hub up", "scripts/mac_health_live_v1.py", "H1 bridge written"),
            ("validate-mac-health-wire-live-v1.sh PASS", "scripts/validate-mac-health-wire-live-v1.sh", "wire audit green"),
            ("Receipt mac-health-launchagent-receipt-v1.json", "~/.sina/mac-health-launchagent-receipt-v1.json", "ok:true"),
        ],
    ),
    (
        "M111-116",
        "Log Shield and disk relief",
        "E01",
        [
            ("Log shield thresholds 100MB/1GB", "scripts/mac_health_log_shield_v1.py", "thresholds documented"),
            ("UI log-bomb banner wired", "scripts/mac-health-standalone/app.js", "banner on critical"),
            ("btn-log-shield-relieve POST action", "scripts/mac_health_guard.py", "log_shield_relieve works"),
            ("Kill stuck readers action", "scripts/mac_health_log_shield_v1.py", "no cat on huge logs"),
            ("Hub truth badge JSON ok:true", "scripts/mac-health-standalone/index.html", "not port-only"),
            ("validate-mac-health-log-shield-v1.sh", "scripts/validate-mac-health-log-shield-v1.sh", "PASS"),
            ("Prevention integration log bomb", "scripts/mac_health_prevention_v1.py", "prevention-line set"),
            ("Validators tail-only logs", "scripts/validate-mac-health-log-shield-v1.sh", "INCIDENT-039 safe"),
            ("Rotate command-server.log snippet", "scripts/mac_health_log_shield_v1.py", "rotate path exists"),
            ("e2e-latest log_shield_ok field", "scripts/_mac_health_validator_common_v1.sh", "field in receipt"),
        ],
    ),
    (
        "M111-117",
        "Panic hotkey and emergency stop",
        "E01",
        [
            ("install-mac-health-panic-hotkey resolved SOURCEA", "scripts/install-mac-health-panic-hotkey-v1.sh", "hotkey registered"),
            ("validate-mac-health-panic-hotkey-v1.sh PASS", "scripts/validate-mac-health-panic-hotkey-v1.sh", "listener alive"),
            ("GET /api/mac-health/panic dry-run only", "scripts/mac-health-guard-server.py", "never kills on GET"),
            ("POST panic fast path", "scripts/mac_health_emergency_stop_v1.py", "founder_line returned"),
            ("POST /api/mac-health/panic/full", "scripts/mac-health-guard-server.py", "full stop route"),
            ("Native emergency_stop Swift bridge", "brand/macos-apps/MacHealthShell.swift", "WKWebView works"),
            ("Panic flash UI 8s", "scripts/mac-health-standalone/index.html", "panic-flash visible"),
            ("validate-mac-health-never-again-v1.sh PASS", "scripts/validate-mac-health-never-again-v1.sh", "mandates wired"),
            ("Cooldown e2e cloud only gate", "scripts/validate-mac-health-cooldown-e2e-v1.sh", "not mac session"),
            ("Receipt mac-health-panic-drill-receipt-v1.json", "~/.sina/mac-health-panic-drill-receipt-v1.json", "ok:true dry-run"),
        ],
    ),
    (
        "M111-118",
        "Founder glance UI v4.1 polish",
        "E01",
        [
            ("ui_upgrade_first_check mac_health ack", "data/ui-upgrade-ledgers/mac_health-v1.json", "MH checklist current"),
            ("contract version 4.1.0", "data/mac-health-founder-glance-ui-contract-v1.json", "version match"),
            ("Hub CSS optional offline", "scripts/mac-health-standalone/index.html", "usable hub-down"),
            ("Null-guard getElementById founder DOM", "scripts/mac-health-standalone/app.js", "no JS throw"),
            ("Pressure grid live poll 8s", "scripts/mac-health-standalone/app.js", "pressure-live updates"),
            ("Score ring cursor_hot override", "scripts/mac-health-standalone/app.js", "ring red when hot"),
            ("validate-mac-health-founder-glance-v1.sh PASS", "scripts/validate-mac-health-founder-glance-v1.sh", "tab_count=0"),
            ("validate-mac-health-ui-v1.sh PASS", "scripts/validate-mac-health-ui-v1.sh", "UI markers"),
            ("UI ledger UP-MH-004 entry", "data/ui-upgrade-ledgers/mac_health-v1.json", "UP-MH-004 shipped"),
            ("Hub Pro experience log append", "data/hub-pro-app-experience-log-v1.json", "mac_health row"),
        ],
    ),
    (
        "M111-119",
        "Prevention and Cursor hot tiers",
        "E01",
        [
            ("prevention modes documented", "scripts/mac_health_prevention_v1.py", "settings schema"),
            ("Cursor hot banner thresholds", "scripts/mac-health-standalone/app.js", "peak/sum pct"),
            ("Playwright stuck banner", "scripts/mac-health-standalone/app.js", "kill button wired"),
            ("btn-heal run_full_relief chain", "scripts/mac_health_guard.py", "pipeline RAM cool down"),
            ("validate-mac-health-prevention-v1.sh PASS", "scripts/validate-mac-health-prevention-v1.sh", "PASS"),
            ("RAM purge hero ≥75%", "scripts/mac_health_ram_pressure_v1.py", "purge wired"),
            ("CPU relief data-action mapped", "scripts/mac-health-standalone/index.html", "all actions wired"),
            ("validate-mac-health-all-actions read-only", "scripts/validate-mac-health-all-actions-v1.sh", "no side effects"),
            ("Settings form save", "scripts/mac_health_settings_v1.py", "save works"),
            ("validate-mac-health-settings-v1.sh PASS", "scripts/validate-mac-health-settings-v1.sh", "PASS"),
        ],
    ),
    (
        "M111-120",
        "Native Swift bridge completeness",
        "E01",
        [
            ("NativeActions vs app.js parity audit", "brand/macos-apps/MacHealthShell.swift", "parity doc in receipt"),
            ("restart_cursor detached verified", "brand/macos-apps/MacHealthShell.swift", "Cursor relaunch"),
            ("desktop_stop opens STOP AGENTS.app", "brand/macos-apps/MacHealthShell.swift", "fallback alert"),
            ("PYTHONPATH resolved scripts dir", "brand/macos-apps/MacHealthShell.swift", "imports work"),
            ("MAC_HEALTH_BUNDLE_ROOT fallback", "brand/macos-apps/MacHealthShell.swift", "bundle fallback"),
            ("App launch log rotation <5MB", "brand/macos-apps/MacHealthShell.swift", "log capped"),
            ("Menu items match web panic", "brand/macos-apps/MacHealthShell.swift", "menu parity"),
            ("?native=1 loads same UI", "scripts/mac-health-standalone/index.html", "native assets ok"),
            ("ATS localhost only", "scripts/build-mac-health-standalone-app-v1.sh", "NSAllowsLocalNetworking"),
            ("Founder sign-off receipt", "~/.sina/mac-health-native-bridge-receipt-v1.json", "ok:true"),
        ],
    ),
    (
        "M111-121",
        "W2 ship gate",
        "E01",
        [
            ("gen_ecosystem_mac_health_111_plan_v1.py --write W2", "scripts/gen_ecosystem_mac_health_111_plan_v1.py", "W2 in JSON"),
            ("validate-ecosystem-mac-health-111-plan-v1.sh W2", "scripts/validate-ecosystem-mac-health-111-plan-v1.sh", "10×10 steps"),
            ("run-mac-health-recipe ship-fast", "scripts/run-mac-health-recipe-v1.sh", "ship-fast PASS"),
            ("ecosystem_mac_health_111_plan_pulse --json", "scripts/ecosystem_mac_health_111_plan_pulse_v1.py", "W2 progress %"),
            ("Cloud CI e2e gate documented", "scripts/validate-mac-health-e2e-v1.sh", "SOURCEA_CI gate"),
            ("Human doc W2 critical path", "docs/SOURCEA_ECOSYSTEM_MAC_HEALTH_111_UPGRADE_PLAN_LOCKED_v1.md", "W2 section"),
            ("UP-MH-004 ledger shipped", "data/ui-upgrade-ledgers/mac_health-v1.json", "status shipped"),
            ("MAC_HEALTH_GUARD_UPGRADE_MANIFEST v4.1 locked", "scripts/MAC_HEALTH_GUARD_UPGRADE_MANIFEST_v4.1.md", "manifest exists"),
            ("Brain runbook Mac Health line", "docs/brain-runbook/brain-operational-runbook.md", ":13024 cited"),
            ("M111-121 status done W2 complete", "data/ecosystem-mac-health-111-upgrade-plan-v1.json", "100/100 W2 steps"),
        ],
    ),
]


def build_w2_upgrades() -> list[dict[str, Any]]:
    if not IS_PERSONAL:
        return []
    out: list[dict[str, Any]] = []
    for plan_id, title, epic, steps in W2_PLAN_SPECS:
        out.append(
            {
                "id": plan_id,
                "wave": "W2",
                "epic": epic,
                "epic_label": "Mac Health W2 — v4.1.0 hardening",
                "tier": "P0",
                "title": title,
                "goal_alignment": "mac_health_founder",
                "execution_plane": "mac_control_panel",
                "status": "planned",
                "founder_session_safe": True,
                "steps": [
                    {
                        "step": i + 1,
                        "title": st,
                        "wired_to": wt,
                        "acceptance": acc,
                        "status": "planned",
                    }
                    for i, (st, wt, acc) in enumerate(steps)
                ],
            }
        )
    return out
