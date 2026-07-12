#!/usr/bin/env python3
"""Mac Health Guard — commercial-edition licensing (14-day trial + Gumroad).

SCAFFOLDING NOTICE: this module ships before the Gumroad product exists.
GUMROAD_PRODUCT_ID below is a placeholder — create the "Mac Health Guard"
product in the Gumroad seller dashboard and replace it with the real
product_id before this can verify any real purchase. Until then, the local
14-day trial still works fine; only online activation of a real key cannot
succeed.

Personal edition never needs or checks a license — every public function
short-circuits on IS_PERSONAL before touching disk or network, so this
module has zero effect on the maintainer's own machine.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mac_health_edition_v1 import IS_PERSONAL, SINA

# TODO: replace with the real product_id from the Gumroad seller dashboard
# once the Mac Health Guard product exists there.
GUMROAD_PRODUCT_ID = "REPLACE_ME"
GUMROAD_VERIFY_URL = "https://api.gumroad.com/v2/licenses/verify"

LICENSE_DIR = SINA / "license"
FIRST_RUN_PATH = LICENSE_DIR / "first-run-v1.json"
VERIFIED_PATH = LICENSE_DIR / "verified-v1.json"

TRIAL_DAYS = 14
RECHECK_INTERVAL_SEC = 7 * 24 * 60 * 60
REQUEST_TIMEOUT_SEC = 8.0

_ISO_FMT = "%Y-%m-%dT%H:%M:%SZ"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().strftime(_ISO_FMT)


def _parse_iso(stamp: Any) -> datetime | None:
    if not isinstance(stamp, str):
        return None
    try:
        return datetime.strptime(stamp, _ISO_FMT).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def _first_run_at() -> datetime:
    """Return the recorded first-run time, stamping it on the very first call."""
    started = _parse_iso(_read_json(FIRST_RUN_PATH).get("first_run_at"))
    if started is not None:
        return started
    now = _now()
    _write_json(FIRST_RUN_PATH, {"first_run_at": now.strftime(_ISO_FMT)})
    return now


def _trial_days_left() -> int:
    started = _first_run_at()
    elapsed = _now() - started
    return max(0, TRIAL_DAYS - elapsed.days)


def _verify_online(license_key: str) -> dict[str, Any]:
    """POST to Gumroad's License Verify API.

    Returns {"ok": True} for a confirmed valid, non-refunded purchase;
    {"ok": False, "error": "invalid"} for a confirmed bad/refunded key; or
    {"ok": False, "error": "network"} if Gumroad couldn't be reached or the
    response couldn't be parsed — callers should treat "network" as "we
    don't know" and fall back to cache/trial, not as a rejection.
    """
    data = urllib.parse.urlencode(
        {"product_id": GUMROAD_PRODUCT_ID, "license_key": license_key}
    ).encode("ascii")
    req = urllib.request.Request(GUMROAD_VERIFY_URL, data=data, method="POST")
    try:
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SEC) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            # Gumroad answers an unknown/invalid key with a non-200 status
            # that still carries a JSON body — a real answer, not a network
            # failure, so read it instead of treating it as unreachable.
            raw = exc.read()
        payload = json.loads(raw.decode("utf-8"))
    except Exception:
        return {"ok": False, "error": "network"}

    if not isinstance(payload, dict):
        return {"ok": False, "error": "network"}
    if not payload.get("success"):
        return {"ok": False, "error": "invalid"}
    purchase = payload.get("purchase") or {}
    if purchase.get("refunded") or purchase.get("chargebacked"):
        return {"ok": False, "error": "invalid"}
    return {"ok": True}


def activate_license(key: str) -> dict[str, Any]:
    """Verify `key` against Gumroad and persist the result on success.

    Personal edition: no-op, always reports licensed — there is nothing to
    activate.
    """
    if IS_PERSONAL:
        return {"ok": True, "state": "licensed", "trial_days_left": None, "edition": "personal"}

    key = (key or "").strip()
    if not key:
        return {
            "ok": False,
            "state": "invalid",
            "trial_days_left": _trial_days_left(),
            "edition": "commercial",
        }

    result = _verify_online(key)
    if result.get("ok"):
        _write_json(
            VERIFIED_PATH,
            {"license_key": key, "verified_at": _now_iso(), "state": "licensed"},
        )
        return {"ok": True, "state": "licensed", "trial_days_left": None, "edition": "commercial"}

    if result.get("error") == "network":
        # Couldn't reach Gumroad to confirm either way — don't brand a
        # possibly-good key "invalid"; fall back to whatever trial/cache
        # already says and note the network hiccup.
        status = license_status()
        status["error"] = "network"
        return status

    return {
        "ok": False,
        "state": "invalid",
        "trial_days_left": _trial_days_left(),
        "edition": "commercial",
    }


def license_status() -> dict[str, Any]:
    """Current license state.

    Never raises; fails safe/quiet on network or parsing errors by trusting
    the last good local cache, then the trial window, before ever reporting
    a hard failure.
    """
    if IS_PERSONAL:
        return {"ok": True, "state": "licensed", "trial_days_left": None, "edition": "personal"}

    cached = _read_json(VERIFIED_PATH)
    if cached.get("state") == "licensed":
        key = cached.get("license_key")
        verified_at = _parse_iso(cached.get("verified_at"))
        age_sec = (_now() - verified_at).total_seconds() if verified_at else None
        if age_sec is None or age_sec < RECHECK_INTERVAL_SEC or not isinstance(key, str) or not key:
            # Cache still fresh (or too malformed to safely re-check) —
            # trust it rather than hit the network on every launch.
            return {"ok": True, "state": "licensed", "trial_days_left": None, "edition": "commercial"}
        result = _verify_online(key)
        if result.get("ok"):
            _write_json(VERIFIED_PATH, {"license_key": key, "verified_at": _now_iso(), "state": "licensed"})
            return {"ok": True, "state": "licensed", "trial_days_left": None, "edition": "commercial"}
        if result.get("error") == "network":
            # Gumroad unreachable — trust the last good verification.
            return {"ok": True, "state": "licensed", "trial_days_left": None, "edition": "commercial"}
        # Confirmed revoked/refunded online — cache is no longer good.
        _write_json(VERIFIED_PATH, {"license_key": key, "verified_at": _now_iso(), "state": "invalid"})

    trial_days_left = _trial_days_left()
    if trial_days_left > 0:
        return {"ok": True, "state": "trial", "trial_days_left": trial_days_left, "edition": "commercial"}
    return {"ok": False, "state": "expired", "trial_days_left": 0, "edition": "commercial"}
