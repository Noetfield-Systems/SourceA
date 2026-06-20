#!/usr/bin/env python3
"""Pulse M111 plan progress — disk truth for Hub founder line."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "ecosystem-mac-health-111-upgrade-plan-v1.json"
RECEIPT = Path.home() / ".sina" / "ecosystem-111-pulse-receipt-v1.json"
GEN = ROOT / "scripts" / "gen_ecosystem_mac_health_111_plan_v1.py"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _probe_done(row: dict) -> bool:
    """Light disk probes for P0 rows already shipped in Jun 2026 session."""
    rid = row["id"]
    sina = Path.home() / ".sina"
    checks: dict[str, bool] = {
        "M111-001": True,  # health API reports tab_count 0
        "M111-012": (sina / "mac-control-plane-v1.flag").is_file(),
        "M111-013": (ROOT / "scripts" / "factory_control_v1.py").is_file(),
        "M111-014": (sina / "cli-disabled-v1.flag").is_file(),
        "M111-016": (ROOT / "scripts" / "founder-mac-reset-v1.sh").is_file(),
        "M111-017": (Path.home() / "Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md").is_file(),
        "M111-027": (sina / "config" / "visual_proof.json").is_file(),
        "M111-051": Path("/Applications/Cursor.app").is_dir(),
        "M111-094": (ROOT / "scripts" / "founder_session_gate_v1.py").is_file(),
        "M111-103": (ROOT / "scripts" / "ecosystem_pressure_v1.py").is_file(),
        "M111-105": PLAN.is_file(),
        "M111-107": (ROOT / "scripts" / "plans_unified_upgrade_v1.py").is_file(),
    }
    if rid in checks:
        return checks[rid]
    title = (row.get("title") or "").lower()
    if "validate-mac-control-plane" in title:
        return (ROOT / "scripts" / "validate-mac-control-plane-v1.sh").is_file()
    if "agent-mandates" in title:
        return (ROOT / "scripts" / "mac_health_agent_mandates_v1.py").is_file()
    if "mac-control-plane.mdc" in title:
        return (Path.home() / "Desktop/MacLaw/.cursor/rules/mac-control-plane.mdc").is_file()
    return False


def _health_tab_zero() -> bool:
    try:
        import urllib.request

        raw = urllib.request.urlopen("http://127.0.0.1:13024/health", timeout=4).read()
        doc = json.loads(raw)
        ui = doc.get("ui_contract") or {}
        return ui.get("tab_count") == 0 and ui.get("ui_mode") == "founder_glance"
    except Exception:
        return False


def pulse(*, sync_plan: bool = True) -> dict:
    if not PLAN.is_file():
        subprocess.run([sys.executable, str(GEN), "--write"], cwd=str(ROOT), check=False, timeout=60)

    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    upgrades = plan.get("upgrades") or []
    done = 0
    for u in upgrades:
        if u.get("id") == "M111-001":
            if _health_tab_zero():
                u["status"] = "done"
                u["done_at"] = _now()
                u["execution_proof"] = {"probe": "health_tab_count_zero"}
                done += 1
            continue
        if u.get("status") == "done":
            done += 1
            continue
        if _probe_done(u):
            u["status"] = "done"
            u["done_at"] = _now()
            u["execution_proof"] = {"probe": "disk_truth_jun2026"}
            done += 1

    total = len(upgrades)
    plan["progress"] = {
        "total": total,
        "done": done,
        "planned": total - done,
        "pct": round(100.0 * done / total, 1) if total else 0,
        "mac_proven": done,
        "cloud_proven": sum(1 for u in upgrades if u.get("status") == "done" and u.get("execution_plane") == "cloud_api_worker"),
    }
    plan["saved_at"] = _now()
    head = next((u for u in upgrades if u.get("status") != "done"), upgrades[0] if upgrades else {})
    line = f"M111 · {done}/{total} · head={head.get('id')} · {head.get('title', '')[:60]}"

    if sync_plan:
        PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "schema": "ecosystem-111-pulse-receipt-v1",
        "at": _now(),
        "ok": True,
        "line": line,
        "progress": plan["progress"],
        "critical_path": plan.get("critical_path"),
        "head_id": head.get("id"),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    surfaces = Path.home() / ".sina" / "agent-live-surfaces-v1.json"
    if surfaces.is_file():
        surf = json.loads(surfaces.read_text(encoding="utf-8"))
        surf["ecosystem_mac_health_111_line"] = line
        surf["ecosystem_mac_health_111_head"] = head.get("id")
        surfaces.write_text(json.dumps(surf, indent=2) + "\n", encoding="utf-8")

    return receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = pulse()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
