#!/usr/bin/env python3
"""Native macOS visual proof capture on BLOCK verdict — Gemini spec.

Capture frontmost window via screencapture -l; fallback to active display + cursor.
Config: ~/.sina/config/visual_proof.json (key visual_proof)
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
VISUAL_PROOF_CONFIG = SINA / "config" / "visual_proof.json"
SESSION_TRACKING = SINA / "visual-proof-session-v1.json"
GLOBAL_RATE_PATH = SINA / "visual-proof-last-capture-v1.json"
QUIET_FLAG = SINA / "mac-health-quiet-v1.flag"
FOCUS_FLAG = SINA / "auto-run-disabled-v1.flag"
DEFAULT_OUTPUT_DIR = SINA / "proofs"
MIN_CAPTURE_GAP_SEC = 120


def _now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_visual_proof_config() -> dict[str, Any] | None:
    if not VISUAL_PROOF_CONFIG.is_file():
        return None
    try:
        data = json.loads(VISUAL_PROOF_CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    vp = data.get("visual_proof")
    if isinstance(vp, dict):
        return vp
    return data if isinstance(data, dict) else None


def _expand_path(raw: str | Path) -> Path:
    return Path(str(raw).replace("~", str(Path.home()))).expanduser()


def _read_session_tracking() -> dict[str, Any]:
    if not SESSION_TRACKING.is_file():
        return {"schema": "visual-proof-session-v1", "sessions": {}}
    try:
        data = json.loads(SESSION_TRACKING.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": "visual-proof-session-v1", "sessions": {}}
    if "sessions" not in data:
        data["sessions"] = {}
    return data


def _write_session_tracking(data: dict[str, Any]) -> None:
    SESSION_TRACKING.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    SESSION_TRACKING.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _session_proof_count(session_id: str) -> int:
    data = _read_session_tracking()
    row = (data.get("sessions") or {}).get(session_id) or {}
    return int(row.get("count") or 0)


def _increment_session_proof_count(session_id: str) -> int:
    data = _read_session_tracking()
    sessions = data.setdefault("sessions", {})
    row = sessions.setdefault(session_id, {"count": 0})
    row["count"] = int(row.get("count") or 0) + 1
    row["last_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_session_tracking(data)
    return int(row["count"])


def _purge_old_proofs(output_dir: Path, days: int) -> dict[str, Any]:
    if days <= 0 or not output_dir.is_dir():
        return {"purged": 0, "days": days, "skipped": days <= 0}
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    purged = 0
    for path in output_dir.glob("*.png"):
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                path.unlink(missing_ok=True)
                purged += 1
        except OSError:
            continue
    return {"purged": purged, "days": days}


def _get_frontmost_window_id() -> int | None:
    script = (
        'tell application "System Events" to get id of window 1 of '
        "(first process whose frontmost is true)"
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        return int(result.stdout.strip())
    except (ValueError, subprocess.TimeoutExpired, OSError):
        return None


def _capture_blocked() -> str | None:
    try:
        from no_auto_screenshot_v1 import capture_blocked_reason  # noqa: WPS433

        blocked = capture_blocked_reason()
        if blocked:
            return blocked
    except Exception:
        pass
    if QUIET_FLAG.is_file():
        return "mac_health_quiet"
    if FOCUS_FLAG.is_file():
        return "mac_focus_freeze"
    return None


def _global_rate_ok() -> bool:
    if not GLOBAL_RATE_PATH.is_file():
        return True
    try:
        row = json.loads(GLOBAL_RATE_PATH.read_text(encoding="utf-8"))
        last = float(row.get("at_epoch") or 0)
        return (datetime.now(timezone.utc).timestamp() - last) >= MIN_CAPTURE_GAP_SEC
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return True


def _mark_global_capture() -> None:
    GLOBAL_RATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GLOBAL_RATE_PATH.write_text(
        json.dumps({"at_epoch": datetime.now(timezone.utc).timestamp(), "at": _now_ts()})
        + "\n",
        encoding="utf-8",
    )


def _screencapture_window(path: Path, window_id: int, *, include_shadow: bool) -> bool:
    cmd: list[str] = ["screencapture", "-x"]
    if not include_shadow:
        cmd.append("-o")
    cmd.extend(["-l", str(window_id), str(path)])
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=15, check=False)
    except (subprocess.TimeoutExpired, OSError):
        return False
    return result.returncode == 0 and path.is_file() and path.stat().st_size > 0


def _screencapture_fallback(path: Path) -> bool:
    try:
        result = subprocess.run(
            ["screencapture", "-x", "-C", str(path)],
            capture_output=True,
            timeout=15,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return False
    return result.returncode == 0 and path.is_file() and path.stat().st_size > 0


def _compress_png_inplace(path: Path) -> dict[str, Any]:
    before = path.stat().st_size
    try:
        result = subprocess.run(
            ["sips", "-s", "format", "png", str(path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"ok": False, "error": str(exc), "before_bytes": before}
    after = path.stat().st_size if path.is_file() else 0
    return {
        "ok": result.returncode == 0,
        "before_bytes": before,
        "after_bytes": after,
    }


def trigger_agent_visual_capture(session_id: str, verdict: str) -> dict[str, Any]:
    """Capture visual proof for agent BLOCK verdict. Returns status dict."""
    blocked = _capture_blocked()
    if blocked:
        return {"status": "skipped", "reason": blocked}

    cfg = _load_visual_proof_config()
    if cfg is None:
        return {
            "status": "skipped",
            "reason": "config_missing",
            "config_path": str(VISUAL_PROOF_CONFIG),
        }

    if not cfg.get("enabled", False):
        return {"status": "skipped", "reason": "disabled"}

    if not _global_rate_ok():
        return {"status": "skipped", "reason": "global_rate_limit", "min_gap_sec": MIN_CAPTURE_GAP_SEC}

    targets = cfg.get("targets") or {}
    trigger = str(targets.get("verdict_trigger") or "BLOCK")
    if verdict != trigger:
        return {
            "status": "skipped",
            "reason": "verdict_mismatch",
            "verdict": verdict,
            "trigger": trigger,
        }

    automation = cfg.get("automation") or {}
    max_proofs = int(automation.get("max_proofs_per_session") or 10)
    count = _session_proof_count(session_id)
    if count >= max_proofs:
        return {
            "status": "skipped",
            "reason": "max_proofs_per_session",
            "session_id": session_id,
            "count": count,
            "max": max_proofs,
        }

    output_dir = _expand_path(cfg.get("output_dir") or str(DEFAULT_OUTPUT_DIR))
    output_dir.mkdir(parents=True, exist_ok=True)

    purge_days = int(automation.get("auto_purge_days") or 30)
    purge_result = _purge_old_proofs(output_dir, purge_days)

    timestamp = _now_ts()
    artifact_path = output_dir / f"{session_id}_{timestamp}_BLOCK.png"

    capture_cfg = cfg.get("capture") or {}
    format_cfg = cfg.get("format") or {}
    include_shadow = bool(
        capture_cfg.get("include_shadow", format_cfg.get("include_shadow", False))
    )

    window_id = _get_frontmost_window_id()
    method = "window"
    captured = False
    if window_id is not None:
        captured = _screencapture_window(
            artifact_path, window_id, include_shadow=include_shadow
        )

    if not captured:
        method = "fallback_display"
        captured = _screencapture_fallback(artifact_path)

    if not captured:
        return {
            "status": "failed",
            "reason": "capture_failed",
            "session_id": session_id,
            "window_id": window_id,
            "purge": purge_result,
        }

    format_cfg = cfg.get("format") or {}
    compress_result: dict[str, Any] | None = None
    if format_cfg.get("compress"):
        compress_result = _compress_png_inplace(artifact_path)

    proof_count = _increment_session_proof_count(session_id)
    _mark_global_capture()

    row: dict[str, Any] = {
        "status": "captured" if method == "window" else "captured_fallback",
        "method": method,
        "session_id": session_id,
        "verdict": verdict,
        "artifact_path": str(artifact_path),
        "filename": artifact_path.name,
        "window_id": window_id,
        "timestamp": timestamp,
        "engine": str(cfg.get("engine") or "macos_native_core"),
        "include_shadow": include_shadow,
        "session_proof_count": proof_count,
        "purge": purge_result,
    }
    if compress_result is not None:
        row["compress"] = compress_result
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Visual proof capture — BLOCK trigger")
    ap.add_argument("session_id", nargs="?", default="test_manual")
    ap.add_argument("--verdict", default="BLOCK")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = trigger_agent_visual_capture(args.session_id, args.verdict)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"VISUAL_PROOF {row.get('status')} — {row.get('reason') or row.get('artifact_path')}")
    return 0 if row.get("status") in ("captured", "captured_fallback", "skipped") else 1


if __name__ == "__main__":
    raise SystemExit(main())
