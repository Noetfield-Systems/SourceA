#!/usr/bin/env python3
"""Apply ASF FIVE-STEP PICK lines → form §ANSWERED + applied-picks JSON."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORM_MD = ROOT / "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md"
APPLIED_PATH = Path.home() / ".sina/canvas-form-picks-applied-v1.json"
LOG_PATH = Path.home() / ".sina/founder-picks-applied-v1.jsonl"

PICK_RE = re.compile(
    r"ASF:\s*FIVE-STEP\s*[—\-]\s*PICK:\s*([A-Za-z0-9._-]+)\s+([A-Za-z0-9_]+)",
    re.IGNORECASE,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_applied() -> dict:
    if APPLIED_PATH.is_file():
        return json.loads(APPLIED_PATH.read_text(encoding="utf-8"))
    return {"schema": "canvas-form-picks-applied-v1", "picks": {}}


def _save_applied(data: dict) -> None:
    APPLIED_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    APPLIED_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _effect_for(qid: str) -> str:
    sys.path.insert(0, str(ROOT / "scripts"))
    from live_founder_decision_form_v1 import OPEN_QUESTIONS_CORE, PENDING_OUTSIDE_AS_OPEN  # noqa: WPS433

    for row in OPEN_QUESTIONS_CORE + PENDING_OUTSIDE_AS_OPEN:
        if row.get("id") == qid:
            return str(row.get("effect") or row.get("title") or qid)
    defaults = {
        "Q-AGENT-MEMORY-ENFORCE": "YES → AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1 bound on Canvas · session gate mandatory",
    }
    return defaults.get(qid, f"ASF PICK · {qid}")


def _append_answered(qid: str, pick: str, effect: str, receipt: str) -> bool:
    if not FORM_MD.is_file():
        return False
    text = FORM_MD.read_text(encoding="utf-8")
    if f"| **{qid}** |" in text:
        return False
    row = (
        f"| **{qid}** | ASF FIVE-STEP PICK | **{pick}** | "
        f"{effect[:140]} | `{receipt}` · {_now()}"
    )
    marker = "## 2. §ANSWERED — locked from evidence"
    if marker not in text:
        return False
    head, tail = text.split(marker, 1)
    lines = tail.splitlines()
    insert_at = 3
    for i, line in enumerate(lines):
        if line.strip().startswith("| **") and i > 2:
            insert_at = i
            break
    lines.insert(insert_at, row + " |")
    FORM_MD.write_text(head + marker + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return True


def parse_picks(text: str) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for m in PICK_RE.finditer(text):
        qid, pick = m.group(1).upper() if m.group(1).startswith("ENF") else m.group(1), m.group(2)
        if qid.startswith("Q-"):
            qid = qid  # keep case for Q- ids
        elif re.match(r"^\d+\.\d+$", qid):
            qid = m.group(1)
        else:
            qid = m.group(1)
        key = f"{qid}:{pick}"
        if key in seen:
            continue
        seen.add(key)
        out.append({"id": m.group(1), "pick": pick, "at": _now()})
    return out


def apply_picks(picks: list[dict], *, receipt: str, dry_run: bool) -> dict:
    applied = _load_applied()
    applied_picks = dict(applied.get("picks") or {})
    shipped: list[dict] = []

    for row in picks:
        qid = row["id"]
        pick = row["pick"]
        if applied_picks.get(qid) == pick:
            continue
        effect = _effect_for(qid)
        entry = {"id": qid, "pick": pick, "effect": effect, "receipt": receipt, "at": _now()}
        if not dry_run:
            if _append_answered(qid, pick, effect, receipt):
                entry["form_row"] = True
            applied_picks[qid] = pick
            with LOG_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        shipped.append(entry)

    if not dry_run and shipped:
        applied["picks"] = applied_picks
        _save_applied(applied)

    return {
        "ok": True,
        "dry_run": dry_run,
        "receipt": receipt,
        "applied_now": len(shipped),
        "applied_total": len(applied_picks),
        "shipped": shipped,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply ASF FIVE-STEP PICK lines to form")
    ap.add_argument("--text", help="Multiline PICK block")
    ap.add_argument("--file", type=Path, help="File containing PICK lines")
    ap.add_argument(
        "--receipt",
        default="SOURCEA_PACK5_ROOMS_PICK_BATCH_2026-06-12_LOCKED_v1.md",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = args.text or ""
    if args.file:
        raw = args.file.read_text(encoding="utf-8")
    if not raw.strip() and not sys.stdin.isatty():
        raw = sys.stdin.read()

    picks = parse_picks(raw)
    if not picks:
        print("FAIL: no PICK lines parsed", file=sys.stderr)
        return 1

    result = apply_picks(picks, receipt=args.receipt, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"OK: founder_pick_apply_v1 · applied_now={result['applied_now']} "
            f"total={result['applied_total']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
