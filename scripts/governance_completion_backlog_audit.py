#!/usr/bin/env python3
"""Open founder decisions + integrity backlog — agents must not forget."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "PROGRAM_PROGRESS.json"
SESSION_LOG = ROOT / "SOURCEA_SYSTEM_INTEGRITY_SESSION_LOG_v1.md"
REQUESTS = Path.home() / ".sina/founder-requests/requests.jsonl"


def _load_progress() -> dict:
    if not PROGRESS.is_file():
        return {}
    return json.loads(PROGRESS.read_text(encoding="utf-8"))


def _load_requests() -> list[dict]:
    if not REQUESTS.is_file():
        return []
    by_id: dict[str, dict] = {}
    for line in REQUESTS.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = row.get("id") or ""
        if not rid:
            continue
        prev = by_id.get(rid)
        if not prev or (row.get("updated_at") or "") >= (prev.get("updated_at") or ""):
            by_id[rid] = row
    return list(by_id.values())


def audit() -> dict:
    items: list[dict] = []

    prog = _load_progress()
    for todo in prog.get("todos") or []:
        founder_open = (todo.get("founder_open") or "").strip()
        if founder_open:
            items.append(
                {
                    "severity": "high",
                    "source": "PROGRAM_PROGRESS",
                    "id": todo.get("id", ""),
                    "title": founder_open,
                    "action": "Founder PICK or Maintainer closeout per playbook",
                }
            )
        if todo.get("id") == "SYS-INTEGRITY-100" and todo.get("status") == "in_progress":
            items.append(
                {
                    "severity": "medium",
                    "source": "PROGRAM_PROGRESS",
                    "id": "SYS-INTEGRITY-100",
                    "title": "100-step integrity playbook still in_progress",
                    "action": "Continue Canvas Phases 3–10 or close Phase 1.10",
                }
            )

    if SESSION_LOG.is_file():
        text = SESSION_LOG.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\|\s*([\d.]+)\s+[^|]+\|\s*\*\*F\*\*\s*\|\s*\*\*(OPEN|WAIT|PARTIAL)\*\*", text):
            items.append(
                {
                    "severity": "critical",
                    "source": "SESSION_LOG",
                    "id": m.group(1),
                    "title": f"Founder step {m.group(1)} status {m.group(2)}",
                    "action": "ASF PICK + Effect or Maintainer execute receipt",
                }
            )
        if "1.10" in text and "**READY**" in text:
            items.append(
                {
                    "severity": "medium",
                    "source": "SESSION_LOG",
                    "id": "1.10",
                    "title": "Phase 1 closeout READY — not sealed",
                    "action": "Run Appendix B PASS + mark 1.10 DONE",
                }
            )

    for row in _load_requests():
        if row.get("status") not in ("open", "in_progress"):
            continue
        pri = row.get("priority", "")
        if pri not in ("critical", "high"):
            continue
        title = row.get("title", "")
        if "Phase 2 founder batch" in title and row.get("status") == "shipped":
            continue
        items.append(
            {
                "severity": "critical" if pri == "critical" else "high",
                "source": "founder_request_tracker",
                "id": row.get("id", ""),
                "title": title,
                "action": "Ship evidence or defer with ASF on Track",
            }
        )

    critical = [i for i in items if i["severity"] == "critical"]
    return {
        "ok": len(critical) == 0,
        "total": len(items),
        "critical_count": len(critical),
        "items": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true", help="Exit 1 if any critical backlog item")
    args = parser.parse_args()
    result = audit()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Governance completion backlog: {result['total']} item(s), critical={result['critical_count']}")
        for item in result["items"]:
            print(f"  [{item['severity']}] {item['source']} {item['id']}: {item['title']}")
    if args.check and not result["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
