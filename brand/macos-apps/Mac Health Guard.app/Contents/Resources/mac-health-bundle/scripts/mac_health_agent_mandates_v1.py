#!/usr/bin/env python3
"""Mac Health Agent Mandates v1 — enforce Mac Law obedience on disk.

Law SSOT: ~/Desktop/MacLaw/MAC_HEALTH_AGENT_MANDATES_LOCKED.md
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mac_health_edition_v1 import IS_PERSONAL, SINA

QUIET_FLAG = SINA / "mac-health-quiet-v1.flag"
FILM_FREEZE = SINA / "commercial-film-render-frozen-v1.flag"
CONTROL_PLANE_FLAG = SINA / "mac-control-plane-v1.flag"
CLI_DISABLED = SINA / "cli-disabled-v1.flag"
API_DISABLED = SINA / "api-disabled-v1.flag"
AUTORUN_LABEL = "com.sourcea.autorun-worker"
PANIC_PATH = SINA / "config" / "mac-health-panic-v1.json"
RECEIPT_PATH = SINA / "mac-health" / "agent-mandates-latest-v1.json"
MANDATE_DOC = Path.home() / "Desktop/MacLaw/MAC_HEALTH_AGENT_MANDATES_LOCKED.md"
NO_AUTO_LAW = Path.home() / "Desktop/MacLaw/MAC_NO_AUTO_SCREENSHOT_LOCKED.md"
VISUAL_PROOF_CONFIG = SINA / "config" / "visual_proof.json"
NO_AUTO_FLAG = SINA / "no-auto-screenshot-v1.flag"

PANIC_LAUNCH_LABELS = (
    "com.sina.mac-health-panic-hotkey",
    "com.sina.panic-stop-menubar",
    "com.sina.mac-health-panic-listener",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _launchd_loaded(label: str) -> bool:
    uid = os.getuid()
    try:
        proc = subprocess.run(
            ["launchctl", "print", f"gui/{uid}/{label}"],
            capture_output=True,
            text=True,
            timeout=4.0,
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _bootout_panic_agents() -> list[dict[str, Any]]:
    uid = os.getuid()
    rows: list[dict[str, Any]] = []
    for label in PANIC_LAUNCH_LABELS:
        loaded = _launchd_loaded(label)
        action = "none"
        if loaded:
            try:
                subprocess.run(
                    ["launchctl", "bootout", f"gui/{uid}/{label}"],
                    capture_output=True,
                    timeout=8.0,
                )
                action = "bootout"
            except (OSError, subprocess.TimeoutExpired):
                action = "bootout_fail"
        rows.append({"label": label, "was_loaded": loaded, "action": action})
    for name in ("Mac Health Panic", "Panic Stop"):
        try:
            subprocess.run(["killall", name], capture_output=True, timeout=4.0)
        except (OSError, subprocess.TimeoutExpired):
            pass
    return rows


def _ensure_quiet_flag() -> dict[str, Any]:
    if QUIET_FLAG.is_file():
        return {"path": str(QUIET_FLAG), "action": "already"}
    SINA.mkdir(parents=True, exist_ok=True)
    QUIET_FLAG.write_text(f"mac-health-quiet-v1 · {_now()} · agent mandates enforce\n", encoding="utf-8")
    return {"path": str(QUIET_FLAG), "action": "created"}


def _ensure_cli_disabled() -> dict[str, Any]:
    if CLI_DISABLED.is_file():
        return {"path": str(CLI_DISABLED), "action": "already"}
    SINA.mkdir(parents=True, exist_ok=True)
    CLI_DISABLED.write_text(f"cli-disabled-v1 · {_now()} · agent mandates enforce\n", encoding="utf-8")
    return {"path": str(CLI_DISABLED), "action": "created"}


def _ensure_api_enabled() -> dict[str, Any]:
    if not API_DISABLED.is_file():
        return {"path": str(API_DISABLED), "action": "already"}
    API_DISABLED.unlink()
    return {"path": str(API_DISABLED), "action": "removed"}


def _ensure_notifications_off() -> dict[str, Any]:
    try:
        import sys

        scripts = Path(__file__).resolve().parent
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from mac_health_settings_v1 import save_settings  # noqa: WPS433

        raw = _probe_notifications_off()
        if raw.get("cpu_warn_enabled"):
            save_settings({"notifications": {"enabled": False, "sounds_enabled": False}})
            return {"action": "patched_settings", "enabled": False}
        return {"action": "ok", "enabled": False}
    except Exception as exc:
        return {"action": "error", "error": str(exc)[:160]}


def _probe_notifications_off() -> dict[str, Any]:
    row: dict[str, Any] = {"ok": False}
    if PANIC_PATH.is_file():
        try:
            doc = json.loads(PANIC_PATH.read_text(encoding="utf-8"))
            cpu_warn = doc.get("cpu_warn") or {}
            row["cpu_warn_enabled"] = bool(cpu_warn.get("enabled", True))
        except (OSError, json.JSONDecodeError):
            row["cpu_warn_enabled"] = None
    row["quiet_flag"] = QUIET_FLAG.is_file()
    row["ok"] = row.get("quiet_flag") and not row.get("cpu_warn_enabled", True)
    return row


def _code_mandates_present() -> dict[str, Any]:
    scripts = Path(__file__).resolve().parent
    emerg = (scripts / "mac_health_emergency_stop_v1.py").read_text(encoding="utf-8")
    settings = (scripts / "mac_health_settings_v1.py").read_text(encoding="utf-8")
    return {
        "mandate_doc": MANDATE_DOC.is_file(),
        "notifications_enabled_fn": "def notifications_enabled()" in settings,
        "notify_respects_quiet": "notifications_enabled()" in emerg and "if not notifications_enabled()" in emerg,
        "motor_kill_pattern": "fbe_motor_delegate_v1" in emerg,
        "rules_loop_kill": "agent_rules_loop_orchestrator" in emerg,
        "anti_staleness_kill": "anti_staleness_auto_wire_v1" in emerg,
    }


def _probe_visual_proof_off() -> dict[str, Any]:
    if not VISUAL_PROOF_CONFIG.is_file():
        return {"ok": True, "enabled": False, "missing_config": True}
    try:
        doc = json.loads(VISUAL_PROOF_CONFIG.read_text(encoding="utf-8"))
        vp = doc.get("visual_proof") or doc
        enabled = bool(vp.get("enabled", False))
        return {"ok": not enabled, "enabled": enabled}
    except (OSError, json.JSONDecodeError):
        return {"ok": True, "enabled": False, "read_error": True}


def _ensure_visual_proof_off() -> dict[str, Any]:
    row = _probe_visual_proof_off()
    if row.get("ok"):
        return {"action": "ok", **row}
    doc: dict[str, Any] = {}
    if VISUAL_PROOF_CONFIG.is_file():
        try:
            doc = json.loads(VISUAL_PROOF_CONFIG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            doc = {}
    vp = doc.get("visual_proof") if isinstance(doc.get("visual_proof"), dict) else doc
    if not isinstance(vp, dict):
        vp = {}
    vp["enabled"] = False
    doc["visual_proof"] = vp
    VISUAL_PROOF_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    VISUAL_PROOF_CONFIG.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return {"action": "patched", "enabled": False}


def run_agent_mandates_probe(*, side_effects: bool = True) -> dict[str, Any]:
    if not IS_PERSONAL:
        return {
            "schema": "mac-health-agent-mandates-v1",
            "at": _now(),
            "side_effects": side_effects,
            "ok": True,
            "available": False,
            "reason": "personal_edition_only",
            "violations": [],
            "enforce": {},
        }
    code = _code_mandates_present()
    notifications = _probe_notifications_off()
    panic_agents = [
        {"label": label, "loaded": _launchd_loaded(label)} for label in PANIC_LAUNCH_LABELS
    ]

    def _collect_violations() -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        if not MANDATE_DOC.is_file():
            out.append({"id": "missing_mandate_doc", "detail": str(MANDATE_DOC)})
        if not QUIET_FLAG.is_file():
            out.append({"id": "quiet_flag_missing", "detail": str(QUIET_FLAG)})
        notif = _probe_notifications_off()
        if notif.get("cpu_warn_enabled"):
            out.append({"id": "cpu_warn_enabled", "detail": "notifications must stay off"})
        agents = [{"label": label, "loaded": _launchd_loaded(label)} for label in PANIC_LAUNCH_LABELS]
        if any(r["loaded"] for r in agents):
            out.append({"id": "panic_agents_loaded", "detail": "boot out panic launch agents"})
        if not CONTROL_PLANE_FLAG.is_file():
            out.append({"id": "control_plane_inactive", "detail": str(CONTROL_PLANE_FLAG)})
        if not CLI_DISABLED.is_file():
            out.append({"id": "cli_not_disabled", "detail": "local CLI drain must stay off on Mac"})
        if API_DISABLED.is_file():
            out.append({"id": "api_disabled", "detail": "cloud APIs must stay enabled from control panel"})
        if _launchd_loaded(AUTORUN_LABEL):
            out.append({"id": "autorun_loaded", "detail": "boot out com.sourcea.autorun-worker"})
        if not FILM_FREEZE.is_file():
            out.append({"id": "film_not_frozen", "detail": str(FILM_FREEZE)})
        if not code.get("notify_respects_quiet"):
            out.append({"id": "notify_not_quiet", "detail": "_notify must gate on notifications_enabled()"})
        vp = _probe_visual_proof_off()
        if vp.get("enabled"):
            out.append({"id": "visual_proof_enabled", "detail": "hub screencapture shutter — must stay off"})
        if not NO_AUTO_LAW.is_file():
            out.append({"id": "missing_no_auto_law", "detail": str(NO_AUTO_LAW)})
        if not NO_AUTO_FLAG.is_file():
            out.append({"id": "no_auto_flag_missing", "detail": str(NO_AUTO_FLAG)})
        try:
            from no_auto_screenshot_v1 import _code_forbidden_pkill  # noqa: WPS433

            forbidden = _code_forbidden_pkill()
            if forbidden:
                out.append({"id": "forbidden_blanket_pkill", "detail": str(forbidden)})
        except Exception:
            pass
        for key in ("motor_kill_pattern", "rules_loop_kill", "anti_staleness_kill"):
            if not code.get(key):
                out.append({"id": f"missing_{key}", "detail": key})
        return out

    violations = _collect_violations()
    enforce: dict[str, Any] = {}
    if side_effects:
        if violations:
            violation_ids = {v.get("id") for v in violations}
            enforce["quiet_flag"] = _ensure_quiet_flag()
            enforce["notifications"] = _ensure_notifications_off()
            enforce["visual_proof"] = _ensure_visual_proof_off()
            if "cli_not_disabled" in violation_ids:
                enforce["cli_disabled"] = _ensure_cli_disabled()
            if "api_disabled" in violation_ids:
                enforce["api_disabled"] = _ensure_api_enabled()
            try:
                from no_auto_screenshot_v1 import run_no_auto_screenshot  # noqa: WPS433

                enforce["no_auto_screenshot"] = run_no_auto_screenshot(side_effects=True)
            except Exception as exc:
                enforce["no_auto_screenshot"] = {"action": "error", "error": str(exc)[:120]}
            try:
                from mac_pipeline_validator_pressure_v1 import run_pressure_probe  # noqa: WPS433

                enforce["pipeline_validator_pressure"] = run_pressure_probe(side_effects=True)
            except Exception as exc:
                enforce["pipeline_validator_pressure"] = {"action": "error", "error": str(exc)[:120]}
            if any(r["loaded"] for r in panic_agents):
                enforce["panic_bootout"] = _bootout_panic_agents()
            if _launchd_loaded(AUTORUN_LABEL):
                uid = os.getuid()
                try:
                    subprocess.run(
                        ["launchctl", "bootout", f"gui/{uid}/{AUTORUN_LABEL}"],
                        capture_output=True,
                        timeout=8.0,
                    )
                    enforce["autorun_bootout"] = {"label": AUTORUN_LABEL, "action": "bootout"}
                except (OSError, subprocess.TimeoutExpired) as exc:
                    enforce["autorun_bootout"] = {"label": AUTORUN_LABEL, "error": str(exc)[:80]}
            try:
                from mac_control_plane_v1 import enter as control_plane_enter  # noqa: WPS433

                if not CONTROL_PLANE_FLAG.is_file():
                    enforce["control_plane"] = control_plane_enter(wire_sync=False)
            except Exception as exc:
                enforce["control_plane"] = {"action": "error", "error": str(exc)[:120]}
            try:
                from mac_health_never_again_v1 import ensure_film_frozen  # noqa: WPS433

                enforce["film"] = ensure_film_frozen(enabled=True)
            except Exception as exc:
                enforce["film"] = {"action": "error", "error": str(exc)[:120]}
            panic_agents = [
                {"label": label, "loaded": _launchd_loaded(label)} for label in PANIC_LAUNCH_LABELS
            ]
            notifications = _probe_notifications_off()
            violations = _collect_violations()
        else:
            enforce["note"] = "already compliant"

    row = {
        "schema": "mac-health-agent-mandates-v1",
        "at": _now(),
        "side_effects": side_effects,
        "mandate_doc": str(MANDATE_DOC),
        "mandate_doc_ok": MANDATE_DOC.is_file(),
        "quiet_flag": QUIET_FLAG.is_file(),
        "film_frozen": FILM_FREEZE.is_file(),
        "control_plane": CONTROL_PLANE_FLAG.is_file(),
        "cli_disabled": CLI_DISABLED.is_file(),
        "api_disabled": API_DISABLED.is_file(),
        "autorun_loaded": _launchd_loaded(AUTORUN_LABEL),
        "notifications": notifications,
        "visual_proof": _probe_visual_proof_off(),
        "no_auto_screenshot_law": NO_AUTO_LAW.is_file(),
        "no_auto_flag": NO_AUTO_FLAG.is_file(),
        "panic_agents": panic_agents,
        "code": code,
        "enforce": enforce,
        "violations": violations,
        "ok": len(violations) == 0,
    }
    if side_effects:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Mac Health agent mandates — Mac Law enforce")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="Probe only — no enforce")
    args = ap.parse_args()
    row = run_agent_mandates_probe(side_effects=not args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        status = "OK" if row.get("ok") else "VIOLATIONS"
        print(f"agent-mandates · {status} · violations={len(row.get('violations') or [])}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
