#!/usr/bin/env python3
"""Register Brain research insights — library + unified research root."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

LIB_ROOT = Path.home() / ".sina" / "brain" / "research-library"
REGISTRY = Path.home() / ".sina" / "research-root" / "registry.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def register(*, subject: str, title: str, insight: str, links: list[str] | None = None) -> dict:
    subject_path = LIB_ROOT / "subjects" / f"{subject}.md"
    if not subject_path.is_file():
        subject_path = LIB_ROOT / "subjects" / f"{subject.replace('_', '-')}.md"
    footer = f"\n\n## Session append ({_now()})\n- **{title}:** {insight}\n"
    if links:
        for u in links:
            footer += f"- link: {u}\n"
    if subject_path.is_file():
        text = subject_path.read_text(encoding="utf-8")
        if insight not in text:
            subject_path.write_text(text.rstrip() + footer, encoding="utf-8")

    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "id": f"brain-lib-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
        "at": _now(),
        "producer": "brain",
        "bucket": "execution_core",
        "subject": subject,
        "title": title,
        "insight": insight,
        "path": str(subject_path),
        "links": links or [],
    }
    with REGISTRY.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return {"ok": True, "registered": row}


def main() -> int:
    p = argparse.ArgumentParser(description="Brain research register")
    p.add_argument("--subject", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--insight", required=True)
    p.add_argument("--link", action="append", default=[])
    args = p.parse_args()
    print(json.dumps(register(
        subject=args.subject,
        title=args.title,
        insight=args.insight,
        links=args.link or None,
    ), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
