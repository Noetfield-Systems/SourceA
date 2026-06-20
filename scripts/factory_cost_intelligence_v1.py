#!/usr/bin/env python3
"""Factory cost intelligence loop + 100 evidence-backed factory registry.

SSOT: data/factory-cost-intelligence-loop-v1.json
Receipt: ~/.sina/factory-cost-intelligence-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "factory-cost-intelligence-loop-v1.json"
RECEIPT = SINA / "factory-cost-intelligence-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_ssot() -> dict:
    return _read(SSOT)


def cost_intelligence_line(*, ssot: dict | None = None) -> str:
    row = ssot or load_ssot()
    n = int(row.get("registry_count") or len(row.get("factories") or []))
    corpus = row.get("evidence_corpus") or {}
    gln = int(corpus.get("wef_gln_total_sites") or 0)
    layers = len((row.get("cost_intelligence_loop") or {}).get("layers") or [])
    return f"cost-intel · loop={layers} · registry={n} · wef={gln} · auto-prompt=planner→inbox"


def inject_slice() -> dict:
    ssot = load_ssot()
    loop = ssot.get("cost_intelligence_loop") or {}
    auto = ssot.get("auto_prompting") or {}
    return {
        "schema": "factory-cost-intelligence-inject-v1",
        "one_law": ssot.get("one_law"),
        "layers": loop.get("layers") or [],
        "auto_prompting": {
            "planner_executor_split": auto.get("planner_executor_split"),
            "sourcea_mapping": auto.get("sourcea_mapping") or {},
        },
        "registry_count": ssot.get("registry_count"),
        "evidence_corpus": ssot.get("evidence_corpus") or {},
        "cost_intelligence_line": cost_intelligence_line(ssot=ssot),
        "ssot": str(SSOT.relative_to(ROOT)),
    }


def hub_slice() -> dict:
    row = sync_receipt(write=True)
    return {
        "schema": "worker-hub-factory-cost-intelligence-v1",
        "ok": bool(row.get("ok")),
        "cost_intelligence_line": row.get("cost_intelligence_line"),
        "registry_count": row.get("registry_count"),
        "wef_gln_total": row.get("wef_gln_total"),
        "one_law": row.get("one_law"),
        "hub_api": "GET /api/worker-hub/v1 · slice factory_cost_intelligence",
    }


def sync_receipt(*, write: bool = True) -> dict:
    ssot = load_ssot()
    factories = ssot.get("factories") or []
    corpus = ssot.get("evidence_corpus") or {}
    row = {
        "schema": "factory-cost-intelligence-receipt-v1",
        "at": _now(),
        "ok": ssot.get("schema") == "factory-cost-intelligence-loop-v1"
        and len(factories) >= 100
        and bool(ssot.get("one_law")),
        "one_law": ssot.get("one_law"),
        "registry_count": len(factories),
        "wef_gln_total": corpus.get("wef_gln_total_sites"),
        "cost_intelligence_line": cost_intelligence_line(ssot=ssot),
        "layers": (ssot.get("cost_intelligence_loop") or {}).get("layers") or [],
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def validate(*, check_mirror: bool = True) -> dict:
    ssot = load_ssot()
    factories = ssot.get("factories") or []
    ssot_ok = (
        ssot.get("schema") == "factory-cost-intelligence-loop-v1"
        and len(factories) == 100
        and bool(ssot.get("cost_intelligence_loop"))
        and bool(ssot.get("auto_prompting"))
        and bool(ssot.get("one_law"))
    )
    ids = [str(f.get("id") or "") for f in factories]
    unique_ids = len(set(ids)) == len(ids)
    mirror = _read(SINA / "agent-memory-mirror-v1.json")
    inject = mirror.get("inject") or {}
    mirror_ok = bool(inject.get("factory_cost_intelligence")) and bool(
        (inject.get("factory_cost_intelligence_detail") or {}).get("registry_count")
    )
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")
    surfaces_ok = bool(surfaces.get("cost_intelligence_line"))
    issues: list[str] = []
    if not ssot_ok:
        issues.append("ssot_incomplete")
    if not unique_ids:
        issues.append("duplicate_factory_ids")
    if check_mirror and not mirror_ok:
        issues.append("memory_mirror_inject_missing")
    if check_mirror and not surfaces_ok:
        issues.append("live_surfaces_cost_line_missing")
    ok = ssot_ok and unique_ids and (not check_mirror or (mirror_ok and surfaces_ok))
    return {
        "ok": ok,
        "ssot_ok": ssot_ok,
        "unique_ids": unique_ids,
        "mirror_inject_ok": mirror_ok,
        "surfaces_ok": surfaces_ok,
        "registry_count": len(factories),
        "cost_intelligence_line": cost_intelligence_line(ssot=ssot),
        "issues": issues,
    }


def run_wire(*, write: bool = True) -> dict:
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
    if surfaces and row.get("cost_intelligence_line"):
        surfaces["cost_intelligence_line"] = row["cost_intelligence_line"]
        surfaces["factory_cost_intelligence"] = {
            "ok": row.get("ok"),
            "receipt": str(RECEIPT),
            "registry_count": row.get("registry_count"),
            "wef_gln_total": row.get("wef_gln_total"),
            "ssot": "data/factory-cost-intelligence-loop-v1.json",
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
        contexts_ok = "cost-intel" in str(wrow.get("text_block") or "") and "cost-intel" in str(
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
        "cost_intelligence_line": row.get("cost_intelligence_line"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Factory cost intelligence loop")
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
        print(row.get("cost_intelligence_line") or row.get("ok"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
