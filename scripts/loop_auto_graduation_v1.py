#!/usr/bin/env python3
"""Auto Runtime graduation — enable shadow auto loop (observe + dispatch) after validators PASS.

Law: data/loop-specialist-cloud-contract-v1.json · CL10
Receipt: ~/.sina/loop-auto-graduation-receipt-v1.json
Founder motion: Hub glance · no RUN INBOX verb when loop_auto_dispatch_enabled
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
CONFIG = SINA / "loop-specialist-config-v1.json"
RECEIPT = SINA / "loop-auto-graduation-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()[-500:]


def graduate(*, mode: str = "shadow_auto", write: bool = True) -> dict:
    checks: list[dict] = []
    for label, cmd in [
        ("validate_loop_specialist", ["bash", "scripts/validate-loop-specialist-v1.sh"]),
        ("validate_loop_chain_e2e", ["bash", "scripts/validate-loop-chain-e2e-v1.sh"]),
        ("validate_disclosure_ladder", ["bash", "scripts/validate-disclosure-ladder-v1.sh"]),
        ("validate_mcp_stack_free_tier", ["bash", "scripts/validate-mcp-stack-free-tier-v1.sh"]),
        ("validate_tool_pick_two_phase", ["bash", "scripts/validate-tool-pick-two-phase-v1.sh"]),
        ("validate_plans_unified", ["bash", "scripts/validate-plans-unified-upgrade-v1.sh"]),
        ("validate_anti_theater", ["bash", "scripts/validate-anti-theater-validator-loop-v1.sh"]),
        ("validate_platform_neutral", ["bash", "scripts/validate-platform-neutral-world-model-v1.sh"]),
        ("validate_full_stack_fix_plan", ["bash", "scripts/validate-full-stack-100-fix-plan-v1.sh"]),
    ]:
        code, tail = _run(cmd)
        checks.append({"check": label, "ok": code == 0, "tail": tail})

    ok = all(c["ok"] for c in checks)
    sys.path.insert(0, str(SCRIPTS))
    from loop_specialist_tick_v1 import load_config, save_config  # noqa: WPS433

    cfg = load_config()
    if ok and mode in ("shadow_auto", "full_auto"):
        cfg["loop_auto_dispatch_enabled"] = True
        cfg["loop_auto_observe_enabled"] = True
        cfg["loop_auto_mode"] = mode
        cfg["founder_motion"] = "Hub glance only · Auto Runtime specialist auto-tick · no RUN INBOX verb"
        cfg["graduated_at"] = _now()
        save_config(cfg)
        subprocess.run(
            [sys.executable, str(SCRIPTS / "loop_specialist_tick_v1.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=90,
        )
    elif mode == "off":
        cfg["loop_auto_dispatch_enabled"] = False
        cfg["loop_auto_mode"] = "off"
        cfg["founder_motion"] = "ASF resume Cloud Forge Run when FREEZE · Auto Runtime specialist tick on Hub"
        save_config(cfg)

    row = {
        "schema": "loop-auto-graduation-receipt-v1",
        "ok": ok or mode == "off",
        "at": _now(),
        "mode": mode,
        "checks": checks,
        "config_path": str(CONFIG),
        "loop_auto_dispatch_enabled": bool(cfg.get("loop_auto_dispatch_enabled")),
        "founder_motion": cfg.get("founder_motion"),
        "command": "python3 scripts/loop_auto_graduation_v1.py --enable-shadow --json",
        "hub_api": "POST /api/loop-specialist/tick/v1 {\"enable_auto_dispatch\": true}",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Auto Runtime graduation")
    ap.add_argument("--enable-shadow", action="store_true")
    ap.add_argument("--enable-full", action="store_true")
    ap.add_argument("--disable", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.disable:
        row = graduate(mode="off")
    elif args.enable_full:
        row = graduate(mode="full_auto")
    elif args.enable_shadow:
        row = graduate(mode="shadow_auto")
    else:
        row = graduate(mode="shadow_auto", write=False)
        row["note"] = "dry-run preview — pass --enable-shadow to graduate"
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_motion") or ("ok" if row.get("ok") else "FAIL"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
