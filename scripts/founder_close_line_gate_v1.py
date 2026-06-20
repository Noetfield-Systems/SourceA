#!/usr/bin/env python3
"""Founder close-line gate — block INCIDENT-028 class phrases in agent output.

Law: SINA_WORKER_STALE_PROMPT_FEED_AUTOSEND_INCIDENT_028_LOCKED_v1.md
      AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from agent_memory_mirror_v1 import FORBIDDEN, INJECT_LAW  # noqa: E402


# Additional founder-output — stale daily steering only (not word-ban law)
STALE_DAILY_STEER = re.compile(
    r"Open\s+Sina\s+Command|Prompt\s+feed\s*→|tap\s+Refresh\s+in\s+Sina\s+Command",
    re.I,
)


def scan_text(text: str) -> dict:
    hits: list[dict] = []
    for fid, pat, inc, label in FORBIDDEN:
        m = re.search(pat, text or "", re.I)
        if m:
            hits.append(
                {
                    "id": fid,
                    "incident": inc,
                    "label": label,
                    "excerpt": m.group(0)[:120],
                }
            )
    for m in STALE_DAILY_STEER.finditer(text or ""):
        hits.append(
            {
                "id": "F23",
                "incident": "034",
                "label": "stale daily hub steering (use live surfaces)",
                "excerpt": m.group(0)[:120],
            }
        )
    return {
        "schema": "founder-close-line-gate-v1",
        "ok": len(hits) == 0,
        "hits": hits,
        "correct_line": INJECT_LAW.get("founder_close_line", ""),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Founder close-line gate v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    body = args.text
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8", errors="replace")
    result = scan_text(body)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"CLOSE_LINE ok={result['ok']} hits={len(result['hits'])}")
        for h in result["hits"]:
            print(f"  {h['id']} {h['label']}: {h['excerpt']!r}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
