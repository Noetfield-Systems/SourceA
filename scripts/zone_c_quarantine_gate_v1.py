#!/usr/bin/env python3
"""Zone C museum quarantine — block agent daily reads of command-data / legacy E2E.

Law: SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md · SOURCEA_GOV_META_AUDIT_LOCKED_v1.md
"""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ZONE_C_FORBIDDEN_PATHS = (
    "agent-control-panel/command-data.json",
    "agent-control-panel/command-data-shell.json",
    "agent-control-panel/command-data-canonical.json",
    "agent-control-panel/command-data-runtime.json",
)

ZONE_C_FORBIDDEN_TASK_RE = re.compile(
    r"(investigate\s+(the\s+)?hub|hub\s+e2e|audit\s+command-data|read\s+all\s+of\s+command-data|"
    r"open\s+sina\s+command\s+prompt\s+feed|prompt\s+feed\s+as\s+daily|confirm\s+auto[- ]?send)",
    re.I,
)

DAILY_STEER_RE = re.compile(
    r"(Open\s+Sina\s+Command\s*→\s*Prompt\s+feed|tap\s+Confirm.*auto[- ]?send\s+10)",
    re.I,
)


def museum_force() -> bool:
    v = os.environ.get("SINA_MUSEUM_FORCE", "").lower()
    return v in ("1", "true", "yes")


def check_zone_c(*, role: str, scan_text: str = "", target_paths: list[str] | None = None) -> dict:
    """Return ok=False if agent attempts Zone C SSOT or forbidden daily steer."""
    if museum_force():
        return {"ok": True, "skipped": "SINA_MUSEUM_FORCE=1"}

    hits: list[dict] = []
    text = scan_text or ""
    if text and ZONE_C_FORBIDDEN_TASK_RE.search(text):
        hits.append({"kind": "task", "detail": "forbidden museum/hub investigation or Prompt feed daily steer"})
    if text and DAILY_STEER_RE.search(text):
        hits.append({"kind": "close_line", "detail": "INCIDENT-028 daily steer in draft"})

    for rel in target_paths or []:
        norm = rel.replace(str(ROOT) + "/", "").replace(str(Path.home()), "~")
        for forbidden in ZONE_C_FORBIDDEN_PATHS:
            if forbidden in norm or norm.endswith("command-data.json"):
                hits.append({"kind": "path", "detail": f"Zone C forbidden read: {forbidden}"})

    if role in ("worker", "governance", "commercial", "brain") and hits:
        return {"ok": False, "zone": "C", "quarantine": True, "hits": hits, "law": "SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md"}
    return {"ok": True, "zone": "A", "hits": []}
