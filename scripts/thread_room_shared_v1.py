"""Thread Room shared — transcript resolve · megachat anchors."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from judge_center_patterns_v1 import CHAT_ROLES  # noqa: E402

PROJECTS = Path.home() / ".cursor/projects"
THREAD_DIR = Path.home() / ".sina/thread-room"

MEGACHAT_DEFAULT = [
    "58148ac9",
    "6245d9dd",
    "e54ddfa8",
    "74f5ccab",
    "3369d11c",
    "a53f3fa1",
]

THREAD_ARCS: dict[str, str] = {
    "58148ac9": "THREAD-SUPERBRAIN",
    "6245d9dd": "THREAD-MERGEPACK",
    "e54ddfa8": "THREAD-ECOSYSTEM",
    "74f5ccab": "THREAD-FACTORY",
    "3369d11c": "THREAD-WIRE",
    "a53f3fa1": "THREAD-ECOSYSTEM",
}


def resolve_transcript(chat_id: str) -> Path | None:
    short = chat_id.strip().lower()
    if len(short) < 8:
        return None
    hits = sorted(PROJECTS.glob(f"*/agent-transcripts/{short}*/{short}*.jsonl"))
    return hits[0] if hits else None


def transcript_stats(path: Path) -> dict:
    user = assistant = 0
    first_user = ""
    last_assistant = ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = row.get("role")
        content = row.get("content")
        if isinstance(content, list):
            text = " ".join(
                p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"
            )
        else:
            text = str(content or "")
        if role == "user" and text:
            user += 1
            if not first_user:
                first_user = text[:200]
        elif role == "assistant" and text:
            assistant += 1
            last_assistant = text[:200]
    size = path.stat().st_size
    return {
        "user_messages": user,
        "assistant_messages": assistant,
        "bytes": size,
        "first_user_excerpt": first_user,
        "last_assistant_excerpt": last_assistant,
    }
