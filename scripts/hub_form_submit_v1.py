#!/usr/bin/env python3
"""Hub FORM_OFFICIAL submit — founder explicit picks only (INCIDENT-037).

Law: SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md · INCIDENT-037
Golden rule: FOUNDER PICK > AGENT RECOMMENDATION > DISK GATHER ROW
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CANVAS_DATA = (
    Path.home()
    / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.data.json"
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_pick(raw: str) -> str:
    return str(raw or "").strip().upper()[:12]


def build_founder_picks_state(*, overrides: dict | None = None) -> dict:
    """Build submit state from explicit founder picks only — never from recommended."""
    sys.path.insert(0, str(SCRIPTS))
    from live_founder_decision_form_v1 import all_open_questions  # noqa: WPS433

    overrides = overrides or {}
    picks: dict[str, str] = {}
    confirmed: dict[str, bool] = {}
    rows: list[dict] = []

    for q in all_open_questions():
        qid = str(q.get("id") or "")
        if not qid:
            continue
        pick = _normalize_pick(overrides.get(qid, ""))
        if pick:
            picks[qid] = pick
            confirmed[qid] = True
            rows.append({"id": qid, "pick": pick, "recommended": q.get("recommended")})

    open_ids = [str(q.get("id") or "") for q in all_open_questions() if q.get("id")]
    missing = [qid for qid in open_ids if qid not in picks]

    return {
        "picks": picks,
        "confirmed": confirmed,
        "rows": rows,
        "count": len(rows),
        "open_count": len(open_ids),
        "missing_ids": missing,
        "complete": not missing,
    }


def build_automatic_state(*, overrides: dict | None = None) -> dict:
    """Deprecated alias — returns founder-picks state only (no recommended backfill)."""
    return build_founder_picks_state(overrides=overrides)


def _write_canvas_state(state: dict) -> Path:
    CANVAS_DATA.parent.mkdir(parents=True, exist_ok=True)
    existing: dict = {}
    if CANVAS_DATA.is_file():
        try:
            existing = json.loads(CANVAS_DATA.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
    existing["picks"] = state["picks"]
    existing["confirmed"] = state["confirmed"]
    if state.get("comments"):
        merged = dict(existing.get("comments") or {})
        merged.update(state["comments"])
        existing["comments"] = merged
    existing["view"] = "pending-confirmations"
    existing["hub_form_submit_at"] = _now()
    existing["hub_form_founder_submit"] = True
    existing.pop("hub_form_automatic", None)
    CANVAS_DATA.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return CANVAS_DATA


def submit_founder_picks(
    *,
    overrides: dict | None = None,
    comments: dict | None = None,
    cascade_hub: bool = True,
    partial_batch: bool = False,
    actor: str = "founder",
    channel: str = "hub_browser",
) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from form_founder_supremacy_guard_v1 import assert_founder_submit_allowed  # noqa: WPS433

    block = assert_founder_submit_allowed(actor=actor, action="hub_form_submit", channel=channel)
    if block.get("blocked"):
        return block

    if actor.strip().lower() not in ("founder", "asf", "human"):
        return {
            "ok": False,
            "error": "FOUNDER_ACTOR_REQUIRED",
            "law": "INCIDENT-037 — only founder Hub Submit writes §ANSWERED",
        }

    if not overrides or not isinstance(overrides, dict):
        return {
            "ok": False,
            "error": "FOUNDER_PICKS_REQUIRED",
            "law": "INCIDENT-037 — explicit picks map required · recommended is not a pick",
        }

    state = build_founder_picks_state(overrides=overrides)
    if not state["open_count"]:
        from live_founder_decision_form_v1 import payload  # noqa: WPS433

        return {
            "ok": True,
            "mode": "founder_picks",
            "applied_now": 0,
            "message": "Form clear — 0 open rows",
            "open_questions_count": 0,
            "form": payload(),
        }

    if not state["complete"]:
        if not partial_batch or state["count"] < 1:
            return {
                "ok": False,
                "error": "INCOMPLETE_FOUNDER_PICKS",
                "law": "INCIDENT-037 — tap every row before full Submit · or use batch Submit for rows you picked",
                "missing_ids": state["missing_ids"][:20],
                "missing_count": len(state["missing_ids"]),
                "picked_count": state["count"],
                "open_count": state["open_count"],
            }
        # Partial batch — only rows founder explicitly picked (never recommended backfill)
        state["partial_batch"] = True
        state["missing_ids"] = state["missing_ids"]

    if comments and isinstance(comments, dict):
        state["comments"] = {
            str(k): str(v).strip()
            for k, v in comments.items()
            if k in state.get("picks", {}) and str(v).strip()
        }

    canvas_path = _write_canvas_state(state)
    from canvas_form_submit_v1 import submit as form_canvas_submit  # noqa: WPS433
    from live_founder_decision_form_v1 import payload  # noqa: WPS433

    result = form_canvas_submit(cascade_hub=cascade_hub, canvas_data=canvas_path, actor=actor, channel=channel)
    result["mode"] = "founder_picks"
    result["submitted_rows"] = state["rows"]
    result["submitted_count"] = state["count"]
    result["message"] = (
        f"Founder submit — {result.get('applied_now', 0)} shipped · "
        f"{result.get('open_questions_count', '?')} open remaining"
    )
    result["form"] = payload()
    return result


def submit_automatic(
    *,
    overrides: dict | None = None,
    cascade_hub: bool = True,
    actor: str = "agent",
) -> dict:
    """Legacy entry — agents blocked; founders must pass explicit picks map."""
    if actor.strip().lower() not in ("founder", "asf", "human"):
        sys.path.insert(0, str(SCRIPTS))
        from form_founder_supremacy_guard_v1 import assert_founder_submit_allowed  # noqa: WPS433

        block = assert_founder_submit_allowed(actor=actor, action="submit_automatic", channel="cli")
        if block.get("blocked"):
            block["law"] = (
                "INCIDENT-037 — submit_automatic forbidden for agents · "
                "founder must Submit on Hub with explicit picks"
            )
            return block
        return {
            "ok": False,
            "blocked": True,
            "error": "SUBMIT_AUTOMATIC_FORBIDDEN",
            "law": "INCIDENT-037 — agents never bulk-fill from recommended",
        }
    return submit_founder_picks(overrides=overrides, cascade_hub=cascade_hub, actor=actor, channel="hub_browser")


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Hub form founder picks submit")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-state", action="store_true", help="Print founder-picks state only")
    ap.add_argument("--actor", default="founder", choices=("founder", "agent"))
    ap.add_argument("--picks-json", default="", help="JSON map of qid→pick for founder dry-run")
    args = ap.parse_args()

    overrides = None
    if args.picks_json:
        try:
            overrides = json.loads(args.picks_json)
        except json.JSONDecodeError:
            print(json.dumps({"ok": False, "error": "invalid --picks-json"}))
            return 1

    if args.dry_state:
        row = build_founder_picks_state(overrides=overrides)
        row["ok"] = True
    else:
        row = submit_founder_picks(overrides=overrides or {}, actor=args.actor)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("message") or json.dumps(row, indent=2))
    return 0 if row.get("ok", True) and not row.get("blocked") else 1


if __name__ == "__main__":
    raise SystemExit(main())
