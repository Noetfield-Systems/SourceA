#!/usr/bin/env python3
"""Single connected gate — session + strict outbound + coherence + inbox latch + hub."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-worker-connected-receipt-v1.json"
HUB_URL = "http://127.0.0.1:13020/api/worker-hub/v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _hub_api_ok() -> dict:
    try:
        req = urllib.request.Request(HUB_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {"ok": resp.status == 200 and body.get("ok", True), "status": resp.status, "hub": body}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "error": str(exc)}


def assess_connected(*, hub_check: bool = True, write_receipt: bool = True) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from outbound_queue_coherence_v1 import assess_queue_coherence, compose_outbound_progress_line  # noqa: WPS433
    from validate_outbound_receipt_path_v1 import validate as validate_receipt  # noqa: WPS433
    from validate_outbound_acceptance_proof_v1 import validate as validate_acceptance  # noqa: WPS433
    from execution_plane_honesty_v1 import assess_execution_plane  # noqa: WPS433

    coherence = assess_queue_coherence()
    receipt = validate_receipt()
    acceptance = validate_acceptance()
    honesty = assess_execution_plane()
    inbox = _read(SINA / "worker-prompt-inbox-v1.json")
    head = coherence.get("head") or {}
    inbox_pending = bool(inbox.get("pending"))
    inbox_uid = str((inbox.get("meta") or {}).get("upgrade_id") or "")
    head_uid = str(head.get("upgrade_id") or "")
    inbox_latch_ok = (not inbox_pending) or inbox_uid == head_uid or not head_uid

    hub_row = _hub_api_ok() if hub_check else {"ok": True, "skipped": True}
    hub_connected = True
    if hub_check and hub_row.get("hub"):
        hub_connected = bool((hub_row.get("hub") or {}).get("connected", True))

    checks = {
        "coherence": bool(coherence.get("ok")),
        "receipt_path": bool(receipt.get("ok")),
        "acceptance_proof": bool(acceptance.get("ok")),
        "execution_plane": bool(honesty.get("ok")),
        "inbox_latch": inbox_latch_ok,
        "hub_api": bool(hub_row.get("ok")),
        "hub_connected_badge": hub_connected,
    }
    ok = all(checks.values())
    row = {
        "schema": "sourcea-worker-connected-receipt-v1",
        "at": _now(),
        "ok": ok,
        "connected": ok,
        "checks": checks,
        "coherence": coherence,
        "receipt_path": {"ok": receipt.get("ok"), "issues": receipt.get("issues")},
        "acceptance": {"ok": acceptance.get("ok"), "failed": acceptance.get("failed")},
        "execution_honesty_line": honesty.get("execution_honesty_line"),
        "outbound_progress_line": compose_outbound_progress_line(),
        "inbox_pending": inbox_pending,
        "head_upgrade_id": head_uid,
        "hub": hub_row,
        "command": "bash scripts/validate-sourcea-worker-connected-v1.sh",
        "line": (
            "worker-connected · PASS"
            if ok
            else "worker-connected · BLOCK:" + next(k for k, v in checks.items() if not v)
        ),
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA Worker connected gate")
    ap.add_argument("--no-hub", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = assess_connected(hub_check=not args.no_hub)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or ("PASS" if row.get("ok") else "FAIL"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
