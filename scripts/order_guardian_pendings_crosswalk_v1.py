#!/usr/bin/env python3
"""sa-0798 — crosswalk Order Guardian judgments/status vs WTM pendings."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from strategic_synthesis_hub import pendings  # noqa: E402
from task_orders_guardian import (  # noqa: E402
    STATUS_JUDGMENT_CONTRACT,
    _read_rows,
    judgment_contract_mismatches,
    orders_payload,
    pendings_orders_drift_warnings,
)


def build_report(*, hub_path: Path | None = None) -> dict:
    hub: dict = {}
    if hub_path and hub_path.is_file():
        hub = json.loads(hub_path.read_text(encoding="utf-8"))
    rows = _read_rows()
    payload = orders_payload(hub)
    status_judgment = Counter((r.get("status"), r.get("judgment")) for r in rows)
    return {
        "schema": "order-guardian-pendings-crosswalk-v1",
        "law": "ORDER_GUARDIAN_AGENT_LOCKED_v1.md",
        "task": "sa-0798",
        "orders_total": len(rows),
        "judgment_mismatches": judgment_contract_mismatches(rows),
        "judgment_mismatch_count": len(judgment_contract_mismatches(rows)),
        "status_judgment_histogram": [
            {"status": st, "judgment": jg, "count": n}
            for (st, jg), n in sorted(status_judgment.items(), key=lambda x: (-x[1], x[0][0] or ""))
        ],
        "pendings": [{"id": p.get("id"), "status": p.get("status"), "title": p.get("title")} for p in pendings()],
        "drift_warnings": pendings_orders_drift_warnings(hub),
        "advisory_signals": payload.get("advisory", {}).get("signals") or {},
        "contract": STATUS_JUDGMENT_CONTRACT,
        "ok": len(judgment_contract_mismatches(rows)) == 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Order guardian ↔ pendings crosswalk v1")
    ap.add_argument("--hub", default=str(ROOT / "agent-control-panel" / "command-data.json"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = build_report(hub_path=Path(args.hub))
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"CROSSWALK ok={report['ok']} mismatches={report['judgment_mismatch_count']} drift={len(report['drift_warnings'])}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
