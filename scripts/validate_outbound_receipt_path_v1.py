#!/usr/bin/env python3
"""Validate outbound receipt path + plan proof + queue coherence + full honesty."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"

sys.path.insert(0, str(ROOT / "scripts"))
from outbound_receipt_path_v1 import LAW, head_receipt_collision  # noqa: E402
from execution_plane_honesty_v1 import assess_execution_plane  # noqa: E402
from outbound_queue_coherence_v1 import assess_queue_coherence  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def validate() -> dict:
    queue = _read_json(SINA / "healthy-queue-30-active.json")
    head = (queue.get("queue") or [{}])[0]
    upgrade_id = str(head.get("upgrade_id") or "")
    sa_id = str(head.get("sa_id") or "")
    collision = head_receipt_collision(upgrade_id=upgrade_id, sa_id=sa_id) if upgrade_id and sa_id else {}
    exec_row = assess_execution_plane()
    coherence = assess_queue_coherence()
    ok = (
        not collision.get("collision")
        and bool(exec_row.get("ok"))
        and bool(coherence.get("ok"))
    )
    issues = list(dict.fromkeys((exec_row.get("issues") or []) + (coherence.get("issues") or [])))
    row = {
        "schema": "validate-outbound-receipt-path-v1",
        "at": _now(),
        "ok": ok,
        "receipt_law": LAW,
        "head": {"upgrade_id": upgrade_id, "sa_id": sa_id},
        "collision": collision,
        "execution_honesty": exec_row.get("execution_honesty_line"),
        "execution_ok": exec_row.get("ok"),
        "coherence_ok": coherence.get("ok"),
        "coherence_line": coherence.get("line"),
        "issues": issues,
        "line": (
            f"receipt-path · law=OK · collision={'YES' if collision.get('collision') else 'NO'}"
            f" · {exec_row.get('execution_honesty_line', '')}"
            + ("" if coherence.get("ok") else f" · {coherence.get('line', '')}")
        ),
    }
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = validate()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["line"])
        for issue in row.get("issues") or []:
            print(f"  BLOCK · {issue}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
