#!/usr/bin/env python3
"""Apply M1 Canvas confirmed picks → form §ANSWERED (FORM_OFFICIAL wire)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FORM_MD = ROOT / "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md"
CANVAS_DATA = (
    Path.home()
    / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.data.json"
)
APPLIED_PATH = Path.home() / ".sina/canvas-form-picks-applied-v1.json"
LOG_PATH = Path.home() / ".sina/canvas-form-picks-applied-v1.jsonl"


def _dbg(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    return


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


def _append_answered(qid: str, pick: str, effect: str, comment: str) -> bool:
    if not FORM_MD.is_file():
        return False
    if qid in _answered_ids():
        return False
    text = FORM_MD.read_text(encoding="utf-8")
    row = (
        f"| **{qid}** | Canvas confirm | **{pick}** | "
        f"{effect[:120]} | `canvas_form_apply_picks_v1.py` · {_now()}"
    )
    if comment:
        row += f" · note: {comment[:80]}"
    row += " |\n"
    marker = "## 2. §ANSWERED — locked from evidence"
    if marker not in text:
        return False
    head, tail = text.split(marker, 1)
    lines = tail.splitlines()
    insert_at = 2 if len(lines) > 2 else len(lines)
    lines.insert(insert_at, row.rstrip())
    FORM_MD.write_text(head + marker + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return True


def _answered_ids() -> set[str]:
    if not FORM_MD.is_file():
        return set()
    text = FORM_MD.read_text(encoding="utf-8")
    if "## 2. §ANSWERED" not in text:
        return set()
    block = text.split("## 2. §ANSWERED", 1)[1]
    for marker in ("## 3.", "## 4.", "## 5."):
        if marker in block:
            block = block.split(marker, 1)[0]
            break
    return set(re.findall(r"\| \*\*([^|*]+)\*\* \|", block))


def _write_form_ship_receipt(*, shipped_ids: list[str], mode: str) -> Path:
    import hashlib

    receipt_path = Path.home() / ".sina/form-ship-receipt-v1.json"
    body = {
        "schema": "form-ship-receipt-v1",
        "ok": True,
        "mode": mode,
        "shipped_ids": sorted(shipped_ids),
        "at": _now(),
        "law": "SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md",
    }
    raw = json.dumps(body, sort_keys=True).encode("utf-8")
    body["receipt_checksum"] = hashlib.sha256(raw).hexdigest()[:16]
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return receipt_path


def _guard(actor: str, action: str, channel: str = "cli") -> dict | None:
    sys.path.insert(0, str(SCRIPTS))
    from form_founder_supremacy_guard_v1 import assert_founder_submit_allowed  # noqa: WPS433

    block = assert_founder_submit_allowed(actor=actor, action=action, channel=channel)
    return block if block.get("blocked") else None


def sync_applied_ship(*, dry_run: bool, actor: str = "agent", channel: str = "cli") -> dict:
    """Ship applied-json picks → §ANSWERED (fixes fake-green when open_ids hid rows)."""
    if not dry_run:
        blocked = _guard(actor, "sync_applied", channel=channel)
        if blocked:
            return blocked
    applied = _load_applied()
    applied_picks = dict(applied.get("picks") or {})
    answered = _answered_ids()
    missing = sorted(set(applied_picks.keys()) - answered)

    shipped: list[dict] = []
    for qid in missing:
        pick = str(applied_picks.get(qid) or "").strip()
        if not pick:
            continue
        row = {"id": qid, "pick": pick, "at": _now(), "mode": "sync_applied"}
        if not dry_run:
            if _append_answered(qid, pick, f"Canvas FORM_OFFICIAL sync · {qid}", ""):
                with LOG_PATH.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                shipped.append(row)
        else:
            shipped.append(row)

    receipt_path = None
    if not dry_run and missing:
        all_answered = _answered_ids()
        if set(applied_picks.keys()) <= all_answered:
            receipt_path = _write_form_ship_receipt(
                shipped_ids=sorted(applied_picks.keys()),
                mode="sync_applied_full",
            )

    sys.path.insert(0, str(ROOT / "scripts"))
    from live_founder_decision_form_v1 import all_open_questions  # noqa: WPS433

    return {
        "ok": True,
        "dry_run": dry_run,
        "missing_before": missing,
        "shipped_now": len(shipped),
        "shipped": shipped,
        "open_remaining": len(all_open_questions()),
        "form_ship_receipt": str(receipt_path) if receipt_path else None,
    }


def apply(*, canvas_path: Path, dry_run: bool, actor: str = "agent", channel: str = "cli") -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from live_founder_decision_form_v1 import all_open_questions  # noqa: WPS433

    if not dry_run:
        blocked = _guard(actor, "canvas_apply", channel=channel)
        if blocked:
            return blocked

    if not canvas_path.is_file():
        return {"ok": False, "error": f"missing canvas data: {canvas_path}"}

    state = json.loads(canvas_path.read_text(encoding="utf-8"))
    picks = state.get("picks") or {}
    confirmed = state.get("confirmed") or {}
    comments = state.get("comments") or {}

    open_rows = all_open_questions()
    open_ids = {q["id"] for q in open_rows}
    applied = _load_applied()
    applied_picks = dict(applied.get("picks") or {})

    shipped: list[dict] = []
    skip_reasons: list[dict] = []
    for qid, is_confirmed in confirmed.items():
        if not is_confirmed:
            continue
        if qid not in open_ids:
            skip_reasons.append({"id": qid, "reason": "not_in_open_ids"})
            continue
        pick = str(picks.get(qid) or "").strip()
        if not pick:
            skip_reasons.append({"id": qid, "reason": "confirmed_no_explicit_pick"})
            continue
        if applied_picks.get(qid) == pick:
            skip_reasons.append({"id": qid, "reason": "already_applied"})
            continue
        row = {"id": qid, "pick": pick, "comment": (comments.get(qid) or "").strip(), "at": _now()}
        if not dry_run:
            _append_answered(qid, pick, f"Canvas FORM_OFFICIAL · {qid}", row["comment"])
            applied_picks[qid] = pick
            with LOG_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        shipped.append(row)

    if not dry_run and shipped:
        applied["picks"] = applied_picks
        _save_applied(applied)

    remaining = len(open_ids) - len([i for i in open_ids if i in applied_picks])
    # #region agent log
    _dbg(
        "H2",
        "canvas_form_apply_picks_v1.py:apply",
        "apply_run",
        {
            "dry_run": dry_run,
            "open_ids_count": len(open_ids),
            "confirmed_true_count": sum(1 for v in confirmed.values() if v),
            "shipped_count": len(shipped),
            "skip_reasons": skip_reasons[:20],
            "open_remaining": remaining,
        },
    )
    # #endregion
    return {
        "ok": True,
        "dry_run": dry_run,
        "applied_now": len(shipped),
        "applied_total": len(applied_picks),
        "open_remaining": remaining,
        "shipped": shipped,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Wire Canvas confirms → form §ANSWERED")
    ap.add_argument("--canvas-data", default=str(CANVAS_DATA))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--sync-applied", action="store_true", help="Ship applied-json gaps → §ANSWERED")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--founder", action="store_true", help="Claim founder actor (still blocked unless unlock or trusted channel)")
    ap.add_argument("--channel", default="cli", choices=("cli", "hub_browser", "m1_canvas"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    actor = "founder" if args.founder else "agent"
    channel = str(args.channel or "cli")
    if args.sync_applied:
        result = sync_applied_ship(dry_run=not args.apply, actor=actor, channel=channel)
    else:
        result = apply(canvas_path=Path(args.canvas_data), dry_run=not args.apply, actor=actor, channel=channel)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"{'OK' if result.get('ok') else 'FAIL'}: "
            f"applied_now={result.get('applied_now', 0)} "
            f"open_remaining={result.get('open_remaining', '?')}"
        )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
