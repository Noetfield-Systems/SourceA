#!/usr/bin/env python3
"""Founder trigger retirement evaluator — earned autonomy (LP-EARNED-AUTONOMY)."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "founder-trigger-retirement-registry-v1.json"
BACKLOG = ROOT / "data" / "autorun-kaizen-backlog-v1.json"
RECEIPT = ROOT / "receipts" / "proof" / "founder-trigger-retirement-latest-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _receipt_ok(path: Path) -> bool:
    row = _read(path)
    return bool(row.get("ok"))


def _count_greens(sources: list[str]) -> int:
    greens = 0
    for src in sources:
        p = ROOT / src
        if _receipt_ok(p):
            greens += 1
    return greens


def _patch_kz002_unblock() -> bool:
    row = _read(BACKLOG)
    changed = False
    for item in row.get("items") or []:
        if isinstance(item, dict) and item.get("id") == "KZ-002" and item.get("blocked_until"):
            item.pop("blocked_until", None)
            item["status"] = "pending"
            changed = True
    if changed:
        row["saved_at"] = _now()
        BACKLOG.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return changed


def _patch_laws_tier1() -> bool:
    laws = ROOT / "docs" / "GOVERNED_AUTORUN_LAWS_v3.md"
    if not laws.is_file():
        return False
    text = laws.read_text(encoding="utf-8")
    if "machine_enabled" in text:
        return False
    new = text.replace(
        "**BLOCKED** until founder triggers Tier 1.",
        "**machine_enabled** — concurrency groups + conflict matrix green (FT-TIER1-PARALLEL-ORCH retired).",
    )
    if new != text:
        laws.write_text(new, encoding="utf-8")
        return True
    return False


def evaluate(*, dry_run: bool = False) -> dict[str, Any]:
    reg = _read(REGISTRY)
    retired: list[str] = []
    patches: list[str] = []

    for trig in reg.get("triggers") or []:
        if not isinstance(trig, dict) or trig.get("status") != "active":
            continue
        tid = str(trig.get("trigger_id") or "")
        required = int(trig.get("green_receipts_required") or 0)
        sources = trig.get("receipt_sources") or []
        greens = _count_greens(sources)
        trig["consecutive_green"] = greens
        if greens >= required:
            if not dry_run:
                trig["status"] = "retired"
                trig["retired_at"] = _now()
                if tid == "FT-KZ002-COPILOT-P4" and _patch_kz002_unblock():
                    patches.append("KZ-002 unblocked")
                if tid == "FT-TIER1-PARALLEL-ORCH" and _patch_laws_tier1():
                    patches.append("Tier1 parallel orch machine_enabled")
                if tid == "FT-MERGE-T0-T1":
                    patches.append("T0-T1 machine merge bootstrap retired")
            retired.append(tid)

    ledger_path = ROOT / "data" / "founder-trigger-ledger-v1.json"
    ledger = _read(ledger_path)
    if ledger and not dry_run:
        for lt in ledger.get("triggers") or []:
            for rt in reg.get("triggers") or []:
                if lt.get("trigger_id") == rt.get("trigger_id"):
                    lt["evidence_counter"] = rt.get("consecutive_green", 0)
        ledger["saved_at"] = _now()
        ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")

    if not dry_run:
        reg["saved_at"] = _now()
        REGISTRY.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")

    doc = {
        "schema": "founder-trigger-retirement-v1",
        "at": _now(),
        "ok": True,
        "retired": retired,
        "patches": patches,
        "triggers": [
            {"trigger_id": t.get("trigger_id"), "consecutive_green": t.get("consecutive_green"), "status": t.get("status")}
            for t in reg.get("triggers") or []
            if isinstance(t, dict)
        ],
        "report_line": (
            f"retirement_eval · retired={retired}" if retired else "retirement_eval · no triggers ready yet"
        ),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = evaluate(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
