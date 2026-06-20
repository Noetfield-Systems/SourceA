#!/usr/bin/env python3
"""Map better-loop commercial_red ship checks → OEGCC linter rule ids.

Law: docs/SOURCEA_OUTBOUND_EMAIL_GENERATOR_CHECKER_CONTROLLER_LOOP_LOCKED_v1.md §8.4
Used by: agent_nerve_system_v1 · loop_observatory_report_v1 · better_loop_pulse_v1
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "outbound-email-oegcc-v1.json"
PY = sys.executable

# Static hints when a commercial gate fails without running the linter on a draft.
CHECK_TO_RULE_HINTS: dict[str, list[str]] = {
    "oegcc_linter": [],
    "w3_output_clean": ["forbidden_one", "lane_forbidden", "salvage_pattern"],
    "w3_sina_read": ["ship_gate:w3_sina_read"],
    "w3_critic_circle": ["ship_gate:w3_critic_circle"],
    "w3_receiver_interest": ["ship_gate:w3_receiver_interest"],
    "w3_conversation_interest": ["ship_gate:w3_conversation_interest"],
    "w3_rrl": ["ship_gate:w3_rrl"],
    "w3_sends": ["ship_gate:approved_not_sent"],
}


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def probe_oegcc_linter_fail_ids(*, lane: str = "", region: str = "canada") -> list[str]:
    """Run linter on canonical fail fixture — returns structured rule ids."""
    fixture = SCRIPTS / "fixtures/outbound-email-linter/fail_opener.txt"
    if not fixture.is_file():
        return []
    try:
        sys.path.insert(0, str(SCRIPTS))
        from outbound_email_linter_v1 import lint_email  # noqa: WPS433

        body = fixture.read_text(encoding="utf-8")
        row = lint_email(body, lane=lane, region=region)
        return sorted(
            {
                str(f.get("id") or "")
                for f in row.get("failures") or []
                if f.get("id") and str(f.get("severity") or "fail") == "fail"
            }
        )
    except Exception:
        return []


def probe_oegcc_controller(*, simulate: bool = False) -> dict[str, Any]:
    """Read controller receipt or run --simulate when missing/stale."""
    receipt_path = SINA / "outbound-email-controller-receipt-v1.json"
    receipt = _read_json(receipt_path)
    if simulate or not receipt.get("at"):
        try:
            subprocess.run(
                [PY, str(SCRIPTS / "outbound_email_controller_v1.py"), "--simulate", "--json"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            receipt = _read_json(receipt_path)
        except (subprocess.SubprocessError, OSError):
            receipt = receipt or {}
    ok = bool(receipt.get("ok"))
    hist = receipt.get("rule_histogram") or {}
    top_rules = sorted(hist.keys(), key=lambda k: (-int(hist[k]), k))[:5]
    return {
        "ok": ok,
        "outcome": receipt.get("outcome"),
        "attempts_used": receipt.get("attempts_used"),
        "rule_histogram": hist,
        "top_rule_ids": top_rules,
        "never_auto_send": receipt.get("never_auto_send", True),
        "line": receipt.get("line") or ("oegcc-controller · no receipt" if not receipt else ""),
    }


def map_commercial_reds(
    ship_checks: list[dict],
    *,
    oegcc_probe: dict | None = None,
    controller_probe: dict | None = None,
) -> dict[str, Any]:
    """Enrich commercial ship check failures with OEGCC linter rule ids."""
    reds = [c for c in ship_checks if c.get("class") == "commercial" and not c.get("ok")]
    fail_fixture_ids = probe_oegcc_linter_fail_ids()
    mapped: list[dict] = []
    all_rule_ids: list[str] = []

    for r in reds:
        cid = str(r.get("id") or "")
        rule_ids: list[str] = []
        source = "static_map"

        if cid == "oegcc_linter":
            source = "linter_probe"
            if oegcc_probe and oegcc_probe.get("failure_ids"):
                rule_ids = list(oegcc_probe.get("failure_ids") or [])
            elif oegcc_probe and not oegcc_probe.get("ok"):
                rule_ids = fail_fixture_ids or ["linter_smoke_fail"]
        else:
            rule_ids = list(CHECK_TO_RULE_HINTS.get(cid) or [f"commercial:{cid}"])

        if controller_probe and not controller_probe.get("ok"):
            for rid in controller_probe.get("top_rule_ids") or []:
                if rid not in rule_ids:
                    rule_ids.append(rid)

        mapped.append(
            {
                "check_id": cid,
                "label": r.get("label"),
                "detail": r.get("detail"),
                "rule_ids": rule_ids,
                "source": source,
            }
        )
        all_rule_ids.extend(rule_ids)

    unique_rules = sorted(set(all_rule_ids))
    rules_bit = ",".join(unique_rules[:6]) if unique_rules else "none"
    if len(unique_rules) > 6:
        rules_bit += f"+{len(unique_rules) - 6}"
    line = f"commercial-red · n={len(reds)} · rules={rules_bit}"

    return {
        "schema": "oegcc-commercial-red-map-v1",
        "commercial_red_count": len(reds),
        "mapped": mapped,
        "rule_ids": unique_rules,
        "fail_fixture_rule_ids": fail_fixture_ids,
        "line": line,
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="OEGCC commercial red → linter rule map")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--simulate-controller", action="store_true")
    args = ap.parse_args()

    bl = _read_json(SINA / "better-loop-pulse-receipt-v1.json")
    checks = bl.get("ship_checks") or bl.get("founder_checks") or []
    ctrl = probe_oegcc_controller(simulate=args.simulate_controller)
    row = map_commercial_reds(checks, controller_probe=ctrl)
    row["controller"] = ctrl
    row["ssot"] = str(SSOT.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
