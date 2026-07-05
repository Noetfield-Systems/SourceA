#!/usr/bin/env python3
"""Nightly Kaizen — one highest-ROI machine_safe improvement_queue item.

fix → verify → external-verify receipt → auto-rollback on regression.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HANDLERS = ROOT / "data/kaizen-fix-handlers-v1.json"
RECEIPT_DIR = ROOT / "receipts/cloud/kaizen/nightly"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_secrets() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import ensure_env  # noqa: WPS433

    ensure_env()


def _supabase() -> tuple[str, str]:
    _load_secrets()
    return os.environ.get("SUPABASE_URL", "").strip().rstrip("/"), os.environ.get(
        "SUPABASE_SERVICE_ROLE_KEY", ""
    ).strip()


def _pick_queue_item() -> dict[str, Any] | None:
    url, key = _supabase()
    if not url or not key:
        return None
    q = (
        f"{url}/rest/v1/improvement_queue"
        "?select=*&status=eq.open&machine_safe=eq.true"
        "&order=expected_roi.desc.nullslast,created_at.asc&limit=1"
    )
    req = urllib.request.Request(
        q,
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
    return rows[0] if isinstance(rows, list) and rows else None


def _patch_queue(item_id: str, patch: dict[str, Any]) -> None:
    url, key = _supabase()
    req = urllib.request.Request(
        f"{url}/rest/v1/improvement_queue?id=eq.{item_id}",
        data=json.dumps({**patch, "updated_at": _now()}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "return=minimal",
        },
        method="PATCH",
    )
    urllib.request.urlopen(req, timeout=25)


def _handler_for_finding(finding: str) -> dict[str, Any] | None:
    row = json.loads(HANDLERS.read_text(encoding="utf-8"))
    for h in row.get("handlers") or []:
        prefix = str(h.get("finding_prefix") or "")
        if prefix and finding.startswith(prefix) and h.get("script"):
            return h
    return None


def _run_cmd(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


def _external_verify_receipt(recipe_id: str) -> dict[str, Any]:
    """Reserved — nightly uses disk validators (no founder_proof_15 on Railway)."""
    return {"ok": False, "skipped": True, "recipe": recipe_id}


def run_nightly() -> dict[str, Any]:
    cfg = json.loads(HANDLERS.read_text(encoding="utf-8"))
    item = _pick_queue_item()
    if not item:
        return {
            "schema": "kaizen-nightly-tick-v1",
            "ok": True,
            "at": _now(),
            "decision": "IDLE_NO_WORK",
            "report_line": "kaizen_nightly · IDLE_NO_WORK",
        }

    item_id = str(item.get("id"))
    finding = str(item.get("finding") or "")
    handler = _handler_for_finding(finding)
    _patch_queue(item_id, {"status": "in_progress"})

    fix_ok = True
    fix_log = ""
    if handler:
        script = str(handler.get("script"))
        code, fix_log = _run_cmd([sys.executable, script])
        fix_ok = code == 0
    else:
        fix_ok = False
        fix_log = "no_machine_handler"

    verify = str((handler or {}).get("verify") or "scripts/sandbox_health_sweep_v1.py")
    if verify.endswith(".sh"):
        vcode, vout = _run_cmd(["bash", str(ROOT / verify)])
    else:
        parts = verify.split()
        rel = parts[0]
        rest = parts[1:]
        vcode, vout = _run_cmd([sys.executable, str(ROOT / rel), *rest])

    regression = vcode != 0
    if regression and handler and handler.get("script"):
        subprocess.run(["git", "checkout", "--", "."], cwd=ROOT, check=False)

    recipe = str(cfg.get("nightly", {}).get("external_verify_recipe") or "cpr-eval-boot")
    ext = {"ok": not regression and fix_ok, "verify": "sandbox_health_sweep", "recipe": recipe}
    if fix_ok and not regression:
        v2code, _ = _run_cmd([sys.executable, "scripts/validate-noetfield-nerve-probe-v1.sh"])
        ext["nerve_probe_disk"] = v2code == 0
        ext["ok"] = ext["ok"] and v2code == 0

    status = "done" if fix_ok and not regression and ext.get("ok") else "founder_gated"
    _patch_queue(item_id, {"status": status})

    row = {
        "schema": "kaizen-nightly-tick-v1",
        "ok": status == "done",
        "at": _now(),
        "decision": "COMPLETE" if status == "done" else "BLOCKED",
        "queue_item_id": item_id,
        "finding": finding[:500],
        "handler": handler.get("id") if handler else None,
        "fix_ok": fix_ok,
        "verify_exit": vcode,
        "regression_rollback": regression,
        "external_verify": {"ok": ext.get("ok"), "recipe": recipe},
        "report_line": f"kaizen_nightly · {status} · {finding[:60]}",
    }
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    (RECEIPT_DIR / f"kaizen-nightly-{datetime.now(timezone.utc).strftime('%Y%m%d')}-v1.json").write_text(
        json.dumps(row, indent=2) + "\n",
        encoding="utf-8",
    )

    sys.path.insert(0, str(ROOT / "scripts"))
    from telegram_alert_v1 import send_telegram_alert  # noqa: WPS433

    send_telegram_alert(f"<b>Kaizen nightly</b> · {status}\n{finding[:350]}")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_nightly()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line", ""))
    return 0 if row.get("ok") or row.get("decision") == "IDLE_NO_WORK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
