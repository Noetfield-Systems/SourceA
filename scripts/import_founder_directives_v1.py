#!/usr/bin/env python3
"""Import historical founder orders into ~/.sina/founder-directives.jsonl."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
SINA_HOME = Path.home() / ".sina"
DIRECTIVES_PATH = SINA_HOME / "founder-directives.jsonl"

from governance_paths_v1 import FOUNDER_FIRST_ASSISTANT_TRACKING

SOURCES = [
    SOURCE_A / "sina-bowl" / "MASTER_ORDERS.json",
    FOUNDER_FIRST_ASSISTANT_TRACKING,
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def jsonl_row_count() -> int:
    if not DIRECTIVES_PATH.is_file():
        return 0
    n = 0
    for line in DIRECTIVES_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            n += 1
    return n


def _existing_keys() -> set[str]:
    if not DIRECTIVES_PATH.is_file():
        return set()
    keys: set[str] = set()
    for line in DIRECTIVES_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        label = (row.get("title") or row.get("text") or "")[:120].lower()
        if label:
            keys.add(label)
    return keys


def _append(row: dict) -> None:
    SINA_HOME.mkdir(parents=True, exist_ok=True)
    with DIRECTIVES_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_import() -> dict:
    seen = _existing_keys()
    imported = 0
    now = _now()

    orders_path = SOURCE_A / "sina-bowl" / "MASTER_ORDERS.json"
    if orders_path.is_file():
        try:
            data = json.loads(orders_path.read_text(encoding="utf-8"))
            for item in data.get("orders") or data.get("must_do_today") or []:
                title = str(item.get("title") or item.get("text") or item.get("id") or "").strip()
                if not title or title.lower() in seen:
                    continue
                seen.add(title.lower())
                _append(
                    {
                        "id": f"DIR-{uuid.uuid4().hex[:10]}",
                        "at": now,
                        "title": title[:240],
                        "source": "MASTER_ORDERS.json",
                        "thread": item.get("thread") or "",
                        "status": "imported",
                    }
                )
                imported += 1
        except json.JSONDecodeError:
            pass

    law = FOUNDER_FIRST_ASSISTANT_TRACKING
    if law.is_file():
        title = "Founder First Assistant — track every idea and order"
        if title.lower() not in seen:
            _append(
                {
                    "id": f"DIR-{uuid.uuid4().hex[:10]}",
                    "at": now,
                    "title": title,
                    "source": law.name,
                    "thread": "THREAD-MAINTAINER",
                    "status": "imported",
                }
            )
            imported += 1

    return {"ok": True, "imported": imported, "path": str(DIRECTIVES_PATH), "jsonl_rows": jsonl_row_count()}


def run_import_on_build() -> dict:
    """Run import only when founder-directives.jsonl already has rows (sa-0219)."""
    rows = jsonl_row_count()
    if rows == 0:
        return {"ok": True, "skipped": True, "reason": "no jsonl rows", "jsonl_rows": 0, "imported": 0}
    out = run_import()
    out["jsonl_rows"] = rows
    out["skipped"] = False
    if not out.get("ok"):
        return out
    if not DIRECTIVES_PATH.is_file() or jsonl_row_count() < rows:
        return {"ok": False, "error": "jsonl missing or truncated after import", "jsonl_rows": rows}
    return out


if __name__ == "__main__":
    print(json.dumps(run_import_on_build(), indent=2))
