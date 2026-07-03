#!/usr/bin/env python3
"""Uncertainty → research pipeline intake (LP-RESEARCH) — no founder ping."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RECEIPT = ROOT / "receipts" / "proof" / "uncertainty-research-latest-v1.json"
PY = sys.executable
CONFIDENCE_THRESHOLD = 0.65


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def enqueue(*, question: str, mission_id: str = "M4", confidence: float = 0.5, intent: str = "") -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from agent_research_pipeline import submit_research  # noqa: WPS433

    op_key = hashlib.sha256(question.encode()).hexdigest()[:40]
    title = f"[{mission_id}] uncertainty: {question[:80]}"
    body = (
        f"Mission: {mission_id}\n"
        f"Confidence: {confidence}\n"
        f"Intent class: {intent or 'ambiguous'}\n"
        f"op_key: {op_key}\n\n"
        f"Question:\n{question}\n\n"
        "Machine-enqueued — resolve via research pipeline before Worker proceeds."
    )
    result = submit_research(
        {
            "title": title,
            "body": body,
            "source_agent": "sinaai_maintainer",
            "source_type": "agent_research",
        }
    )
    ok = bool(result.get("ok"))
    doc = {
        "schema": "uncertainty-research-v1",
        "at": _now(),
        "ok": ok,
        "mission_id": mission_id,
        "confidence": confidence,
        "op_key": op_key,
        "research_item": result.get("item"),
        "error": result.get("error"),
        "report_line": (
            f"uncertainty_research ENQUEUED · {result.get('item', {}).get('id', '')}"
            if ok
            else f"uncertainty_research FAIL · {result.get('error')}"
        ),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--question", required=True)
    ap.add_argument("--mission-id", default="M4")
    ap.add_argument("--confidence", type=float, default=0.5)
    ap.add_argument("--intent", default="ambiguous")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.confidence >= CONFIDENCE_THRESHOLD:
        row = {
            "schema": "uncertainty-research-v1",
            "at": _now(),
            "ok": True,
            "skipped": True,
            "reason": f"confidence {args.confidence} >= threshold — no enqueue",
            "report_line": "uncertainty_research SKIP · confidence sufficient",
        }
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    else:
        row = enqueue(
            question=args.question,
            mission_id=args.mission_id,
            confidence=args.confidence,
            intent=args.intent,
        )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
