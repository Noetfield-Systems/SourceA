#!/usr/bin/env python3
"""CI failure → Kaizen machine_safe auto-file + pick (LP-SELF-REPAIR)."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "data" / "autorun-kaizen-backlog-v1.json"
RECEIPT = ROOT / "receipts" / "proof" / "self-repair-latest-v1.json"
PY = sys.executable


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": "autorun-kaizen-backlog-v1", "items": []}


def file_kaizen(*, title: str, evidence_url: str, log_excerpt: str) -> dict[str, Any]:
    row = _read(BACKLOG)
    items = row.get("items") if isinstance(row.get("items"), list) else []
    kid = f"KZ-CI-{uuid.uuid4().hex[:6]}"
    max_rank = max((int(i.get("roi_rank") or 0) for i in items if isinstance(i, dict)), default=0)
    item = {
        "id": kid,
        "title": title[:120],
        "status": "pending",
        "class": "machine_safe",
        "value_class": "hygiene",
        "roi_rank": max_rank + 1,
        "plane": "P6_improvement",
        "evidence_url": evidence_url,
        "log_excerpt": log_excerpt[:500],
        "source": "self_repair_ci_to_kaizen_v1",
    }
    items.append(item)
    row["items"] = items
    row["saved_at"] = _now()
    BACKLOG.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return item


def run_repair(*, run_url: str = "", log_excerpt: str = "", workflow: str = "") -> dict[str, Any]:
    excerpt = log_excerpt.strip()
    if not excerpt and run_url:
        excerpt = f"CI failure at {run_url} — inspect Actions log"
    if not excerpt:
        excerpt = "CI failure — manual stub; provide --log-excerpt"

    title = f"CI fix: {workflow or 'workflow'} — {excerpt[:60]}"
    item = file_kaizen(title=title, evidence_url=run_url, log_excerpt=excerpt)

    pick_out = ""
    try:
        pick_out = subprocess.check_output(
            [PY, str(ROOT / "scripts" / "autorun_kaizen_queue_v1.py"), "--pick", "--json"],
            text=True,
            cwd=str(ROOT),
        )
        pick = json.loads(pick_out)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        pick = {"ok": False, "report_line": "kaizen pick failed"}

    doc = {
        "schema": "self-repair-v1",
        "at": _now(),
        "ok": True,
        "filed": item,
        "pick": pick,
        "report_line": f"self_repair · filed {item['id']} · {pick.get('report_line', '')}",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from-run-url", default="")
    ap.add_argument("--log-excerpt", default="")
    ap.add_argument("--workflow", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_repair(run_url=args.from_run_url, log_excerpt=args.log_excerpt, workflow=args.workflow)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
