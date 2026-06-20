#!/usr/bin/env python3
"""Daily pins for Super Fast Hub — Judge Center + Thread Room (disk-fast, no pipeline on poll)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
JUDGE_DIR = SINA / "judge-center"
THREAD_DIR = SINA / "thread-room"
FORM_JSON = SINA / "live-founder-decision-form-v1.json"

DEFAULT_CHATS = "58148ac9,6245d9dd,e54ddfa8,74f5ccab"
WEEKLY_RUN_SEC = 7 * 86400
DAILY_STRIP_SEC = 86400


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        s = str(ts).replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def _age_sec(ts: str | None) -> float | None:
    dt = _parse_iso(ts)
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds())


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _form_open_count() -> int:
    form = _read_json(FORM_JSON)
    if form.get("open_questions_count") is not None:
        return int(form.get("open_questions_count") or 0)
    return len(form.get("open_questions") or [])


def judge_center_pin(*, rebuild_strip: bool = False) -> dict:
    if rebuild_strip or not (JUDGE_DIR / "latest-alarm-strip-v1.json").is_file():
        try:
            import sys

            root = Path(__file__).resolve().parents[1]
            sys.path.insert(0, str(root / "scripts"))
            from hub_judge_alarm_strip_v1 import write_strip  # noqa: WPS433

            strip = write_strip(refresh_judge=rebuild_strip)
        except Exception as exc:
            strip = {"ok": False, "error": str(exc)}
    else:
        strip = _read_json(JUDGE_DIR / "latest-alarm-strip-v1.json")

    resolution = _read_json(JUDGE_DIR / "latest-resolution-v1.json")
    receipt = _read_json(JUDGE_DIR / "latest-run-receipt-v1.json")
    built_at = strip.get("built_at") or resolution.get("benched_at")
    age = _age_sec(built_at)
    summary = strip.get("summary") or {}

    run_due = age is None or age >= WEEKLY_RUN_SEC
    strip_due = age is None or age >= DAILY_STRIP_SEC

    return {
        "id": "judge-center",
        "label": "Judge Center",
        "cadence": "daily read · weekly run",
        "law": "SINA_JUDGE_STACK_LOCKED_v1.md",
        "headline": strip.get("headline") or "No judge strip yet",
        "tone": strip.get("tone") or "muted",
        "case_id": strip.get("case_id") or resolution.get("case_id"),
        "built_at": built_at,
        "age_sec": round(age, 1) if age is not None else None,
        "active_stale": int(summary.get("active_stale") or 0),
        "bad": int(summary.get("bad") or 0),
        "past_stale_only": int(summary.get("past_stale_only") or 0),
        "form_open": int(summary.get("form_open") or _form_open_count()),
        "p0_count": len((strip.get("levels") or [{}])[0].get("items") or []) if strip.get("levels") else 0,
        "executive_resolution": (strip.get("executive_resolution") or resolution.get("executive_resolution") or "")[:240],
        "run_due": run_due,
        "strip_refresh_due": strip_due,
        "last_run_ok": bool(receipt.get("ok")),
        "default_chats": DEFAULT_CHATS,
    }


def thread_room_pin() -> dict:
    curation = _read_json(THREAD_DIR / "latest-curation-v1.json")
    map_row = _read_json(THREAD_DIR / "latest-map-v1.json")
    receipt = _read_json(THREAD_DIR / "latest-run-receipt-v1.json")
    built_at = curation.get("curated_at") or map_row.get("mapped_at")
    age = _age_sec(built_at)
    arcs = list(map_row.get("arcs") or [])
    drafts = list(curation.get("form_row_drafts") or [])

    return {
        "id": "thread-room",
        "label": "Thread Room",
        "cadence": "weekly run · daily read",
        "law": "SINA_THREAD_ROOM_LOCKED_v1.md",
        "headline": curation.get("executive_summary") or "No thread curation yet",
        "case_id": curation.get("case_id"),
        "built_at": built_at,
        "age_sec": round(age, 1) if age is not None else None,
        "arc_count": len(arcs),
        "thread_drafts": len(drafts),
        "arcs_preview": [
            a.get("thread_id") or a.get("arc_id") or a.get("thread_arc")
            for a in arcs[:5]
            if isinstance(a, dict)
        ],
        "run_due": age is None or age >= WEEKLY_RUN_SEC,
        "last_run_ok": bool(receipt.get("ok")),
        "default_chats": DEFAULT_CHATS,
    }


def loop_judge_room_pin() -> dict:
    jv = _read_json(SINA / "judge-loop" / "latest-verdict-v1.json")
    inv = _read_json(SINA / "loop-health-investigation-receipt-v1.json")
    spec = _read_json(SINA / "loop-specialist-tick-receipt-v1.json")
    built_at = jv.get("at") or inv.get("at")
    age = _age_sec(built_at)
    return {
        "id": "loop-judge-room",
        "label": "Judge Loop Room",
        "cadence": "every live wire sync · session gate",
        "law": "docs/SOURCEA_INVESTIGATOR_JUDGE_LOOP_ROOM_LOCKED_v1.md",
        "headline": jv.get("judge_loop_line") or "No loop judge verdict yet",
        "loop_verdict": jv.get("loop_verdict"),
        "investigation_verdict": inv.get("investigation_verdict"),
        "tick_decision": spec.get("tick_decision"),
        "built_at": built_at,
        "age_sec": round(age, 1) if age is not None else None,
        "escalations": jv.get("escalations") or [],
        "hub_api": "POST /api/judge-loop/tick/v1",
    }


def daily_rooms_payload(*, rebuild_judge_strip: bool = False) -> dict:
    judge = judge_center_pin(rebuild_strip=rebuild_judge_strip)
    thread = thread_room_pin()
    loop_judge = loop_judge_room_pin()
    form_open = _form_open_count()
    any_p0 = judge.get("active_stale", 0) > 0 or judge.get("bad", 0) > 0
    return {
        "schema": "worker-hub-daily-rooms-v1",
        "built_at": _now(),
        "form_open": form_open,
        "needs_founder": any_p0 or form_open > 0,
        "judge_center": judge,
        "thread_room": thread,
        "loop_judge_room": loop_judge,
        "actions": {
            "run_judge": {"path": "/api/worker-hub/rooms/run", "body": {"room": "judge"}},
            "run_thread": {"path": "/api/worker-hub/rooms/run", "body": {"room": "thread"}},
            "run_both": {"path": "/api/worker-hub/rooms/run", "body": {"room": "both"}},
            "refresh_strip": {"path": "/api/worker-hub/rooms/run", "body": {"room": "strip"}},
            "loop_chain_tick": {"path": "/api/loop-chain/tick/v1", "method": "POST", "body": {}},
        },
    }


def run_rooms(*, room: str = "both", chats: str | None = None) -> dict:
    """Run Judge / Thread / strip refresh (founder one-tap — not Terminal)."""
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[1]
    py = sys.executable
    chat_list = chats or DEFAULT_CHATS
    steps: list[dict] = []
    ok = True

    if room in ("strip", "both", "judge"):
        try:
            from hub_judge_alarm_strip_v1 import write_strip  # noqa: WPS433

            row = write_strip(refresh_judge=(room in ("both", "judge")))
            steps.append({"step": "judge_strip", "ok": True, "headline": row.get("headline")})
        except Exception as exc:
            ok = False
            steps.append({"step": "judge_strip", "ok": False, "error": str(exc)})

    if room in ("both", "judge"):
        try:
            proc = subprocess.run(
                [py, str(root / "scripts" / "judge_center_run_v1.py"), "--chats", chat_list, "--json"],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=300,
            )
            steps.append({"step": "judge_run", "ok": proc.returncode == 0, "tail": (proc.stdout or proc.stderr)[-200:]})
            ok = ok and proc.returncode == 0
            if proc.returncode == 0:
                from hub_judge_alarm_strip_v1 import write_strip  # noqa: WPS433

                write_strip(refresh_judge=False)
                steps.append({"step": "judge_strip_after_run", "ok": True})
        except Exception as exc:
            ok = False
            steps.append({"step": "judge_run", "ok": False, "error": str(exc)})

    if room in ("both", "thread"):
        try:
            proc = subprocess.run(
                [py, str(root / "scripts" / "thread_room_run_v1.py"), "--chats", chat_list, "--json"],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=300,
            )
            steps.append({"step": "thread_run", "ok": proc.returncode == 0, "tail": (proc.stdout or proc.stderr)[-200:]})
            ok = ok and proc.returncode == 0
        except Exception as exc:
            ok = False
            steps.append({"step": "thread_run", "ok": False, "error": str(exc)})

    from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

    invalidate_worker_hub_cache()
    pins = daily_rooms_payload()
    return {
        "ok": ok,
        "schema": "worker-hub-rooms-run-v1",
        "room": room,
        "chats": chat_list,
        "steps": steps,
        "daily_rooms": pins,
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Worker hub daily rooms")
    p.add_argument("--json", action="store_true")
    p.add_argument("--rebuild-strip", action="store_true")
    p.add_argument("--run", choices=("judge", "thread", "both", "strip"))
    args = p.parse_args()
    if args.run:
        row = run_rooms(room=args.run)
    else:
        row = daily_rooms_payload(rebuild_judge_strip=args.rebuild_strip)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        if args.run:
            print(f"ROOMS RUN: ok={row.get('ok')} room={args.run}")
        else:
            j = row.get("judge_center") or {}
            t = row.get("thread_room") or {}
            print(f"DAILY: judge={j.get('headline')} thread_arcs={t.get('arc_count')}")
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
