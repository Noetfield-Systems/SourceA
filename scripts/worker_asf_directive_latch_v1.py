#!/usr/bin/env python3
"""ASF directive latch — fail-closed memory for founder stop phrases (INCIDENT-031)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

LATCH = Path.home() / ".sina" / "worker-asf-directive-latch-v1.json"

STOP_PHRASES = (
    "no hub rebuild",
    "no need to hub",
    "no need to help rebuild",
    "stop hub",
    "no hub archive",
    "don't touch hub",
    "do not touch hub",
)

PLAN_PHRASES = (
    "give me your plan",
    "give me the plan",
    "give me a plan",
    "just the plan",
    "plan only",
    "no help",
    "don't help",
    "do not help",
    "stop helping",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_latch() -> dict:
    if not LATCH.is_file():
        return {}
    try:
        return json.loads(LATCH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_latch(data: dict) -> dict:
    LATCH.parent.mkdir(parents=True, exist_ok=True)
    LATCH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def set_plan_only(*, note: str = "") -> dict:
    data = read_latch()
    data.update(
        {
            "schema": "worker-asf-directive-latch-v1",
            "plan_only": True,
            "chat_first": True,
            "set_at": _now(),
            "plan_note": note or "ASF plan-only — no help/implement until run inbox",
            "incident": "INCIDENT-031",
        }
    )
    write_latch(data)
    try:
        from founder_directive_ssot_v1 import sync_all_layers  # noqa: WPS433

        sync_all_layers(stairlift=True)
    except Exception:
        pass
    return data


def set_no_hub(*, note: str = "") -> dict:
    data = read_latch()
    sticky = {
        k: data[k]
        for k in ("command_retired_forever", "hub2_drain_allowed", "hub_status")
        if data.get(k) is not None
    }
    data.update(
        {
            "schema": "worker-asf-directive-latch-v1",
            "no_hub": True,
            "no_hub_rebuild": True,
            "no_hub_archive": True,
            "hub_status": sticky.get("hub_status") or "ARCHIVED_CLOSED",
            "set_at": _now(),
            "note": note or data.get("note") or "ASF no-hub stop",
            "incident": "INCIDENT-031",
        }
    )
    if sticky.get("command_retired_forever"):
        data["command_retired_forever"] = True
        data["hub_status"] = "COMMAND_RETIRED_FOREVER"
    if sticky.get("hub2_drain_allowed"):
        data["hub2_drain_allowed"] = True
    write_latch(data)
    try:
        from founder_directive_ssot_v1 import sync_all_layers  # noqa: WPS433

        sync_all_layers(stairlift=True)
    except Exception:
        pass
    return data


def clear_latch() -> dict:
    data = {"schema": "worker-asf-directive-latch-v1", "no_hub": False, "cleared_at": _now()}
    return write_latch(data)


def directive_block() -> str:
    lat = read_latch()
    lines: list[str] = []
    if lat.get("no_hub"):
        if lat.get("command_retired_forever"):
            lines += [
                "=== ASF DIRECTIVE LATCH (Command RETIRED — mandatory) ===",
                "Hub only (H1 / + H2 /machines/) · Sina Command name retired · /legacy/ must not serve.",
                "FORBIDDEN: /legacy/ route, Sina Command UI strings, build-sina-command-panel for daily use.",
                "ALLOWED: Hub 2 validators, factory CHECK→ACT→VERIFY when hub2_drain_allowed.",
            ]
        elif lat.get("hub2_drain_allowed"):
            lines += [
                "=== ASF DIRECTIVE LATCH (INCIDENT-031 — mandatory) ===",
                "Sina Command: QUARANTINE — no rebuild, no archive homework, no /legacy/ daily.",
                "Hub 2 drain: ALLOWED — phase-s8 backlog under SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md.",
                "FORBIDDEN: hub_self_refresh, build-sina-command-panel, Sina Command app.js patches.",
                "ALLOWED: Hub 2 validators, h2-pending-registry, machines/ receipts, factory CHECK→ACT→VERIFY.",
            ]
        else:
            lines += [
                "=== ASF DIRECTIVE LATCH (INCIDENT-031 — mandatory) ===",
                "no_hub: TRUE — founder forbade Sina Command rebuild, archive, refresh homework.",
                "FORBIDDEN this session: hub_self_refresh, build-sina-command-panel, phase-s8 sa picks.",
                "ALLOWED: research queue, non-hub sa per ASF order, factory/broker discipline.",
            ]
    if lat.get("plan_only"):
        lines += [
            "=== ASF PLAN-ONLY LATCH (mandatory) ===",
            "plan_only: TRUE — founder asked for PLAN, not help, not implement, not queue rebuild.",
            "REPLY FORMAT: numbered plan bullets only · cite disk truth · zero suggestions about 'next order rebuild'.",
            "FORBIDDEN: auto-pickup · run inbox · sa CHECK/ACT until founder says 'run inbox'.",
            "READ founder latest chat message verbatim before any disk queue work.",
        ]
    if not lines:
        return ""
    if lat.get("note"):
        lines.append(f"note: {lat['note']}")
    if lat.get("plan_note"):
        lines.append(f"plan_note: {lat['plan_note']}")
    if lat.get("set_at"):
        lines.append(f"set_at: {lat['set_at']}")
    return "\n".join(lines) + "\n"


def detect_plan_in_text(text: str) -> bool:
    t = (text or "").lower()
    return any(p in t for p in PLAN_PHRASES)


def detect_and_apply(text: str) -> dict:
    """Scan founder message — set latch flags (agent or script, not founder Terminal)."""
    low = (text or "").lower()
    if "cascade proof test" in low or low.startswith("validator_proof:"):
        return read_latch()
    if detect_stop_in_text(text):
        set_no_hub(note=f"auto-detect: {(text or '')[:120]}")
    if detect_plan_in_text(text):
        set_plan_only(note=f"auto-detect: {(text or '')[:120]}")
    return read_latch()


def detect_stop_in_text(text: str) -> bool:
    t = (text or "").lower()
    return any(p in t for p in STOP_PHRASES)


def main() -> int:
    ap = argparse.ArgumentParser(description="ASF directive latch (INCIDENT-031)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_set = sub.add_parser("set", help="Set latch flags")
    p_set.add_argument("--no-hub", action="store_true", help="Block hub lane steering")
    p_set.add_argument("--plan-only", action="store_true", help="Plan-only — no help/implement until run inbox")
    p_set.add_argument("--note", default="", help="Optional note")

    sub.add_parser("clear", help="Clear latch")
    sub.add_parser("show", help="Print latch JSON")
    sub.add_parser("block", help="Print directive block for turn context")

    p_detect = sub.add_parser("detect", help="Detect stop phrases in stdin/text")
    p_detect.add_argument("--text", default="", help="Text to scan")

    p_detect.add_argument("--apply", action="store_true", help="Set latch if phrases detected")

    args = ap.parse_args()
    if args.cmd == "set":
        if args.no_hub:
            print(json.dumps(set_no_hub(note=args.note), indent=2))
            return 0
        if args.plan_only:
            print(json.dumps(set_plan_only(note=args.note), indent=2))
            return 0
        print(json.dumps({"ok": False, "error": "specify --no-hub"}, indent=2))
        return 1
    if args.cmd == "clear":
        print(json.dumps(clear_latch(), indent=2))
        return 0
    if args.cmd == "show":
        print(json.dumps(read_latch() or {"no_hub": False}, indent=2))
        return 0
    if args.cmd == "block":
        print(directive_block(), end="")
        return 0
    if args.cmd == "detect":
        if args.apply and args.text:
            print(json.dumps(detect_and_apply(args.text), indent=2))
            return 0
        hit = detect_stop_in_text(args.text) or detect_plan_in_text(args.text)
        print(json.dumps({"detected": hit}, indent=2))
        return 0 if hit else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
