#!/usr/bin/env python3
"""K1 read gate — validate receipts at loader choke points, not at build_payload().

Law: enforce where data is READ (load_healthy_queue, load_factory_now, load_active_now).
build_payload() is a downstream aggregator — edge-rank ≠ read-path.

Graphify god-node note: build_payload has 108 fan-in; loaders are the receipt read sources.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
DEFAULT_MAX_AGE_HOURS = float(os.environ.get("K1_MAX_RECEIPT_AGE_HOURS", "8"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _age_hours(ts: str) -> float | None:
    at = _parse_ts(ts)
    if not at:
        return None
    return (datetime.now(timezone.utc) - at).total_seconds() / 3600.0


def verify_checksum_on_read(data: dict[str, Any], *, path: str = "") -> dict[str, Any]:
    """Tamper-on-read when receipt_checksum present (demo-enforcement receipts)."""
    if not data.get("receipt_checksum"):
        return {"ok": True, "skipped": True, "reason": "no_checksum", "path": path}
    try:
        import sys

        sys.path.insert(0, str(SCRIPTS))
        from commit_intent_v1 import verify_receipt_checksum  # noqa: WPS433

        ok = verify_receipt_checksum(data)
        return {"ok": ok, "path": path, "reason": "checksum_valid" if ok else "checksum_mismatch"}
    except Exception as exc:
        return {"ok": False, "path": path, "error": str(exc)}


def freshness_gate(data: dict[str, Any], *, max_age_hours: float = DEFAULT_MAX_AGE_HOURS) -> dict[str, Any]:
    """Receipt freshness gate (same discipline as sourcea-boot receipt_fresh)."""
    at = str(data.get("at") or data.get("written_at") or "")
    age = _age_hours(at)
    if age is None:
        return {"ok": False, "reason": "missing_timestamp", "at": at}
    if age > max_age_hours:
        return {"ok": False, "reason": "stale", "age_hours": round(age, 2), "max_hours": max_age_hours}
    return {"ok": True, "age_hours": round(age, 2), "max_hours": max_age_hours}


def load_json_k1(path: Path, *, require_checksum: bool = False) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Load JSON + K1 gates. Returns (data, k1_meta)."""
    meta: dict[str, Any] = {"path": str(path), "ok": True}
    if not path.is_file():
        meta["ok"] = False
        meta["reason"] = "missing"
        return None, meta
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        meta["ok"] = False
        meta["reason"] = str(exc)
        return None, meta
    if not isinstance(data, dict):
        meta["ok"] = False
        meta["reason"] = "not_object"
        return None, meta
    chk = verify_checksum_on_read(data, path=str(path))
    meta["checksum"] = chk
    if require_checksum and chk.get("skipped"):
        meta["ok"] = False
        meta["reason"] = "checksum_required"
        return data, meta
    if not chk.get("ok") and not chk.get("skipped"):
        meta["ok"] = False
        meta["reason"] = "checksum_fail"
    fresh = freshness_gate(data)
    meta["freshness"] = fresh
    if not fresh.get("ok") and str(data.get("at") or ""):
        meta["ok"] = meta.get("ok", True) and False
        meta.setdefault("reasons", []).append("stale")
    return data, meta


def k1_after_queue_read(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    """Post-read hook for healthy queue — phase_strict alignment."""
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from healthy_queue_ssot_lib import phase_strict_queue_check  # noqa: WPS433

    check = phase_strict_queue_check()
    return {"phase_strict": check, "path": str(path), "ok": check.get("ok", True)}


def active_now_file_fresh(*, max_age_hours: float = DEFAULT_MAX_AGE_HOURS) -> dict[str, Any]:
    """ACTIVE_NOW.md mtime freshness — independent of parsed fields."""
    active = ROOT / "ACTIVE_NOW.md"
    if not active.is_file():
        return {"ok": False, "reason": "ACTIVE_NOW_MISSING"}
    mtime = datetime.fromtimestamp(active.stat().st_mtime, tz=timezone.utc)
    age_h = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600.0
    ok = age_h <= max_age_hours
    return {
        "ok": ok,
        "fresh": ok,
        "stale": not ok,
        "age_hours": round(age_h, 2),
        "max_hours": max_age_hours,
        "path": str(active),
    }


def strict_mode() -> bool:
    return os.environ.get("K1_READ_STRICT", "").strip().lower() in ("1", "true", "yes")
