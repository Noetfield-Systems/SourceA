#!/usr/bin/env python3
"""Judge Center temporal layer — past vs active STALE · correction · revert.

TRACE: SINA_JUDGE_STACK v2 temporal · three-layer judge (Human · Disk · AI)

Temporal tags (per chat, not whole-history stamp):
  TRUSTED          — recent window aligns with disk; past may contain archaeology
  PAST_STALE_ONLY  — stale claims only in old transcript; recent clean or corrected
  ACTIVE_STALE     — stale/wrong claims still appear in RECENT assistant output
  ACTIVE_BAD       — BAD conduct in recent window
  REVERT           — agent corrected then repeated stale claim in recent window
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Import pattern lists from audit module (shared SSOT)
from judge_center_patterns_v1 import BAD_PATTERNS, STALE_PATTERNS

RECENT_ASSISTANT_MESSAGES = 15
RECENT_CHAR_FRACTION = 0.25  # last 25% of transcript chars

CORRECTION_PATTERNS = [
    re.compile(r"\bsupersedes?_stale\b", re.I),
    re.compile(r"\bself[- ]?correct", re.I),
    re.compile(r"\bwas wrong\b|\bwas stale\b", re.I),
    re.compile(r"\bthree[- ]layer correction\b", re.I),
    re.compile(r"\bform v2\b.*\b(RT LIVE|9\.07)", re.I),
    re.compile(r"\bSTALE.*Jun 8", re.I),
    re.compile(r"\badmit.*wrong\b", re.I),
    re.compile(r"\bignore.*AUTO[- ]?RUN\b", re.I),
]

STALE_CLAIM_PATTERNS = [
    (re.compile(r"\bAUTO[- ]?RUN\b.*\b(P0|live proof|founder objective)\b", re.I), "autorun_p0"),
    (re.compile(r"\bgovernance model is complete\b", re.I), "governance_complete"),
    (re.compile(r"\bMaster Operating Tracker is the permanent founder command center\b", re.I), "tracker_ssot"),
]


@dataclass
class TranscriptWindows:
    all_text: str
    past_text: str
    recent_text: str
    recent_assistant_text: str
    assistant_message_count: int
    correction_hits: list[str] = field(default_factory=list)


def _extract_text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(str(part.get("text") or ""))
        return "\n".join(parts)
    return ""


def load_transcript_windows(path: Path) -> TranscriptWindows:
    """Parse JSONL line-by-line; recent = last N assistant messages + last char slice."""
    assistant_chunks: list[str] = []
    all_chunks: list[str] = []

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            import json

            row = json.loads(line)
        except Exception:
            continue
        text = _extract_text_from_content(row.get("content"))
        if not text:
            continue
        all_chunks.append(text)
        if row.get("role") == "assistant":
            assistant_chunks.append(text)

    all_text = "\n".join(all_chunks)
    recent_assist = assistant_chunks[-RECENT_ASSISTANT_MESSAGES:] if assistant_chunks else []
    recent_assistant_text = "\n".join(recent_assist)
    past_assist = assistant_chunks[:-RECENT_ASSISTANT_MESSAGES] if len(assistant_chunks) > RECENT_ASSISTANT_MESSAGES else []

    cut = int(len(all_text) * (1.0 - RECENT_CHAR_FRACTION))
    recent_text = all_text[cut:]
    past_text = all_text[:cut]

    correction_hits: list[str] = []
    for pat in CORRECTION_PATTERNS:
        if pat.search(recent_assistant_text) or pat.search(all_text[-50000:]):
            correction_hits.append(pat.pattern[:60])

    return TranscriptWindows(
        all_text=all_text,
        past_text="\n".join(past_assist) if past_assist else past_text,
        recent_text=recent_text,
        recent_assistant_text=recent_assistant_text,
        assistant_message_count=len(assistant_chunks),
        correction_hits=correction_hits,
    )


def _scan_patterns(text: str, form: dict | None = None) -> list[dict]:
    hits: list[dict] = []
    open_count = int((form or {}).get("open_questions_count") or 0)
    for pat, code in BAD_PATTERNS:
        for m in pat.finditer(text):
            hits.append({"tag": "BAD", "code": code, "excerpt": m.group(0)[:120]})
    for pat, code in STALE_PATTERNS:
        for m in pat.finditer(text):
            row: dict[str, Any] = {"code": code, "excerpt": m.group(0)[:120]}
            if code == "open_count_claim":
                try:
                    claimed = int(m.group(1))
                    row["tag"] = "STALE" if claimed != open_count else "RIGHT"
                    if claimed != open_count:
                        row["disk"] = f"open_questions_count={open_count}"
                except (IndexError, ValueError):
                    row["tag"] = "STALE"
            else:
                row["tag"] = "STALE"
            hits.append(row)
    seen: set[str] = set()
    out: list[dict] = []
    for h in hits:
        k = f"{h['code']}:{h['excerpt'][:60]}"
        if k in seen:
            continue
        seen.add(k)
        out.append(h)
    return out


def _detect_revert(windows: TranscriptWindows) -> list[dict]:
    """Correction acknowledged in recent history, then stale claim repeated after."""
    reverts: list[dict] = []
    recent = windows.recent_assistant_text
    if not windows.correction_hits:
        return reverts
    for pat, code in STALE_CLAIM_PATTERNS:
        matches = list(pat.finditer(recent))
        if matches and windows.correction_hits:
            reverts.append(
                {
                    "code": f"revert_{code}",
                    "excerpt": matches[-1].group(0)[:120],
                    "note": "Correction markers logged but stale claim repeated in recent assistant output",
                }
            )
    return reverts


def temporal_verdict(windows: TranscriptWindows, form: dict) -> dict:
    past_alarms = _scan_patterns(windows.past_text, form)
    recent_alarms = _scan_patterns(windows.recent_assistant_text, form)
    reverts = _detect_revert(windows)

    past_stale = [a for a in past_alarms if a.get("tag") == "STALE"]
    recent_stale = [a for a in recent_alarms if a.get("tag") == "STALE"]
    recent_bad = [a for a in recent_alarms if a.get("tag") == "BAD"]

    if recent_bad:
        overall = "ACTIVE_BAD"
        trust = "do_not_trust_recent"
    elif reverts:
        overall = "REVERT"
        trust = "do_not_trust_recent"
    elif recent_stale:
        overall = "ACTIVE_STALE"
        trust = "do_not_trust_recent"
    elif past_stale and not recent_stale:
        overall = "PAST_STALE_ONLY"
        trust = "trust_recent_ignore_past_headlines"
    elif windows.correction_hits and not recent_stale:
        overall = "TRUSTED"
        trust = "trust_recent_corrected"
    elif not past_stale and not recent_stale:
        overall = "TRUSTED"
        trust = "trust_recent"
    else:
        overall = "PAST_STALE_ONLY"
        trust = "trust_recent_ignore_past_headlines"

    return {
        "temporal_schema": "judge-center-temporal-v1",
        "overall": overall,
        "trust_recent": trust,
        "assistant_messages": windows.assistant_message_count,
        "recent_window_messages": min(RECENT_ASSISTANT_MESSAGES, windows.assistant_message_count),
        "correction_markers": windows.correction_hits,
        "past_stale_count": len(past_stale),
        "recent_stale_count": len(recent_stale),
        "recent_bad_count": len(recent_bad),
        "reverts": reverts,
        "past_alarms_sample": past_stale[:5],
        "recent_alarms_sample": recent_stale[:5] + recent_bad[:3],
        "founder_line": _founder_line(overall, past_stale, recent_stale, reverts, windows.correction_hits),
    }


def _founder_line(overall, past_stale, recent_stale, reverts, corrections) -> str:
    if overall == "TRUSTED":
        return "Trust RECENT replies · past archaeology optional"
    if overall == "PAST_STALE_ONLY":
        return f"Ignore PAST stale headlines ({len(past_stale)} hits) · RECENT window clean — agent may be corrected"
    if overall == "ACTIVE_STALE":
        return f"Do NOT trust RECENT output · {len(recent_stale)} active stale claim(s) vs disk today"
    if overall == "ACTIVE_BAD":
        return "Do NOT trust RECENT · BAD conduct in latest assistant messages"
    if overall == "REVERT":
        return "Do NOT trust RECENT · agent corrected then relapsed to stale claim"
    return "Review RECENT window manually"


def analyze_transcript(path: Path, form: dict) -> dict:
    windows = load_transcript_windows(path)
    return temporal_verdict(windows, form)
