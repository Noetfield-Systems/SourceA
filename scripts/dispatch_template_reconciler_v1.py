#!/usr/bin/env python3
"""Dispatch template reconciler — R2 instantiate from failure receipts (MACHINE_LOOPS §4)."""
from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / ".agent-policy" / "dispatch-templates"
QUEUE_DIR = ROOT / "receipts" / "cloud" / "dispatch-queue"
RECEIPT = ROOT / "receipts" / "proof" / "dispatch-instantiated-latest-v1.json"
CANON_VERSION = "FOUNDER_CANON_v1"

FAILURE_SCHEMAS = frozenset(
    {
        "self-repair-v1",
        "adversarial-critic-v1",
        "machine-cycle-v1",
        "autorun-pending-v1",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_template(template_id: str) -> dict[str, Any]:
    for path in TEMPLATE_DIR.glob("*.json"):
        row = _read(path)
        if row.get("template_id") == template_id:
            return row
    return {}


def _failure_sources() -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    checks = [
        ("self_repair", ROOT / "receipts/proof/self-repair-latest-v1.json"),
        ("critic", ROOT / "receipts/proof/adversarial-critic-latest-v1.json"),
        ("machine_cycle", ROOT / "receipts/proof/machine-cycle-latest-v1.json"),
        ("pending", ROOT / "receipts/cloud/autorun-pending/pending-latest-v1.json"),
    ]
    for name, path in checks:
        row = _read(path)
        if not row:
            continue
        schema = str(row.get("schema") or "")
        if name == "critic" and row.get("verdict") == "REJECT":
            sources.append({"source": name, "path": str(path), "row": row})
        elif name == "machine_cycle" and not row.get("ok"):
            sources.append({"source": name, "path": str(path), "row": row})
        elif name == "pending" and int(row.get("count") or 0) > 0:
            sources.append({"source": name, "path": str(path), "row": row})
        elif name == "self_repair" and row.get("filed"):
            sources.append({"source": name, "path": str(path), "row": row})
    return sources


def reconcile(*, dry_run: bool = False) -> dict[str, Any]:
    sources = _failure_sources()
    dispatches: list[dict[str, Any]] = []

    for src in sources:
        source_name = src["source"]
        row = src["row"]
        if source_name in ("critic", "machine_cycle", "pending"):
            tmpl = _load_template("repair-from-failure-v1")
            if not tmpl:
                continue
            excerpt = json.dumps(row)[:400]
            op_key = hashlib.sha256(excerpt.encode()).hexdigest()[:40]
            disp = {
                "dispatch_id": f"DISP-{uuid.uuid4().hex[:10]}",
                "template_id": tmpl.get("template_id"),
                "canon_version": CANON_VERSION,
                "at": _now(),
                "op_key": op_key,
                "source": source_name,
                "source_path": src["path"],
                "parameters": {
                    "failure_receipt_path": src["path"],
                    "log_excerpt": excerpt[:200],
                },
                "law": "R2 — fresh lane repair; failed lane preserved read-only",
            }
            dispatches.append(disp)
        elif source_name == "self_repair":
            filed = row.get("filed") if isinstance(row.get("filed"), dict) else {}
            dispatches.append(
                {
                    "dispatch_id": f"DISP-{uuid.uuid4().hex[:10]}",
                    "template_id": "repair-from-failure-v1",
                    "canon_version": CANON_VERSION,
                    "at": _now(),
                    "op_key": hashlib.sha256(str(filed.get("id", "")).encode()).hexdigest()[:40],
                    "source": "kaizen_filed",
                    "parameters": {"kaizen_id": filed.get("id"), "title": filed.get("title")},
                    "status": "queued_for_worker",
                }
            )

    if not dispatches and not dry_run:
        worker_tmpl = _load_template("worker-cycle-v1")
        if worker_tmpl:
            dispatches.append(
                {
                    "dispatch_id": f"DISP-{uuid.uuid4().hex[:10]}",
                    "template_id": "worker-cycle-v1",
                    "canon_version": CANON_VERSION,
                    "at": _now(),
                    "op_key": hashlib.sha256(_now().encode()).hexdigest()[:40],
                    "source": "idle_kaizen",
                    "parameters": {"mission_id": "M4", "task": "machine_safe kaizen pick"},
                    "status": "idle_no_work_fallback",
                }
            )

    queue_doc = {
        "schema": "dispatch-queue-v1",
        "at": _now(),
        "count": len(dispatches),
        "dispatches": dispatches,
    }

    doc = {
        "schema": "dispatch-instantiated-v1",
        "version": "1.0.0",
        "canon_version": CANON_VERSION,
        "at": _now(),
        "ok": True,
        "sources_scanned": len(sources),
        "dispatched": len(dispatches),
        "dispatches": dispatches,
        "dry_run": dry_run,
        "report_line": (
            f"dispatch_reconciler · {len(dispatches)} instantiated from {len(sources)} failure sources"
            if dispatches
            else "dispatch_reconciler · IDLE_NO_WORK · no failure sources"
        ),
    }

    if not dry_run:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        (QUEUE_DIR / "pending-v1.json").write_text(json.dumps(queue_doc, indent=2) + "\n", encoding="utf-8")
        mirror = Path.home() / ".sina" / "dispatch-queue-pending-v1.json"
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_text(json.dumps(queue_doc, indent=2) + "\n", encoding="utf-8")

    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = reconcile(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
