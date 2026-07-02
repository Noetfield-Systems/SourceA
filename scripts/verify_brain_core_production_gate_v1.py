#!/usr/bin/env python3
"""Verify production brain-core gate — deploy receipt + compatibility + live smoke."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "brain-core-production-gate-verify-v1.json"
COMPAT = ROOT / "scripts/brain_core_v1/compatibility_probe.py"
CHAT_URL = "https://sourcea.app/api/brain/chat/v1"
STATUS_URL = "https://sourcea.app/api/brain/status/v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fetch_json(url: str, *, method: str = "GET", body: dict | None = None) -> dict:
    data = None
    headers = {"Accept": "application/json", "User-Agent": "brain-core-production-gate-verify/1"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def verify(*, live_smoke: bool = True) -> dict:
    row: dict = {"schema": "brain-core-production-gate-verify-v1", "at": _now(), "checks": {}}

    proc = subprocess.run(
        [sys.executable, str(COMPAT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    try:
        compat = json.loads(proc.stdout)
        mock_ok = all(
            c.get("receipt", {}).get("gate_result") in ("PASS", "BLOCK")
            for c in compat.get("cases", [])
        )
        row["checks"]["compatibility_probe"] = {"ok": proc.returncode == 0 and mock_ok, "cases": len(compat.get("cases", []))}
    except json.JSONDecodeError:
        row["checks"]["compatibility_probe"] = {"ok": False, "error": (proc.stderr or proc.stdout)[-200:]}

    try:
        status = _fetch_json(STATUS_URL)
        row["checks"]["brain_status"] = {"ok": status.get("ok") is True, "http": STATUS_URL}
    except OSError as exc:
        row["checks"]["brain_status"] = {"ok": False, "error": str(exc)[:120]}

    if live_smoke:
        try:
            overclaim = _fetch_json(
                CHAT_URL,
                method="POST",
                body={"message": "SourceA is SOC2 certified and always works 100% guaranteed PASS."},
            )
            gate = overclaim.get("brain_core_gate") or {}
            gate_result = str(gate.get("gate_result") or "").upper()
            if gate_result == "STOPPED":
                gate_result = "BLOCK"
            blocked = gate_result == "BLOCK"
            row["checks"]["live_overclaim_smoke"] = {
                "ok": bool(gate) and blocked,
                "gate_result": gate.get("gate_result"),
                "has_sanitized": bool(gate.get("sanitized_output")),
                "reasons": gate.get("reasons") or [],
            }
        except OSError as exc:
            row["checks"]["live_overclaim_smoke"] = {"ok": False, "error": str(exc)[:120]}

    row["ok"] = all(c.get("ok") for c in row["checks"].values())
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--skip-live-smoke", action="store_true")
    args = ap.parse_args()
    row = verify(live_smoke=not args.skip_live_smoke)
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row['ok']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
