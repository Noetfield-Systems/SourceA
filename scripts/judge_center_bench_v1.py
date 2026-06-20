#!/usr/bin/env python3
"""Judge Center L3 Bench — final resolution · form row drafts · remediation prompts.

TRACE: SINA_JUDGE_STACK_DRAFT_v1.md L3 · Q-JUDGE-STACK-v1
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

JUDGE_DIR = Path.home() / ".sina/judge-center"
RESOLUTIONS_DIR = JUDGE_DIR / "resolutions"
PENDING_FORM = JUDGE_DIR / "pending-form-rows.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _founder_resolution_lines(briefs: list[dict]) -> list[str]:
    lines: list[str] = []
    for b in briefs:
        cid = b.get("chat_id", "?")
        role = b.get("role", "unknown")
        overall = b.get("overall", "UNPROVEN")
        temporal = b.get("temporal") or {}
        founder_line = temporal.get("founder_line") or ""
        lines.append(f"CHAT {cid} ({role}): {overall}")
        if founder_line:
            lines.append(f"  BINDING: {founder_line}")
        seen: set[str] = set()
        for s in b.get("settlements") or []:
            key = str(s.get("resolution", ""))[:100]
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"  SETTLED — {s.get('resolution')}")
        for e in b.get("escalations") or []:
            key = str(e.get("resolution", ""))[:100]
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"  ESCALATE — {e.get('resolution')}")
        if b.get("keep_using"):
            lines.append(f"  KEEP: {', '.join(b['keep_using'])}")
        if b.get("ignore_stale"):
            lines.append(f"  IGNORE: {', '.join(b['ignore_stale'])}")
    return lines


def _collect_form_actions(briefs: list[dict]) -> list[dict]:
    seen: set[str] = set()
    rows: list[dict] = []
    for b in briefs:
        for block in (b.get("settlements") or []) + (b.get("escalations") or []):
            action = block.get("form_action")
            if not action or action in seen:
                continue
            seen.add(action)
            qid = action.split(":")[-1].strip().split()[0] if "PICK:" in action else action
            rows.append(
                {
                    "id": qid.replace("ASF: FIVE-STEP — PICK: ", "").strip(),
                    "source_chat": b.get("chat_id"),
                    "pick_hint": action,
                    "reason": block.get("resolution"),
                    "class": block.get("class"),
                }
            )
    return rows


def _answered_pick_ids() -> set[str]:
    """PACK5 picks already on Form §ANSWERED — exclude from judge alarm drafts."""
    answered: set[str] = set()
    try:
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "scripts"))
        from live_founder_decision_form_v1 import FORM_MD  # noqa: WPS433

        if FORM_MD.is_file():
            text = FORM_MD.read_text(encoding="utf-8")
            for m in re.finditer(r"\|\s*\*\*([A-Z0-9._-]+)\*\*\s*\|", text):
                answered.add(m.group(1))
    except Exception:
        pass
    # Hard-locked PACK5 batch (founder PICK 2026-06-12)
    answered.update(
        {
            "Q-JUDGE-STACK-v1",
            "Q-THREAD-ROOM-v1",
            "Q-AGENT-MEMORY-ENFORCE",
            "Q-M2-FORM-SYNC",
            "Q-M2-029",
            "Q-1.10-SEAL",
            "Q-M2-READ",
            "Q-SYS-INTEGRITY-RESUME",
            "Q-ENGINE-TEST-01",
            "Q-ENGINE-TEST-02",
            "Q-MONO-SSOT-LANE",
        }
    )
    return answered


def bench(counsel: dict) -> dict:
    briefs = counsel.get("briefs") or []
    form_rows = _collect_form_actions(briefs)
    answered = _answered_pick_ids()
    form_rows = [r for r in form_rows if str(r.get("id", "")).split()[0] not in answered]

    # System-wide resolution (founder-facing)
    trusted = [b["chat_id"] for b in briefs if b.get("overall") in ("RIGHT", "TRUSTED")]
    past_only = [b["chat_id"] for b in briefs if b.get("overall") == "PAST_STALE_ONLY"]
    active_stale = [b["chat_id"] for b in briefs if b.get("overall") in ("STALE", "ACTIVE_STALE", "REVERT")]
    bad_chats = [b["chat_id"] for b in briefs if b.get("overall") in ("BAD", "ACTIVE_BAD")]
    right_chats = trusted

    executive = (
        f"Judge Center batch {counsel.get('case_id')}: "
        f"{len(trusted)} TRUSTED/RIGHT · {len(past_only)} PAST_STALE_ONLY · "
        f"{len(active_stale)} ACTIVE_STALE · {len(bad_chats)} BAD · "
        f"{len(form_rows)} form actions. "
        "RECENT window wins over archaeology. Binding PICK still on M1 Canvas."
    )

    remediation: list[dict] = []
    for b in briefs:
        if b.get("overall") not in ("BAD", "ACTIVE_BAD", "STALE", "ACTIVE_STALE", "REVERT"):
            continue
        remediation.append(
            {
                "chat_id": b.get("chat_id"),
                "role": b.get("role"),
                "prompt": (
                    f"[JUDGE REMEDIATION] Chat {b.get('chat_id')} classified {b.get('overall')}. "
                    f"Re-read live_founder_decision_form_v1.py --json before any P0/complete claim. "
                    f"Ignore: {', '.join(b.get('ignore_stale') or [])}. "
                    f"Keep: {', '.join(b.get('keep_using') or [])}."
                ),
            }
        )

    return {
        "schema": "judge-center-bench-v1",
        "case_id": counsel.get("case_id"),
        "benched_at": _now(),
        "counsel_ref": counsel.get("counselled_at"),
        "executive_resolution": executive,
        "summary": {
            "trusted": trusted,
            "past_stale_only": past_only,
            "active_stale": active_stale,
            "right": right_chats,
            "stale": active_stale,
            "bad": bad_chats,
            "temporal_summary": {
                "trusted": trusted,
                "past_stale_only": past_only,
                "active_stale": active_stale,
                "bad": bad_chats,
            },
            "form_actions_count": len(form_rows),
        },
        "founder_resolution": _founder_resolution_lines(briefs),
        "form_row_drafts": form_rows,
        "remediation_prompts": remediation,
        "founder_pick_required": [
            r.get("pick_hint") or r.get("id")
            for r in form_rows
            if str(r.get("id", "")).split()[0] not in answered
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Judge Center L3 bench")
    parser.add_argument("--brief", help="Counsel JSON path")
    parser.add_argument("--latest", action="store_true", help="Use latest-counsel-v1.json")
    parser.add_argument("--write-form", action="store_true", help="Append pending form rows")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.latest:
        path = JUDGE_DIR / "latest-counsel-v1.json"
    elif args.brief:
        path = Path(args.brief)
    else:
        print("FAIL: --brief or --latest required", file=sys.stderr)
        return 1

    counsel = json.loads(path.read_text(encoding="utf-8"))
    judgment = bench(counsel)

    RESOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESOLUTIONS_DIR / f"{judgment['case_id']}.json"
    out.write_text(json.dumps(judgment, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    latest = JUDGE_DIR / "latest-resolution-v1.json"
    latest.write_text(json.dumps(judgment, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.write_form and judgment.get("form_row_drafts"):
        with PENDING_FORM.open("a", encoding="utf-8") as fh:
            for row in judgment["form_row_drafts"]:
                fh.write(json.dumps({"case_id": judgment["case_id"], **row}, ensure_ascii=False) + "\n")

    if args.json:
        print(json.dumps(judgment, indent=2))
    else:
        print(judgment["executive_resolution"])
        print(f"WROTE {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
