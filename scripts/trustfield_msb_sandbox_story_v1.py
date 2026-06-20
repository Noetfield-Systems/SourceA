#!/usr/bin/env python3
"""TrustField MSB / compliance sandbox story — P0-06 acceptance gate.

Receipt: ~/.sina/trustfield-msb-sandbox-story-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "trustfield-msb-compliance-sandbox-story-v1.json"
BEATS = ROOT / "data" / "trustfield-commercial-film-beats-v1.json"
RECEIPT = SINA / "trustfield-msb-sandbox-story-receipt-v1.json"

FORBIDDEN = ("mac only", "only on mac", "mac-only", "requires a mac")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _sandbox_beat(beats: dict) -> dict | None:
    for beat in beats.get("beats") or []:
        if str(beat.get("id") or "").upper() == "SANDBOX":
            return beat
    return None


def assess(*, write: bool = True) -> dict:
    story = _read(SSOT)
    beats = _read(BEATS)
    sandbox = _sandbox_beat(beats) or {}
    blob = json.dumps({**story, **beats}).lower()

    checks: list[dict] = []
    checks.append(
        {
            "id": "schema",
            "ok": story.get("schema") == "trustfield-msb-compliance-sandbox-story-v1",
            "detail": story.get("schema"),
        }
    )
    checks.append({"id": "lane", "ok": story.get("lane") == "trustfield", "detail": story.get("lane")})
    live_ok = bool(sandbox.get("live_sandbox")) and str(sandbox.get("id") or "").upper() == "SANDBOX"
    checks.append(
        {
            "id": "live_sandbox_beat",
            "ok": live_ok,
            "detail": sandbox.get("id") or "missing SANDBOX beat",
        }
    )
    rpaa_ok = "rpaa" in blob and "pilot" in blob and "sandbox" in blob
    checks.append(
        {
            "id": "rpaa_pilot_narrative",
            "ok": rpaa_ok,
            "detail": "rpaa+pilot+sandbox" if rpaa_ok else "RPAA pilot narrative incomplete",
        }
    )
    forbidden_hit = next((f for f in FORBIDDEN if f in blob), None)
    checks.append(
        {
            "id": "platform_neutral",
            "ok": forbidden_hit is None,
            "detail": "ok" if forbidden_hit is None else forbidden_hit,
        }
    )

    ok = all(c.get("ok") for c in checks)
    row = {
        "schema": "trustfield-msb-sandbox-story-receipt-v1",
        "at": _now(),
        "ok": ok,
        "tf_sandbox_line": (
            f"TrustField MSB sandbox · live_beat={live_ok} · rpaa_pilot={rpaa_ok} · "
            f"checks={sum(1 for c in checks if c.get('ok'))}/{len(checks)}"
        ),
        "ssot": str(SSOT.relative_to(ROOT)),
        "phase0_id": "P0-06",
        "checks": checks,
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="TrustField MSB sandbox story assess")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = assess(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("tf_sandbox_line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
