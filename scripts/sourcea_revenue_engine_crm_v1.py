#!/usr/bin/env python3
"""SourceA Revenue Engine v1 — lightweight CRM pipeline on disk."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "sourcea-revenue-engine-crm-pipeline-v1.json"
SINA = Path.home() / ".sina"
RUNTIME = SINA / "sourcea-revenue-engine-crm-v1.json"
VALID_STAGES = {
    "lead",
    "outreach_sent",
    "conversation",
    "meeting_booked",
    "proposal_sent",
    "won",
    "lost",
    "nurture",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_ssot() -> dict[str, Any]:
    return json.loads(SSOT.read_text(encoding="utf-8"))


def _load_runtime() -> dict[str, Any]:
    if not RUNTIME.is_file():
        return {}
    return json.loads(RUNTIME.read_text(encoding="utf-8"))


def _write_runtime(row: dict[str, Any]) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    RUNTIME.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _find_prospect(row: dict[str, Any], prospect_id: str) -> dict[str, Any] | None:
    for p in row.get("prospects") or []:
        if p.get("id") == prospect_id:
            return p
    return None


def cmd_init(*, force: bool) -> dict[str, Any]:
    if RUNTIME.is_file() and not force:
        return {"ok": False, "error": "runtime_exists", "path": str(RUNTIME), "hint": "use --force to reset"}
    ssot = _load_ssot()
    row = {
        "schema": ssot["schema"],
        "version": ssot["version"],
        "initialized_at": _now(),
        "ssot_path": str(SSOT),
        "templates_doc": ssot.get("templates_doc"),
        "prospects": [],
        "activity_log": [],
    }
    _write_runtime(row)
    return {"ok": True, "path": str(RUNTIME), "prospects": 0}


def cmd_add(args: argparse.Namespace) -> dict[str, Any]:
    row = _load_runtime()
    if not row:
        init_row = cmd_init(force=False)
        if not init_row.get("ok"):
            cmd_init(force=True)
        row = _load_runtime()
    prospect_id = args.id.strip()
    if _find_prospect(row, prospect_id):
        return {"ok": False, "error": "duplicate_id", "id": prospect_id}
    prospect: dict[str, Any] = {
        "id": prospect_id,
        "name": args.name.strip(),
        "segment": args.segment,
        "stage": "lead",
        "channel": args.channel,
        "created_at": _now(),
        "last_touch_at": _now(),
    }
    if args.company:
        prospect["company"] = args.company.strip()
    if args.email:
        prospect["email"] = args.email.strip()
    if args.deal:
        prospect["deal_value_cad"] = int(args.deal)
    if args.sku:
        prospect["offer_sku"] = args.sku
    if args.warmth:
        prospect["warmth"] = args.warmth
    if args.next_action:
        prospect["next_action"] = args.next_action
    row.setdefault("prospects", []).append(prospect)
    row.setdefault("activity_log", []).append(
        {
            "at": _now(),
            "prospect_id": prospect_id,
            "action": "add",
            "stage": "lead",
            "note": args.note or "prospect added",
        }
    )
    _write_runtime(row)
    return {"ok": True, "prospect": prospect}


def cmd_touch(args: argparse.Namespace) -> dict[str, Any]:
    row = _load_runtime()
    if not row:
        return {"ok": False, "error": "not_initialized", "hint": "run: sourcea_revenue_engine_crm_v1.py init"}
    prospect = _find_prospect(row, args.id.strip())
    if not prospect:
        return {"ok": False, "error": "not_found", "id": args.id}
    stage = args.stage
    if stage not in VALID_STAGES:
        return {"ok": False, "error": "invalid_stage", "stage": stage, "valid": sorted(VALID_STAGES)}
    prev = prospect.get("stage")
    prospect["stage"] = stage
    prospect["last_touch_at"] = _now()
    if args.template:
        prospect["template_id"] = args.template
    if args.deal is not None:
        prospect["deal_value_cad"] = int(args.deal)
    if args.next_action:
        prospect["next_action"] = args.next_action
    for flag in ("case_study_sent", "offer_page_sent", "pureflow_link_sent"):
        if getattr(args, flag, False):
            prospect[flag] = True
    row.setdefault("activity_log", []).append(
        {
            "at": _now(),
            "prospect_id": args.id,
            "action": "touch",
            "from_stage": prev,
            "to_stage": stage,
            "template_id": args.template,
            "note": args.note or "",
        }
    )
    _write_runtime(row)
    return {"ok": True, "prospect": prospect, "from_stage": prev, "to_stage": stage}


def cmd_list(args: argparse.Namespace) -> dict[str, Any]:
    row = _load_runtime()
    prospects = list(row.get("prospects") or [])
    if args.stage:
        prospects = [p for p in prospects if p.get("stage") == args.stage]
    return {"ok": True, "count": len(prospects), "prospects": prospects, "path": str(RUNTIME)}


def cmd_summary(_: argparse.Namespace) -> dict[str, Any]:
    row = _load_runtime()
    prospects = row.get("prospects") or []
    by_stage: dict[str, int] = {}
    pipeline_cad = 0
    won_cad = 0
    for p in prospects:
        st = p.get("stage") or "lead"
        by_stage[st] = by_stage.get(st, 0) + 1
        val = int(p.get("deal_value_cad") or 0)
        if st == "won":
            won_cad += val
        elif st in {"proposal_sent", "meeting_booked", "conversation"}:
            pipeline_cad += val
    ssot = _load_ssot()
    target = (ssot.get("metrics") or {}).get("30_day_target") or {}
    return {
        "ok": True,
        "path": str(RUNTIME),
        "prospect_count": len(prospects),
        "by_stage": by_stage,
        "won_cad": won_cad,
        "pipeline_cad": pipeline_cad,
        "30_day_target": target,
        "funnel_ready": by_stage.get("outreach_sent", 0) >= 1,
    }


def cmd_seed_examples(_: argparse.Namespace) -> dict[str, Any]:
    row = _load_runtime()
    if not row:
        cmd_init(force=True)
        row = _load_runtime()
    ssot = _load_ssot()
    added = 0
    existing = {p.get("id") for p in row.get("prospects") or []}
    for ex in ssot.get("starter_prospects_example") or []:
        if ex.get("id") in existing:
            continue
        row.setdefault("prospects", []).append(dict(ex))
        row.setdefault("activity_log", []).append(
            {
                "at": _now(),
                "prospect_id": ex.get("id"),
                "action": "seed",
                "stage": ex.get("stage"),
                "note": "starter example from SSOT",
            }
        )
        added += 1
    _write_runtime(row)
    return {"ok": True, "added": added, "path": str(RUNTIME)}


def main() -> int:
    parser = argparse.ArgumentParser(description="SourceA Revenue Engine CRM v1")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize runtime CRM file")
    p_init.add_argument("--force", action="store_true")
    p_init.add_argument("--json", action="store_true", help="JSON output")

    p_add = sub.add_parser("add", help="Add prospect")
    p_add.add_argument("--json", action="store_true", help="JSON output")
    p_add.add_argument("--id", required=True)
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--segment", required=True)
    p_add.add_argument("--channel", required=True)
    p_add.add_argument("--company", default="")
    p_add.add_argument("--email", default="")
    p_add.add_argument("--deal", type=int, default=0)
    p_add.add_argument("--sku", default="SKU-48H-001")
    p_add.add_argument("--warmth", choices=["warm", "cold"], default="warm")
    p_add.add_argument("--next-action", default="")
    p_add.add_argument("--note", default="")

    p_touch = sub.add_parser("touch", help="Update stage / log outreach")
    p_touch.add_argument("--json", action="store_true", help="JSON output")
    p_touch.add_argument("--id", required=True)
    p_touch.add_argument("--stage", required=True)
    p_touch.add_argument("--template", default="")
    p_touch.add_argument("--deal", type=int)
    p_touch.add_argument("--next-action", default="")
    p_touch.add_argument("--note", default="")
    p_touch.add_argument("--case-study-sent", action="store_true")
    p_touch.add_argument("--offer-page-sent", action="store_true")
    p_touch.add_argument("--pureflow-link-sent", action="store_true")

    p_list = sub.add_parser("list", help="List prospects")
    p_list.add_argument("--json", action="store_true", help="JSON output")
    p_list.add_argument("--stage", default="")

    p_summary = sub.add_parser("summary", help="Funnel summary")
    p_summary.add_argument("--json", action="store_true", help="JSON output")

    p_seed = sub.add_parser("seed-examples", help="Add SSOT starter rows (bracket placeholders)")
    p_seed.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()
    handlers = {
        "init": lambda a: cmd_init(force=a.force),
        "add": cmd_add,
        "touch": cmd_touch,
        "list": cmd_list,
        "summary": cmd_summary,
        "seed-examples": cmd_seed_examples,
    }
    result = handlers[args.cmd](args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
