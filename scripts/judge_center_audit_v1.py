#!/usr/bin/env python3
"""Judge Center L1 Audit — extract chat claims · alarm vs disk (no verdict).

TRACE: SINA_JUDGE_STACK_DRAFT_v1.md L1 · Q-JUDGE-STACK-v1
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = Path.home() / ".sina/judge-center"
CASES_PATH = CASES_DIR / "cases.jsonl"
PROJECTS = Path.home() / ".cursor/projects"

from judge_center_patterns_v1 import BAD_PATTERNS, CHAT_ROLES, STALE_PATTERNS


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_transcript(chat_id: str) -> Path | None:
    short = chat_id.strip().lower()
    if len(short) < 8:
        return None
    hits = sorted(PROJECTS.glob(f"*/agent-transcripts/{short}*/{short}*.jsonl"))
    return hits[0] if hits else None


def _load_form() -> dict:
    raw = subprocess.check_output(
        [sys.executable, str(ROOT / "scripts/live_founder_decision_form_v1.py"), "--json"],
        text=True,
    )
    return json.loads(raw)


def _extract_transcript_text(path: Path, max_chars: int = 2_000_000) -> str:
    """Raw transcript file text — robust for megachat JSONL (single-line rows)."""
    data = path.read_text(encoding="utf-8", errors="replace")
    return data[-max_chars:] if len(data) > max_chars else data


def _scan_alarms(text: str, form: dict) -> list[dict]:
    alarms: list[dict] = []
    open_count = int(form.get("open_questions_count") or 0)

    for pat, code in BAD_PATTERNS:
        for m in pat.finditer(text):
            alarms.append({"tag": "BAD", "code": code, "excerpt": m.group(0)[:120]})

    for pat, code in STALE_PATTERNS:
        for m in pat.finditer(text):
            tag = "STALE"
            detail = m.group(0)[:120]
            if code == "open_count_claim":
                claimed = int(m.group(1))
                if claimed != open_count:
                    alarms.append(
                        {
                            "tag": tag,
                            "code": code,
                            "excerpt": detail,
                            "disk": f"form open_questions_count={open_count}",
                        }
                    )
                else:
                    alarms.append({"tag": "RIGHT", "code": "open_count_match", "excerpt": detail})
            elif code == "success_without_path" and "FOUND —" not in text[-5000:]:
                alarms.append({"tag": tag, "code": code, "excerpt": detail})
            elif code not in ("success_without_path",):
                alarms.append({"tag": tag, "code": code, "excerpt": detail})

    if not alarms:
        alarms.append({"tag": "UNPROVEN", "code": "no_alarm_match", "excerpt": "no stale/bad patterns in sample"})
    # Dedupe by code + excerpt prefix
    seen: set[str] = set()
    unique: list[dict] = []
    for a in alarms:
        key = f"{a.get('code')}:{str(a.get('excerpt',''))[:80]}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(a)
    return unique


def audit_chats(chat_ids: list[str]) -> dict:
    form = _load_form()
    packets: list[dict] = []
    for cid in chat_ids:
        path = _resolve_transcript(cid)
        if not path:
            packets.append(
                {
                    "chat_id": cid,
                    "tag": "UNPROVEN",
                    "transcript": None,
                    "alarms": [{"tag": "UNPROVEN", "code": "transcript_missing", "excerpt": cid}],
                }
            )
            continue
        text = _extract_transcript_text(path)
        alarms = _scan_alarms(text, form)
        tags = {a["tag"] for a in alarms}
        archaeology = "BAD" if "BAD" in tags else "STALE" if "STALE" in tags else "RIGHT" if "RIGHT" in tags else "UNPROVEN"
        from judge_center_temporal_v1 import analyze_transcript

        temporal = analyze_transcript(path, form)
        overall = temporal.get("overall") or archaeology
        if archaeology in ("STALE", "BAD") and overall == "TRUSTED" and not temporal.get("correction_markers"):
            overall = "PAST_STALE_ONLY"
            temporal["overall"] = "PAST_STALE_ONLY"
            temporal["trust_recent"] = "trust_recent_ignore_past_headlines"
            temporal["founder_line"] = (
                f"Archaeology {archaeology} in full transcript — RECENT assistant window clean. "
                "Trust latest replies; ignore past headlines unless agent relapses."
            )
        packets.append(
            {
                "chat_id": cid,
                "role": CHAT_ROLES.get(cid[:8], "unknown"),
                "transcript": str(path),
                "tag": overall,
                "archaeology_tag": archaeology,
                "temporal": temporal,
                "alarms": alarms,
                "found": [f"FOUND — {path}"],
            }
        )

    case = {
        "schema": "judge-center-audit-v2",
        "audited_at": _now(),
        "form_open_count": int(form.get("open_questions_count") or 0),
        "packets": packets,
    }
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    with CASES_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(case, ensure_ascii=False) + "\n")
    return case


def main() -> int:
    parser = argparse.ArgumentParser(description="Judge Center L1 audit")
    parser.add_argument("--chats", required=True, help="Comma-separated chat id prefixes")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    ids = [c.strip() for c in args.chats.split(",") if c.strip()]
    result = audit_chats(ids)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for p in result["packets"]:
            print(f"{p['chat_id']}: {p['tag']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
