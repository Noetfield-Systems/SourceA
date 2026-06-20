#!/usr/bin/env python3
"""H2 weekly machine receipt bundle — regen cadence (never on Hub 1 daily refresh).

Law: SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md · integration-fabric build_cadence_schedule.weekly
Receipt: ~/.sina/h2-machine-weekly-bundle-receipt-v1.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "h2-machine-weekly-bundle-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_hub_health(*, timeout: int = 45) -> bool:
    import time
    import urllib.error
    import urllib.request

    base = "http://127.0.0.1:13020/health"

    def _probe() -> bool:
        try:
            with urllib.request.urlopen(base, timeout=3) as resp:
                return resp.status == 200
        except (OSError, urllib.error.URLError):
            return False

    if _probe():
        return True
    subprocess.run(
        ["bash", str(SCRIPTS / "serve-sina-command.sh")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _probe():
            return True
        time.sleep(1)
    return False


def _run_py(script: str, *args: str, timeout: int = 120) -> dict:
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or "") + (proc.stderr or "")
        detail = {}
        if "{" in out:
            try:
                detail = json.loads(out[out.find("{") :])
            except json.JSONDecodeError:
                detail = {}
        return {"ok": proc.returncode == 0, "exit": proc.returncode, "detail": detail}
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit": -1, "error": "timeout"}


def run_weekly_bundle(*, reason: str = "weekly") -> dict:
    steps: list[dict] = []

    recon = _run_py("h2_pending_registry_reconcile_v1.py", "--json")
    steps.append({"step": "h2_registry_reconcile", **recon})

    heal = _run_py("hub_dual_heal_v1.py", "--json", "--reason", f"h2-weekly-bundle:{reason}")
    steps.append({"step": "hub_dual_heal", **heal})

    hub_up = _ensure_hub_health()
    steps.append({"step": "ensure_hub_health", "ok": hub_up})

    try:
        proc = subprocess.run(
            ["bash", str(SCRIPTS / "validate-machine-hub-v1.sh")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        steps.append({"step": "validate_machine_hub", "ok": proc.returncode == 0})
    except subprocess.TimeoutExpired:
        steps.append({"step": "validate_machine_hub", "ok": False, "error": "timeout"})

    surface = _run_py("hub_surface_v1.py", "--json", timeout=90)
    steps.append({"step": "hub_surface_slices", **surface})

    core_ok = all(
        s.get("ok")
        for s in steps
        if s["step"] in ("h2_registry_reconcile", "hub_dual_heal", "ensure_hub_health", "validate_machine_hub")
    )
    row = {
        "ok": core_ok,
        "schema": "h2-machine-weekly-bundle-v1",
        "at": _now(),
        "reason": reason,
        "cadence": "weekly",
        "law": "integration-fabric-registry-v1.yaml build_cadence_schedule.weekly h2-machine-bundle",
        "forbidden_on": ["h1-light-refresh", "worker_turn", "founder_daily_tap"],
        "steps": steps,
        "receipts": {
            "registry": str(SINA / "h2-pending-registry-v1.json"),
            "dual_heal": str(SINA / "two-hub-heal-receipt-v1.json"),
            "bundle": str(RECEIPT),
        },
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if core_ok:
        try:
            from h2_machine_hub_evidence_v1 import append_priority_h2_weekly_ship_evidence  # noqa: WPS433

            row["evidence_append"] = append_priority_h2_weekly_ship_evidence()
        except Exception as exc:  # noqa: BLE001
            row["evidence_append"] = {"ok": False, "error": str(exc)}
            RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="H2 weekly machine receipt bundle")
    p.add_argument("--json", action="store_true")
    p.add_argument("--reason", default="cli")
    args = p.parse_args()
    row = run_weekly_bundle(reason=args.reason)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"H2-WEEKLY-BUNDLE: ok={row.get('ok')} at={row.get('at')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
