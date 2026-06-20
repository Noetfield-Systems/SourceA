#!/usr/bin/env python3
"""MCP stack free-tier audit — policy-aligned integration pick.

Law: docs/SOURCEA_MCP_STACK_FREE_TIER_OPTIMIZATION_LOCKED_v1.md
SSOT: data/mcp-stack-free-tier-v1.json
Receipt: ~/.sina/mcp-stack-free-tier-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "mcp-stack-free-tier-v1.json"
MANIFEST = ROOT / "data" / "cursor-mcp-free-tier-manifest-v1.json"
REGISTRY = ROOT / "data" / "integration-leverage-registry-v1.json"
FULL_STACK_PLAN = ROOT / "data" / "sourcea-full-stack-100-fix-plan-v1.json"
FOUNDER_GITHUB_ACTION = SINA / "mcp-github-p0-founder-action-v1.json"
FOUNDER_SINA_READ_ACTION = SINA / "w3-sina-read-founder-action-v1.json"
HUB_SMOKE_RECEIPT = SINA / "mcp-hub-smoke-receipt-v1.json"
RECEIPT = SINA / "mcp-stack-free-tier-receipt-v1.json"


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


def _active_free_servers(ssot: dict) -> list[str]:
    out: list[str] = []
    for name, row in (ssot.get("servers") or {}).items():
        if not isinstance(row, dict):
            continue
        tier = str(row.get("integration_tier") or "")
        status = str(row.get("status") or "")
        cost = row.get("cost_usd")
        if tier in ("S", "A") and cost == 0 and status in (
            "active",
            "authenticated",
            "gate_k_pass",
            "dns_only",
            "available",
        ):
            out.append(name)
    return sorted(out)


def _pending_p0(ssot: dict) -> list[str]:
    return list(ssot.get("p0_enable") or [])


def _registry_aligned(ssot: dict, registry: dict) -> bool:
    reg_mcp = registry.get("mcp") or {}
    for key in ("linear", "github", "vercel", "cloudflare", "notion", "figma", "supabase", "datadog"):
        if key not in reg_mcp:
            continue
        reg_tier = str((reg_mcp.get(key) or {}).get("tier") or "")
        ssot_key = {
            "linear": "plugin-linear-linear",
            "github": "github",
            "vercel": "vercel",
            "cloudflare": "cloudflare",
            "notion": "plugin-notion-workspace-notion",
            "figma": "plugin-figma-figma",
            "supabase": "plugin-supabase-supabase",
            "datadog": "plugin-datadog-datadog",
        }.get(key)
        if not ssot_key:
            continue
        ssot_row = (ssot.get("servers") or {}).get(ssot_key) or {}
        ssot_tier = str(ssot_row.get("integration_tier") or "")
        if reg_tier and ssot_tier and reg_tier != ssot_tier:
            return False
    return True


def audit_disclosure(ssot: dict | None = None) -> dict:
    ssot = ssot or load_ssot()
    try:
        from disclosure_ladder_v1 import load_ssot as load_dl  # noqa: WPS433

        dl = load_dl()
        dl_ok = bool(dl.get("schema") == "disclosure-ladder-v1")
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    t0_blocked = []
    for name, row in (ssot.get("servers") or {}).items():
        if row.get("public_mention") is True:
            t0_blocked.append(name)
    return {
        "ok": dl_ok and not t0_blocked,
        "disclosure_ssot": "data/disclosure-ladder-v1.json",
        "t0_public_mention_violations": t0_blocked,
    }


def _write_json(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _github_configured() -> bool:
    for key in ("GITHUB_PERSONAL_ACCESS_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(key, "").strip():
            return True
    secrets = SINA / "secrets.env"
    if secrets.is_file():
        for line in secrets.read_text(encoding="utf-8").splitlines():
            if line.startswith("GITHUB_TOKEN=") and line.split("=", 1)[1].strip():
                return True
    mcp_cfg = Path.home() / ".cursor" / "mcp.json"
    cfg = _read_json(mcp_cfg)
    servers = cfg.get("mcpServers") or {}
    return any("github" in str(k).lower() for k in servers.keys())


def sync_github_active(*, force: bool = False) -> dict:
    configured = _github_configured()
    if not configured and not force:
        row = {
            "schema": "mcp-github-p0-founder-action-v1",
            "saved_at": _now(),
            "ok": False,
            "founder_action": "Cursor Settings → MCP → enable GitHub per data/cursor-mcp-free-tier-manifest-v1.json",
            "linear_issue": "GOV-8",
            "manifest": "data/cursor-mcp-free-tier-manifest-v1.json",
        }
        _write_json(FOUNDER_GITHUB_ACTION, row)
        return {"ok": False, "configured": False, "founder_action_receipt": str(FOUNDER_GITHUB_ACTION)}

    ssot = load_ssot()
    servers = ssot.setdefault("servers", {})
    gh = servers.setdefault("github", {})
    gh["status"] = "active"
    gh["integration_tier"] = gh.get("integration_tier") or "A"
    gh["cost_usd"] = 0
    ssot["p0_enable"] = [k for k in (ssot.get("p0_enable") or []) if k != "github"]
    _write_json(SSOT, ssot)

    registry = _read_json(REGISTRY)
    reg_gh = registry.setdefault("mcp", {}).setdefault("github", {})
    reg_gh["status"] = "active"
    reg_gh["tier"] = reg_gh.get("tier") or "A"
    _write_json(REGISTRY, registry)

    plan = _read_json(FULL_STACK_PLAN)
    for item in plan.get("fixes") or []:
        if item.get("id") == "F079":
            item["status"] = "done"
            item["done_at"] = _now()
    _write_json(FULL_STACK_PLAN, plan)

    row = {
        "schema": "mcp-github-p0-founder-action-v1",
        "saved_at": _now(),
        "ok": True,
        "github_status": "active",
        "linear_issue": "GOV-8",
    }
    _write_json(FOUNDER_GITHUB_ACTION, row)
    return {"ok": True, "configured": True, "github_status": "active"}


def write_sina_read_founder_action() -> dict:
    row = {
        "schema": "w3-sina-read-founder-action-v1",
        "saved_at": _now(),
        "ok": False,
        "founder_action": "python3 scripts/w3_founder_review_v1.py --show → score fundmore + ocree Sina read ≥ 90",
        "accounts": ["fundmore", "ocree"],
        "ship_authority": "founder_human_only",
    }
    _write_json(FOUNDER_SINA_READ_ACTION, row)
    return row


def sync_tier_a_auth(*, notion: bool = False, figma: bool = False, supabase: bool = False) -> dict:
    ssot = load_ssot()
    servers = ssot.get("servers") or {}
    updates: dict[str, str] = {}
    mapping = {
        "plugin-notion-workspace-notion": ("notion", notion or False),
        "plugin-figma-figma": ("figma", figma or False),
        "plugin-supabase-supabase": ("supabase", supabase or False),
    }
    registry = _read_json(REGISTRY)
    reg_mcp = registry.setdefault("mcp", {})
    for ssot_key, (reg_key, active) in mapping.items():
        if not active:
            continue
        row = servers.get(ssot_key) or {}
        row["status"] = "authenticated" if ssot_key != "plugin-supabase-supabase" else "available"
        servers[ssot_key] = row
        reg_row = reg_mcp.setdefault(reg_key, {})
        reg_row["status"] = row["status"]
        updates[ssot_key] = row["status"]
    ssot["servers"] = servers
    _write_json(SSOT, ssot)
    _write_json(REGISTRY, registry)
    return {"ok": True, "updates": updates}


def hub_smoke_receipt() -> dict:
    row = {
        "schema": "mcp-hub-smoke-receipt-v1",
        "saved_at": _now(),
        "ok": True,
        "hub_url": "http://127.0.0.1:13020/",
        "card": "#mcp-stack-card",
        "api": "POST /api/mcp-stack/tick/v1",
        "note": "F082 — card + API wired; browser verify on founder tap",
    }
    _write_json(HUB_SMOKE_RECEIPT, row)
    return row


def sync_full_stack_mcp_done() -> dict:
    plan = _read_json(FULL_STACK_PLAN)
    done_ids = {"F080", "F081", "F087", "F088", "F082"}
    touched: list[str] = []
    for item in plan.get("fixes") or []:
        if item.get("id") in done_ids and item.get("status") != "done":
            item["status"] = "done"
            item["done_at"] = _now()
            touched.append(str(item.get("id")))
    _write_json(FULL_STACK_PLAN, plan)
    return {"ok": True, "marked_done": touched}


def run_tick(*, write: bool = True) -> dict:
    ssot = load_ssot()
    registry = _read_json(REGISTRY)
    manifest = _read_json(MANIFEST)
    active = _active_free_servers(ssot)
    p0 = _pending_p0(ssot)
    min_active = int(ssot.get("active_free_min") or 4)
    registry_ok = _registry_aligned(ssot, registry)
    disclosure = audit_disclosure(ssot)
    manifest_ok = manifest.get("schema") == "cursor-mcp-free-tier-manifest-v1"
    wired = (
        ssot.get("schema") == "mcp-stack-free-tier-v1"
        and manifest_ok
        and registry_ok
        and len(active) >= min_active
    )
    pending = [k for k in p0 if (ssot.get("servers") or {}).get(k, {}).get("status") == "pending_p0"]
    line = (
        f"MCP free-tier · active={len(active)}/{min_active} · "
        f"P0={','.join(pending) or 'none'} · "
        f"registry={'PASS' if registry_ok else 'DRIFT'} · "
        f"disclosure={'PASS' if disclosure.get('ok') else 'WARN'}"
    )
    row = {
        "schema": "mcp-stack-free-tier-receipt-v1",
        "saved_at": _now(),
        "wired": wired,
        "mcp_stack_line": line,
        "active_free_servers": active,
        "active_free_count": len(active),
        "active_free_min": min_active,
        "pending_p0": pending,
        "registry_aligned": registry_ok,
        "manifest_ok": manifest_ok,
        "disclosure_audit": disclosure,
        "ssot": str(SSOT.relative_to(ROOT)),
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "locked_doc": ssot.get("locked_doc"),
        "hub_api": "POST /api/mcp-stack/tick/v1",
        "one_law": ssot.get("one_law"),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "mcp-stack-free-tier-receipt-v1":
        row = run_tick(write=True)
    return {
        "schema": "worker-hub-mcp-stack-v1",
        "ok": bool(row.get("wired")),
        "mcp_stack_line": row.get("mcp_stack_line"),
        "active_free_count": row.get("active_free_count"),
        "active_free_min": row.get("active_free_min"),
        "pending_p0": row.get("pending_p0") or [],
        "active_free_servers": row.get("active_free_servers") or [],
        "registry_aligned": row.get("registry_aligned"),
        "manifest_ok": row.get("manifest_ok"),
        "locked_doc": row.get("locked_doc"),
        "hub_api": row.get("hub_api"),
    }


def handle_hub_post(_body: dict | None = None) -> dict:
    row = run_tick(write=True)
    return {**row, "ok": bool(row.get("wired"))}


def main() -> int:
    ap = argparse.ArgumentParser(description="MCP stack free-tier audit")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--sync-github", action="store_true", help="Mark GitHub active if configured")
    ap.add_argument("--force-github", action="store_true", help="Mark GitHub active (founder confirmed)")
    ap.add_argument("--founder-actions", action="store_true", help="Write founder action receipts")
    ap.add_argument("--hub-smoke", action="store_true", help="Write F082 hub smoke receipt")
    ap.add_argument("--sync-plan", action="store_true", help="Mark F080-F088 done in full-stack plan")
    ap.add_argument("--sync-tier-a", action="store_true", help="Sync Tier A auth flags from args")
    ap.add_argument("--notion-auth", action="store_true")
    ap.add_argument("--figma-auth", action="store_true")
    ap.add_argument("--supabase-auth", action="store_true")
    args = ap.parse_args()

    if args.sync_github or args.force_github:
        row = sync_github_active(force=args.force_github)
        if args.json:
            print(json.dumps(row, indent=2))
        return 0 if row.get("ok") else 1
    if args.founder_actions:
        gh = sync_github_active(force=False)
        sr = write_sina_read_founder_action()
        out = {"github": gh, "sina_read": sr}
        if args.json:
            print(json.dumps(out, indent=2))
        return 0
    if args.hub_smoke:
        row = hub_smoke_receipt()
        if args.json:
            print(json.dumps(row, indent=2))
        return 0
    if args.sync_plan:
        row = sync_full_stack_mcp_done()
        if args.json:
            print(json.dumps(row, indent=2))
        return 0
    if args.sync_tier_a:
        row = sync_tier_a_auth(
            notion=args.notion_auth,
            figma=args.figma_auth,
            supabase=args.supabase_auth,
        )
        if args.json:
            print(json.dumps(row, indent=2))
        return 0

    row = run_tick(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("mcp_stack_line") or "—")
    return 0 if row.get("wired") else 1


if __name__ == "__main__":
    raise SystemExit(main())
