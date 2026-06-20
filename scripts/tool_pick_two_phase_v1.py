#!/usr/bin/env python3
"""Two-phase tool pick — free tier exhaust · affordable AI founder approval only.

Law: data/tool-pick-two-phase-v1.json
Phase 1: auto-wire all good $0 tools
Phase 2: pending_founder_approval — never wire without approval receipt
Receipt: ~/.sina/tool-pick-two-phase-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "tool-pick-two-phase-v1.json"
MCP_SSOT = ROOT / "data" / "mcp-stack-free-tier-v1.json"
RECEIPT = SINA / "tool-pick-two-phase-receipt-v1.json"
APPROVAL = SINA / "tool-pick-phase2-founder-approval-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_ssot() -> dict:
    return _read_json(SSOT)


def _write_json(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _phase1_status(tool: dict, mcp_ssot: dict) -> str:
    wire = str(tool.get("wire") or "")
    tid = str(tool.get("id") or "")
    if tid == "github_mcp":
        gh = (mcp_ssot.get("servers") or {}).get("github") or {}
        return str(gh.get("status") or wire)
    mapping = {
        "cursor-ide-browser": "cursor-ide-browser",
        "plugin-linear-linear": "plugin-linear-linear",
        "vercel_hobby": "vercel",
        "cloudflare_dns": "cloudflare",
        "notion_mcp": "plugin-notion-workspace-notion",
        "figma_mcp": "plugin-figma-figma",
        "supabase_free": "plugin-supabase-supabase",
    }
    key = mapping.get(tid)
    if key:
        row = (mcp_ssot.get("servers") or {}).get(key) or {}
        return str(row.get("status") or wire)
    if wire in ("active", "authenticated", "gate_k_pass", "dns_only", "available", "tier0_priority_1"):
        return "active"
    return wire or "unknown"


def _phase1_active(status: str) -> bool:
    return status in (
        "active",
        "authenticated",
        "gate_k_pass",
        "dns_only",
        "available",
        "tier0_priority_1",
        "tier0_priority_2",
        "tier0_priority_3",
        "tier0_priority_4",
        "tier0_priority_6",
        "tier0_last",
    )


def _approved_phase2() -> dict[str, dict]:
    row = _read_json(APPROVAL)
    out: dict[str, dict] = {}
    for item in row.get("approved") or []:
        if isinstance(item, dict) and item.get("id"):
            out[str(item["id"])] = item
    return out


def run_tick(*, write: bool = True) -> dict:
    ssot = load_ssot()
    mcp = _read_json(MCP_SSOT)
    p1 = ssot.get("phase_1_free") or {}
    p2 = ssot.get("phase_2_affordable_ai") or {}
    p1_tools = p1.get("tools") or []
    p2_tools = p2.get("tools") or []
    approved = _approved_phase2()

    p1_rows: list[dict] = []
    p1_active = 0
    for tool in p1_tools:
        if not isinstance(tool, dict):
            continue
        status = _phase1_status(tool, mcp)
        active = _phase1_active(status)
        if active:
            p1_active += 1
        p1_rows.append({"id": tool.get("id"), "status": status, "active": active})

    p2_pending: list[str] = []
    p2_approved: list[str] = []
    p2_wired: list[str] = []
    for tool in p2_tools:
        if not isinstance(tool, dict):
            continue
        tid = str(tool.get("id") or "")
        base = str(tool.get("status") or "pending_founder_approval")
        if tid in approved:
            appr = approved[tid]
            if appr.get("wired"):
                p2_wired.append(tid)
            else:
                p2_approved.append(tid)
        elif base == "pending_founder_approval":
            p2_pending.append(tid)

    p1_total = len(p1_tools) or 1
    exhaust_pct = int(round(100 * p1_active / p1_total))
    phase_1_ok = exhaust_pct >= 70
    line = (
        f"Tool pick · P1 free {p1_active}/{p1_total} ({exhaust_pct}%) · "
        f"P2 pending={len(p2_pending)} · approved={len(p2_approved)} · "
        f"wire=founder_only"
    )
    row = {
        "schema": "tool-pick-two-phase-receipt-v1",
        "saved_at": _now(),
        "ok": ssot.get("schema") == "tool-pick-two-phase-v1",
        "wired": phase_1_ok and p2.get("auto_wire") is False,
        "tool_pick_line": line,
        "one_law": ssot.get("one_law"),
        "phase_1": {
            "active_count": p1_active,
            "total": p1_total,
            "exhaust_pct": exhaust_pct,
            "auto_wire": p1.get("auto_wire"),
            "tools": p1_rows,
        },
        "phase_2": {
            "founder_approval_required": p2.get("founder_approval_required"),
            "auto_wire": p2.get("auto_wire"),
            "pending_founder_approval": p2_pending,
            "approved_not_wired": p2_approved,
            "wired": p2_wired,
            "approval_verb": p2.get("approval_verb"),
        },
        "ssot": str(SSOT.relative_to(ROOT)),
        "approval_receipt": str(APPROVAL),
        "hub_api": "POST /api/tool-pick/tick/v1",
    }
    if write:
        _write_json(RECEIPT, row)
        if not APPROVAL.is_file():
            _write_json(
                APPROVAL,
                {
                    "schema": "tool-pick-phase2-founder-approval-v1",
                    "saved_at": _now(),
                    "approved": [],
                    "note": "Add entries: {\"id\":\"runway_hero\",\"approved_at\":\"...\",\"wired\":false}",
                },
            )
    return row


def approve_tool(tool_id: str, *, wired: bool = False) -> dict:
    ssot = load_ssot()
    valid = {str(t.get("id")) for t in (ssot.get("phase_2_affordable_ai") or {}).get("tools") or []}
    if tool_id not in valid:
        return {"ok": False, "error": f"unknown phase 2 tool: {tool_id}"}
    row = _read_json(APPROVAL)
    if row.get("schema") != "tool-pick-phase2-founder-approval-v1":
        row = {"schema": "tool-pick-phase2-founder-approval-v1", "approved": []}
    approved = [a for a in (row.get("approved") or []) if a.get("id") != tool_id]
    approved.append({"id": tool_id, "approved_at": _now(), "wired": wired})
    row["approved"] = approved
    row["saved_at"] = _now()
    _write_json(APPROVAL, row)
    return {"ok": True, "tool_id": tool_id, "wired": wired}


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "tool-pick-two-phase-receipt-v1":
        row = run_tick(write=True)
    p2 = row.get("phase_2") or {}
    return {
        "schema": "worker-hub-tool-pick-v1",
        "ok": bool(row.get("wired")),
        "tool_pick_line": row.get("tool_pick_line"),
        "phase_1_exhaust_pct": (row.get("phase_1") or {}).get("exhaust_pct"),
        "pending_founder_approval": p2.get("pending_founder_approval") or [],
        "approval_verb": p2.get("approval_verb"),
        "founder_approval_required": p2.get("founder_approval_required"),
        "hub_api": row.get("hub_api"),
    }


def handle_hub_post(body: dict | None = None) -> dict:
    body = body or {}
    if body.get("approve_tool_id"):
        approve_tool(str(body["approve_tool_id"]), wired=bool(body.get("wired")))
    row = run_tick(write=True)
    return {**row, "ok": bool(row.get("wired"))}


def main() -> int:
    ap = argparse.ArgumentParser(description="Two-phase tool pick audit")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--approve", metavar="TOOL_ID", help="Founder approve phase 2 tool (no auto-wire unless --wired)")
    ap.add_argument("--wired", action="store_true", help="Mark approved tool as wired (founder only)")
    args = ap.parse_args()
    if args.approve:
        row = approve_tool(args.approve, wired=args.wired)
        if args.json:
            print(json.dumps(row, indent=2))
        run_tick(write=not args.no_write)
        return 0 if row.get("ok") else 1
    row = run_tick(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("tool_pick_line") or "—")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
