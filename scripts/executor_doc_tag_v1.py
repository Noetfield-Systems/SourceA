#!/usr/bin/env python3
"""Auto (Cursor executor) doc tags — unique AUTO-TRACE-* on every saved artifact.

Law: brain-os/contract/DOC_TRACE_TAG_FORMAT_LOCKED_v1.md · agent Auto
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

AGENT_NAME = "Auto"
AGENT_REF = "AUTO_AGENT_REF"
PREFIX = "AUTO-TRACE"


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def make_tag(*, domain: str, artifact: str, major: int = 1, minor: int = 0) -> dict:
    """Return trace_tag per LOCKED format AUTO-TRACE-{DOMAIN}-{ARTIFACT}-vM.m"""
    dom = re.sub(r"[^A-Z0-9]+", "-", domain.upper()).strip("-")[:24] or "RUNTIME"
    art = re.sub(r"[^A-Z0-9]+", "-", artifact.upper()).strip("-")[:32] or "DOC"
    trace_tag = f"{PREFIX}-{dom}-{art}-v{major}.{minor}"
    return {
        "agent_ref": AGENT_REF,
        "agent": AGENT_NAME,
        "trace_tag": trace_tag,
        "written": _today(),
        "canonical": False,
    }


def header_md(*, domain: str, artifact: str, title: str, major: int = 1, minor: int = 0, workspace: str = "~/Desktop/SourceA") -> str:
    t = make_tag(domain=domain, artifact=artifact, major=major, minor=minor)
    return f"""[{AGENT_REF} · {AGENT_NAME} · {t['trace_tag']}]

**trace_tag:** `{t['trace_tag']}`
**agent:** `{AGENT_NAME}`

| Field | Value |
|-------|-------|
| **trace_tag** | `{t['trace_tag']}` |
| **agent** | `{AGENT_NAME}` |
| **repo_chat** | `SourceA` |
| **workspace** | `{workspace}` |
| **plane** | `EXECUTOR` |
| **thread** | `THREAD-ECOSYSTEM` |
| **canonical** | `false` |
| **adoption** | `GOVERNANCE_UNIFICATION_ENGINE` only |
| **written** | `{t['written']}` |

# {title}

"""


def script_comment(*, domain: str, artifact: str, path: str, major: int = 1, minor: int = 0) -> str:
    t = make_tag(domain=domain, artifact=artifact, major=major, minor=minor)
    return f"# TRACE: {t['trace_tag']} · agent {AGENT_NAME} · {path}"


def write_attachment(
    *,
    rel_path: str,
    domain: str,
    artifact: str,
    title: str,
    body: str,
    major: int = 1,
    minor: int = 0,
    root: Path | None = None,
) -> Path:
    root = root or Path(__file__).resolve().parents[1]
    out = root / rel_path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(header_md(domain=domain, artifact=artifact, title=title, major=major, minor=minor) + body.lstrip(), encoding="utf-8")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Auto doc tag helper (AUTO-TRACE-*)")
    p.add_argument("--domain", required=True, help="DOMAIN lane e.g. WORKER, RUNTIME")
    p.add_argument("--artifact", required=True, help="ARTIFACT slug e.g. BATCH-GATE-10")
    p.add_argument("--major", type=int, default=1)
    p.add_argument("--minor", type=int, default=0)
    p.add_argument("--json", action="store_true")
    p.add_argument("--header", action="store_true", help="Print markdown header only")
    p.add_argument("--script-comment", metavar="PATH", help="Print # TRACE line for a script")
    args = p.parse_args()
    if args.header:
        print(header_md(domain=args.domain, artifact=args.artifact, major=args.major, minor=args.minor, title=args.artifact.replace("-", " ")))
        return 0
    if args.script_comment:
        print(script_comment(domain=args.domain, artifact=args.artifact, path=args.script_comment, major=args.major, minor=args.minor))
        return 0
    row = make_tag(domain=args.domain, artifact=args.artifact, major=args.major, minor=args.minor)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["trace_tag"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
