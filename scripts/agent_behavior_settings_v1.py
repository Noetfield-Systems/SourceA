#!/usr/bin/env python3
"""Agent behavior settings — founder intent first (all roles).

SSOT: data/agent-behavior-settings-v1.json
Receipt: ~/.sina/agent-behavior-settings-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "agent-behavior-settings-v1.json"
RECEIPT = SINA / "agent-behavior-settings-receipt-v1.json"
MIRROR = SINA / "agent-memory-mirror-v1.json"
CURSOR_RULE = ROOT / ".cursor" / "rules" / "agent-founder-intent-first.mdc"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_settings() -> dict:
    return _read(SSOT)


def behavior_line(*, ssot: dict | None = None, role: str = "") -> str:
    row = ssot or load_settings()
    one = str(row.get("one_law") or "Founder intent first")
    truth = str((row.get("truth_hard_concrete") or {}).get("market_posture") or "")
    if role == "brain":
        anchor = (row.get("role_anchors") or {}).get("brain") or {}
        title = str(anchor.get("title") or "Brain")
        return f"behavior · {title} · disk truth · no green theater"
    base = f"behavior · intent-first · {one[:72]}"
    if truth:
        return f"{base} · {truth[:48]}"
    return base


def brain_truth_line(*, ssot: dict | None = None) -> str:
    row = ssot or load_settings()
    anchor = (row.get("role_anchors") or {}).get("brain") or {}
    return (
        f"{anchor.get('title') or 'Brain'} · "
        f"{anchor.get('main_job') or 'route Worker'} · "
        "disk truth only · RED stays RED · no sweet lies"
    )


def inject_slice() -> dict:
    ssot = load_settings()
    intent = ssot.get("intent_first") or {}
    truth = ssot.get("truth_hard_concrete") or {}
    report_lang = ssot.get("agent_report_language") or {}
    mp_trig = ssot.get("main_problem_trigger") or {}
    nt_trig = ssot.get("next_task_trigger") or {}
    tp_pri = ssot.get("task_plan_priority") or {}
    comp_loop = ssot.get("cloud_comprehension_pipeline_loop") or {}
    out = {
        "schema": "agent-behavior-inject-v1",
        "one_law": ssot.get("one_law"),
        "before_act": intent.get("before_act") or [],
        "required": (intent.get("required") or []) + (truth.get("required") or []),
        "forbidden_behaviors": (intent.get("forbidden") or []) + (truth.get("forbidden") or []),
        "read_order": intent.get("read_order") or [],
        "truth_hard_concrete": truth,
        "role_anchors": ssot.get("role_anchors") or {},
        "agent_report_language": {
            "one_law": report_lang.get("one_law"),
            "comprehension_before_speak": report_lang.get("comprehension_before_speak") or [],
            "human_story_rules": report_lang.get("human_story_rules") or [],
            "forbidden_patterns": report_lang.get("forbidden_patterns") or [],
            "calibration": report_lang.get("calibration_models") or [],
        },
        "main_problem_trigger": {
            "active": bool(mp_trig.get("active")),
            "one_law": mp_trig.get("one_law"),
            "mode": mp_trig.get("mode"),
            "trigger_phrases": mp_trig.get("trigger_phrases") or [],
            "ssot": mp_trig.get("ssot"),
        },
        "next_task_trigger": {
            "active": bool(nt_trig.get("active")),
            "always_apply": bool(nt_trig.get("always_apply", True)),
            "one_law": nt_trig.get("one_law"),
            "mode": nt_trig.get("mode"),
            "trigger_phrases": nt_trig.get("trigger_phrases") or [],
            "task_plan_topic_patterns": nt_trig.get("task_plan_topic_patterns") or [],
            "required_question": "What is the real-world output supposed to be?",
            "reply_sections": [
                "What is this task?",
                "Benefit and priority",
                "Real-world output",
                "Usefulness verdict",
                "Proceed?",
            ],
            "command_refresh": "python3 scripts/next_task_trigger_v1.py --refresh --json",
            "ssot": nt_trig.get("ssot"),
        },
        "task_plan_priority": {
            "active": bool(tp_pri.get("active", True)),
            "one_law": tp_pri.get("one_law"),
            "priority_stack": tp_pri.get("priority_stack") or [],
            "command_refresh": "python3 scripts/task_plan_priority_v1.py --refresh --json",
            "ssot": tp_pri.get("ssot"),
        },
        "cloud_comprehension_pipeline_loop": {
            "active": bool(comp_loop.get("active")),
            "one_law": comp_loop.get("one_law"),
            "circles": comp_loop.get("circles") or [],
            "ssot": comp_loop.get("ssot"),
        },
        "brain_truth_line": brain_truth_line(ssot=ssot),
        "behavior_line": behavior_line(ssot=ssot),
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    return out


def hub_slice() -> dict:
    row = sync_receipt(write=True)
    inj = inject_slice()
    return {
        "schema": "worker-hub-agent-behavior-v1",
        "ok": bool(row.get("ok")),
        "behavior_line": row.get("behavior_line"),
        "one_law": row.get("one_law"),
        "case_count": row.get("case_count"),
        "required": inj.get("required") or [],
        "hub_api": "GET /api/worker-hub/v1 · inject founder_intent_first_detail",
    }


def sync_receipt(*, write: bool = True) -> dict:
    ssot = load_settings()
    mirror = _read(MIRROR)
    detail = (mirror.get("inject") or {}).get("founder_intent_first_detail") or {}
    mirror_ok = bool(detail.get("one_law"))
    row = {
        "schema": "agent-behavior-settings-receipt-v1",
        "at": _now(),
        "ok": bool(ssot.get("one_law")) and CURSOR_RULE.is_file(),
        "one_law": ssot.get("one_law"),
        "applies_to": ssot.get("applies_to"),
        "case_count": len(ssot.get("cases") or []),
        "behavior_line": behavior_line(ssot=ssot),
        "mirror_inject_ok": mirror_ok,
        "cursor_rule": CURSOR_RULE.is_file(),
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def validate(*, check_mirror: bool = True) -> dict:
    ssot = load_settings()
    ssot_ok = (
        ssot.get("schema") == "agent-behavior-settings-v1"
        and bool(ssot.get("one_law"))
        and bool((ssot.get("intent_first") or {}).get("required"))
        and bool((ssot.get("intent_first") or {}).get("forbidden"))
        and bool((ssot.get("truth_hard_concrete") or {}).get("required"))
        and bool((ssot.get("role_anchors") or {}).get("brain"))
    )
    mirror = _read(MIRROR)
    inject = mirror.get("inject") or {}
    mirror_ok = bool(inject.get("founder_intent_first")) and bool(
        (inject.get("founder_intent_first_detail") or {}).get("one_law")
    )
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")
    surfaces_ok = bool(surfaces.get("behavior_line"))
    issues: list[str] = []
    if not ssot_ok:
        issues.append("ssot_incomplete")
    if not CURSOR_RULE.is_file():
        issues.append("cursor_rule_missing")
    if check_mirror and not mirror_ok:
        issues.append("memory_mirror_inject_missing")
    if check_mirror and not surfaces_ok:
        issues.append("live_surfaces_behavior_line_missing")
    ok = ssot_ok and CURSOR_RULE.is_file() and (not check_mirror or (mirror_ok and surfaces_ok))
    return {
        "ok": ok,
        "ssot_ok": ssot_ok,
        "cursor_rule": CURSOR_RULE.is_file(),
        "mirror_inject_ok": mirror_ok,
        "surfaces_ok": surfaces_ok,
        "one_law": ssot.get("one_law"),
        "behavior_line": behavior_line(ssot=ssot),
        "issues": issues,
    }


def run_wire(*, write: bool = True) -> dict:
    """Refresh mirror inject + receipt + live surfaces behavior_line."""
    try:
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        from agent_memory_mirror_v1 import sync_mirror  # noqa: WPS433

        sync_mirror()
    except Exception as exc:
        return {"ok": False, "error": f"mirror_sync:{exc}"}
    row = sync_receipt(write=write)
    surfaces_path = SINA / "agent-live-surfaces-v1.json"
    surfaces = _read(surfaces_path)
    if surfaces and row.get("behavior_line"):
        surfaces["behavior_line"] = row["behavior_line"]
        surfaces["agent_behavior"] = {
            "ok": row.get("ok"),
            "receipt": str(RECEIPT),
            "one_law": row.get("one_law"),
        }
        surfaces_path.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    try:
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        from worker_live_context_v1 import build_worker_live_context  # noqa: WPS433
        from brain_live_context_v1 import build_brain_live_context  # noqa: WPS433

        wrow = build_worker_live_context()
        brow = build_brain_live_context()
        SINA.mkdir(parents=True, exist_ok=True)
        (SINA / "worker-live-context-v1.json").write_text(json.dumps(wrow, indent=2) + "\n", encoding="utf-8")
        (SINA / "brain-live-context-v1.json").write_text(json.dumps(brow, indent=2) + "\n", encoding="utf-8")
        contexts_ok = "behavior:" in str(wrow.get("text_block") or "") and "behavior:" in str(
            brow.get("text_block") or ""
        )
    except Exception:
        contexts_ok = False
    val = validate(check_mirror=True)
    ok = bool(row.get("ok")) and bool(val.get("ok")) and contexts_ok
    return {
        "ok": ok,
        "receipt": row,
        "validate": val,
        "contexts_ok": contexts_ok,
        "behavior_line": row.get("behavior_line"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Agent behavior settings")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--wire", action="store_true")
    ap.add_argument("--no-mirror-check", action="store_true")
    args = ap.parse_args()
    if args.wire:
        row = run_wire(write=True)
    elif args.hub_slice:
        row = hub_slice()
    elif args.inject:
        row = inject_slice()
    elif args.validate:
        row = validate(check_mirror=not args.no_mirror_check)
    else:
        row = sync_receipt(write=True)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("behavior_line") or row.get("inject_line") or row.get("one_law") or row.get("ok"))
    ok = bool(row.get("ok", True)) if args.inject else bool(row.get("ok", True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
