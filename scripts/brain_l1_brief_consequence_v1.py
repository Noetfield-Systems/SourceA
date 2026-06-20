#!/usr/bin/env python3
"""L1 brief → Brain consequence analysis — governance.constraints.yaml (B0601).

Reads: ~/.sina/research-root/filtered/governance.constraints.yaml
Writes: ~/.sina/brain-l1-brief-governance-constraints-receipt-v1.json
Law: brain-os/lanes/GOAL_SPECIALIST_CHAT_PACK_LOCKED_v1.md · UNIFIED_RESEARCH_ROOT
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
BRIEF = SINA / "research-root" / "filtered" / "governance.constraints.yaml"
RECEIPT = SINA / "brain-l1-brief-governance-constraints-receipt-v1.json"
FEDERATED = ROOT / "receipts" / "federated-run-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_brief() -> dict:
    if not BRIEF.is_file():
        return {"ok": False, "error": "missing_brief", "path": str(BRIEF)}
    try:
        import yaml  # noqa: WPS433

        data = yaml.safe_load(BRIEF.read_text(encoding="utf-8"))
        items = list((data or {}).get("items") or [])
        return {"ok": True, "path": str(BRIEF), "items": items, "count": len(items)}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "path": str(BRIEF)}


def _consequences(items: list) -> list[dict]:
    out: list[dict] = []
    for i, raw in enumerate(items[:5]):
        text = str(raw)[:240]
        out.append(
            {
                "constraint_ref": f"governance.constraints[{i}]",
                "summary": text[:120],
                "cloud_consequence": (
                    "Brain routes via cloud_api_worker — constraint blocks local Worker bypass; "
                    "Hub control plane must gate dispatch."
                ),
                "execution_plane": "cloud_api_worker",
                "control_plane": "mac_hub",
            }
        )
    return out


def run(*, upgrade_id: str = "B0601", write: bool = True) -> dict:
    brief = _load_brief()
    fed = _read_json(FEDERATED)
    consequences = _consequences(brief.get("items") or []) if brief.get("ok") else []
    row = {
        "schema": "brain-l1-brief-consequence-receipt-v1",
        "at": _now(),
        "upgrade_id": upgrade_id,
        "brief_file": "governance.constraints.yaml",
        "brief_path": str(BRIEF),
        "brief_ok": bool(brief.get("ok")),
        "brief_count": brief.get("count", 0),
        "trigger": "L1 brief governance.constraints.yaml → Brain consequence analysis",
        "owner_role": "brain",
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_hub",
        "local_worker_deprecated": True,
        "consequences": consequences,
        "federated_proof": {
            "ok": bool(fed.get("ok")),
            "remote_status": fed.get("remote_status"),
            "path": str(FEDERATED),
        },
        "ok": bool(brief.get("ok")) and bool(consequences) and bool(fed.get("ok")),
        "law": "GOAL_SPECIALIST_CHAT_PACK_LOCKED_v1.md",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="L1 governance.constraints.yaml → Brain consequence analysis")
    ap.add_argument("--upgrade-id", default="B0601")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = run(upgrade_id=args.upgrade_id, write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row.get('ok')} consequences={len(row.get('consequences') or [])}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
