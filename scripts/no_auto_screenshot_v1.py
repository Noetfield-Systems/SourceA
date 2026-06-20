#!/usr/bin/env python3
"""No auto screenshot v1 — Mac Law enforce.

Law: ~/Desktop/MacLaw/MAC_NO_AUTO_SCREENSHOT_LOCKED.md
Never blanket-kill founder native Screenshot UI (pkill -f screencapture).
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
NO_AUTO_FLAG = SINA / "no-auto-screenshot-v1.flag"
VISUAL_PROOF_CONFIG = SINA / "config" / "visual_proof.json"
FILM_FREEZE = SINA / "commercial-film-render-frozen-v1.flag"
RECEIPT_PATH = SINA / "mac-health" / "no-auto-screenshot-latest-v1.json"
LAW_DOC = Path.home() / "Desktop/MacLaw/MAC_NO_AUTO_SCREENSHOT_LOCKED.md"

# SourceA/hub automation only — NOT /usr/sbin/screencapture for founder ⌘⇧4/5
AUTOMATION_KILL_PATTERNS = (
    "visual_proof_capture_v1",
    "trigger_agent_visual_capture",
    "commercial_short_film_v1",
    "cinematic-film-factory",
)

FORBIDDEN_SCRIPT_NEEDLES = (
    'pkill -9 -f screencapture',
    '["pkill", "-9", "-f", "screencapture"]',
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_flag() -> dict[str, Any]:
    if NO_AUTO_FLAG.is_file():
        return {"path": str(NO_AUTO_FLAG), "action": "already"}
    SINA.mkdir(parents=True, exist_ok=True)
    NO_AUTO_FLAG.write_text(
        f"no-auto-screenshot-v1 · {_now()} · Mac Law — no hub/factory auto capture\n",
        encoding="utf-8",
    )
    return {"path": str(NO_AUTO_FLAG), "action": "created"}


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


def _pgrep(pattern: str) -> list[int]:
    try:
        proc = subprocess.run(
            ["pgrep", "-f", pattern],
            capture_output=True,
            text=True,
            timeout=4.0,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if proc.returncode != 0:
        return []
    out: list[int] = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.isdigit():
            out.append(int(line))
    return out


def kill_automation_only() -> dict[str, Any]:
    """Kill SourceA capture workers — never blanket screencapture."""
    killed: list[dict[str, Any]] = []
    for pat in AUTOMATION_KILL_PATTERNS:
        pids = _pgrep(pat)
        for pid in pids:
            if pid == os.getpid():
                continue
            try:
                subprocess.run(["kill", "-TERM", str(pid)], capture_output=True, timeout=3.0)
                killed.append({"pattern": pat, "pid": pid, "signal": "TERM"})
            except (OSError, subprocess.TimeoutExpired):
                killed.append({"pattern": pat, "pid": pid, "signal": "fail"})
    return {"ok": True, "killed": killed, "note": "founder native screencapture untouched"}


def _probe_automation_pids() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for pat in AUTOMATION_KILL_PATTERNS:
        pids = _pgrep(pat)
        if pids:
            rows.append({"pattern": pat, "pids": pids})
    return {"ok": len(rows) == 0, "running": rows}


def _code_forbidden_pkill() -> list[dict[str, str]]:
    scripts = Path(__file__).resolve().parent
    hits: list[dict[str, str]] = []
    for rel in (
        "founder-mac-reset-v1.sh",
        "mac_control_plane_v1.py",
        "mac_daily_cleanup_v1.py",
    ):
        path = scripts / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for needle in FORBIDDEN_SCRIPT_NEEDLES:
            if needle in text:
                hits.append({"file": rel, "needle": needle})
    return hits


def run_no_auto_screenshot(*, side_effects: bool = True) -> dict[str, Any]:
    violations: list[dict[str, str]] = []
    if not LAW_DOC.is_file():
        violations.append({"id": "missing_law_doc", "detail": str(LAW_DOC)})
    if not NO_AUTO_FLAG.is_file():
        violations.append({"id": "no_auto_flag_missing", "detail": str(NO_AUTO_FLAG)})
    vp = _probe_visual_proof_off()
    if vp.get("enabled"):
        violations.append({"id": "visual_proof_enabled", "detail": "auto screenshot forbidden"})
    auto = _probe_automation_pids()
    if not auto.get("ok"):
        violations.append({"id": "automation_capture_running", "detail": str(auto.get("running"))})
    forbidden = _code_forbidden_pkill()
    if forbidden:
        violations.append({"id": "forbidden_blanket_pkill", "detail": str(forbidden)})
    if not FILM_FREEZE.is_file():
        violations.append({"id": "film_not_frozen", "detail": str(FILM_FREEZE)})

    enforce: dict[str, Any] = {}
    if side_effects and violations:
        enforce["flag"] = _ensure_flag()
        enforce["visual_proof"] = _ensure_visual_proof_off()
        if not auto.get("ok"):
            enforce["kill_automation"] = kill_automation_only()
        try:
            from mac_health_never_again_v1 import ensure_film_frozen  # noqa: WPS433

            enforce["film"] = ensure_film_frozen(enabled=True)
        except Exception as exc:
            enforce["film"] = {"error": str(exc)[:120]}
        violations = _collect_violations_after_enforce()

    row = {
        "schema": "no-auto-screenshot-v1",
        "at": _now(),
        "law_doc": str(LAW_DOC),
        "law_doc_ok": LAW_DOC.is_file(),
        "no_auto_flag": NO_AUTO_FLAG.is_file(),
        "visual_proof": _probe_visual_proof_off(),
        "automation_pids": _probe_automation_pids(),
        "forbidden_pkill_in_code": forbidden,
        "film_frozen": FILM_FREEZE.is_file(),
        "side_effects": side_effects,
        "enforce": enforce,
        "violations": violations,
        "ok": len(violations) == 0,
    }
    if side_effects:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _collect_violations_after_enforce() -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    if not NO_AUTO_FLAG.is_file():
        violations.append({"id": "no_auto_flag_missing", "detail": str(NO_AUTO_FLAG)})
    if _probe_visual_proof_off().get("enabled"):
        violations.append({"id": "visual_proof_enabled", "detail": "auto screenshot forbidden"})
    if not _probe_automation_pids().get("ok"):
        violations.append({"id": "automation_capture_running", "detail": "still running"})
    if _code_forbidden_pkill():
        violations.append({"id": "forbidden_blanket_pkill", "detail": "fix scripts"})
    if not FILM_FREEZE.is_file():
        violations.append({"id": "film_not_frozen", "detail": str(FILM_FREEZE)})
    return violations


def capture_blocked_reason() -> str | None:
    """Gate for visual_proof_capture_v1 — returns skip reason or None if allowed."""
    if NO_AUTO_FLAG.is_file():
        return "no_auto_screenshot_law"
    if not _probe_visual_proof_off().get("ok", True):
        return "visual_proof_disabled"
    return None


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Mac Law — no auto screenshot enforce")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--enforce", action="store_true", help="Alias for default side-effects run")
    ap.add_argument("--kill-automation-only", action="store_true")
    args = ap.parse_args()
    if args.kill_automation_only:
        row = kill_automation_only()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"kill-automation-only · killed={len(row.get('killed') or [])}")
        return 0
    side = not args.dry_run
    row = run_no_auto_screenshot(side_effects=side)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        status = "OK" if row.get("ok") else "VIOLATIONS"
        print(f"no-auto-screenshot · {status} · violations={len(row.get('violations') or [])}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
