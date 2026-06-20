#!/usr/bin/env python3
"""Export one-sa event chain as JSONL — EVENT_CONTRACT.yaml field names (HUB-P0-2)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS_DIR = Path.home() / ".sina" / "events"
BROKER = Path.home() / ".sina" / "goal1-lane-broker-events.jsonl"
INTERNAL_KEYS = frozenset({"raw", "internal", "debug", "stack"})


def _sa_match(row: dict, sa_id: str) -> bool:
    sid = sa_id.lower()
    data = row.get("data") or {}
    for key in ("sa_id", "sa", "task_id", "id"):
        val = row.get(key) or data.get(key)
        if val and str(val).lower() == sid:
            return True
    trace = str(row.get("trace_id") or "")
    if sid in trace.lower():
        return True
    payload = json.dumps(row, ensure_ascii=False).lower()
    return sid in payload


def _normalize(row: dict, *, customer: bool) -> dict:
    evt = row.get("event") or row.get("kind") or row.get("event_type") or "UNKNOWN"
    out = {
        "at": row.get("at") or row.get("ts"),
        "event": evt,
        "actor": row.get("actor") or row.get("source") or "unknown",
        "trace_id": row.get("trace_id"),
        "data": row.get("data") or {},
    }
    if customer:
        data = {k: v for k, v in (out.get("data") or {}).items() if k not in INTERNAL_KEYS}
        out["data"] = data
    return out


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def collect_chain(sa_id: str) -> list[dict]:
    rows: list[dict] = []
    if EVENTS_DIR.is_dir():
        for path in sorted(EVENTS_DIR.glob("*.jsonl")):
            rows.extend(_read_jsonl(path))
    rows.extend(_read_jsonl(BROKER))
    matched = [r for r in rows if _sa_match(r, sa_id)]
    matched.sort(key=lambda r: str(r.get("at") or r.get("ts") or ""))
    return matched


def export_chain(sa_id: str, *, customer: bool = False) -> tuple[list[dict], dict]:
    raw = collect_chain(sa_id)
    chain = [_normalize(r, customer=customer) for r in raw]
    kinds = {r["event"] for r in chain}
    meta = {
        "sa_id": sa_id,
        "count": len(chain),
        "has_worker_started": "WORKER_STARTED" in kinds,
        "events": sorted(kinds),
        "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "contract": "brain-os/system/EVENT_CONTRACT.yaml",
    }
    return chain, meta


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sa_id", required=True)
    p.add_argument("--customer", action="store_true")
    p.add_argument("--check", action="store_true", help="Exit 1 if WORKER_STARTED missing")
    p.add_argument("--out", default="")
    args = p.parse_args()
    chain, meta = export_chain(args.sa_id, customer=args.customer)
    if args.check and not meta["has_worker_started"] and chain:
        print(f"FAIL: WORKER_STARTED missing for {args.sa_id}", file=sys.stderr)
        return 1
    if args.out:
        Path(args.out).write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in chain) + ("\n" if chain else ""),
            encoding="utf-8",
        )
    else:
        for row in chain:
            print(json.dumps(row, ensure_ascii=False))
    if args.check:
        print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
