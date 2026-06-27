#!/usr/bin/env python3
"""Pre-write guard — one fast check before any agent disk edit.

Combines cross_lane_edit_guard + live SASCIP posture + panic flags.
Law: docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
LIVE_WIRE = SINA / "stranger-agent-safety-live-wire-v1.json"
SASCIP_RECEIPT = SINA / "stranger-agent-admission-receipt-v1.json"


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _resolve_target(path: str) -> Path:
    p = Path(path.replace("~/", str(Path.home()) + "/"))
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    else:
        p = p.resolve()
    return p


def check_pre_write(*, agent: str, path: str, explicit_order: str = "") -> dict:
    path = str(_resolve_target(path))
    sys.path.insert(0, str(SCRIPTS))
    from cross_lane_edit_guard_v1 import check_edit  # noqa: WPS433

    guard = check_edit(agent=agent, path=path, explicit_order=explicit_order)
    live = _read_json(LIVE_WIRE)
    admission = live.get("admission") or _read_json(SASCIP_RECEIPT).get("classification") or {}

    cancel_flag = SINA / "agent-cancel-v1.flag"
    emergency_flag = SINA / "mac-health-emergency-active-v1.flag"
    panic_active = cancel_flag.is_file() or emergency_flag.is_file()

    blockers: list[str] = []
    ui_baseline: dict | None = None
    if panic_active:
        blockers.append("PANIC_FLAG_ACTIVE")
    sascip = _read_json(SASCIP_RECEIPT)
    cls = sascip.get("classification") or admission
    stranger = cls.get("stranger") if isinstance(cls, dict) else False
    if stranger and not explicit_order.strip():
        blockers.append("STRANGER_QUARANTINE")
    tier = live.get("admission", {}).get("trust_tier") or cls.get("trust_tier") or admission.get("trust_tier")
    if tier == "T6_hostile_block":
        blockers.append("HOSTILE_TIER")

    if bool(guard.get("allowed")) and not blockers:
        from ui_upgrade_baseline_guard_v1 import check_path, is_controlled_ui_path  # noqa: WPS433
        from ui_upgrade_first_check_v1 import check_write as ui_first_check  # noqa: WPS433

        ui_first = ui_first_check(path=path, explicit_order=explicit_order)
        if not ui_first.get("ok") and not ui_first.get("skipped"):
            blockers.append("UI_UPGRADE_FIRST_CHECK_REQUIRED")
            ui_baseline = ui_first
        elif is_controlled_ui_path(path):
            ui_baseline = check_path(path)
            if not ui_baseline.get("ok"):
                blockers.append("UI_BASELINE_FAIL")

    allowed = bool(guard.get("allowed")) and not blockers

    if allowed and not explicit_order.strip():
        try:
            from mac_law_universal_wire_v1 import check_pre_write  # noqa: WPS433

            ml = check_pre_write(path=path)
            if not ml.get("ok"):
                for b in ml.get("blockers") or []:
                    blockers.append(str(b))
        except Exception:
            pass

    allowed = bool(guard.get("allowed")) and not blockers
    rule_hook: dict | None = None
    if allowed:
        try:
            from rule_zero_latency_hook_v1 import is_rule_governance_path, maybe_hook_after_pre_write  # noqa: WPS433

            if is_rule_governance_path(path):
                rule_hook = maybe_hook_after_pre_write(path=path, agent=agent)
        except Exception as exc:
            rule_hook = {"ok": False, "error": str(exc)[:120], "step": "rule_zero_latency_hook"}

    return {
        "ok": allowed,
        "allowed": allowed,
        "agent": guard.get("agent") or agent,
        "path": guard.get("path") or path,
        "cross_lane": guard,
        "blockers": blockers,
        "ui_baseline": ui_baseline,
        "trust_tier": live.get("admission", {}).get("trust_tier") or admission.get("trust_tier"),
        "sascip_safety_line": live.get("sascip_safety_line"),
        "law": "STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md",
        "rule_zero_latency_hook": rule_hook,
        "message": (
            "write allowed"
            if allowed
            else (
                ui_baseline.get("message")
                if "UI_UPGRADE_FIRST_CHECK_REQUIRED" in blockers and isinstance(ui_baseline, dict)
                else (
                    "UI baseline fail — run: python3 scripts/ui_upgrade_baseline_guard_v1.py check --path \""
                    + path
                    + "\" --json"
                    if "UI_BASELINE_FAIL" in blockers
                    else (blockers[0] if blockers else guard.get("message") or "write blocked")
                )
            )
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-write guard")
    ap.add_argument("cmd", choices=("check", "post-write"))
    ap.add_argument("--agent", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--explicit-order", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.cmd == "post-write":
        sys.path.insert(0, str(SCRIPTS))
        from rule_zero_latency_hook_v1 import run_hook  # noqa: WPS433

        row = run_hook(path=args.path, reason=f"post_write:{args.agent}", tier="fast", sync_cursor_index=True)
        try:
            from rule_zero_latency_hook_v1 import is_rule_governance_path  # noqa: WPS433
            from anti_poison_lib_v1 import scan_file, ship_window_active, mac_founder_session  # noqa: WPS433

            if is_rule_governance_path(args.path):
                hits = scan_file(_resolve_target(args.path))
                row["anti_poison_post_write"] = {
                    "hits": len(hits),
                    "ok": len(hits) == 0,
                    "sample": hits[:3],
                }
                if hits and ship_window_active() and not mac_founder_session():
                    row["ok"] = False
                    row["anti_poison_post_write"]["block"] = "ship_window_poison_in_new_rule"
        except Exception as exc:
            row["anti_poison_post_write"] = {"ok": True, "skipped": str(exc)[:80]}
    else:
        row = check_pre_write(agent=args.agent, path=args.path, explicit_order=args.explicit_order)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print("allowed" if row.get("allowed") else f"blocked: {row.get('message')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
