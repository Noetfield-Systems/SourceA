#!/usr/bin/env python3
"""ACTIVE_NOW.md — ecosystem heartbeat. Every agent/script reads this first.

Law: brain-os/laws/ACTIVE_NOW_HEARTBEAT_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

def _source_a_root() -> Path:
    import os

    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[1]


ROOT = _source_a_root()
ACTIVE_NOW = ROOT / "ACTIVE_NOW.md"
HEARTBEAT_LOG = Path.home() / ".sina" / "active-now-heartbeat-v1.jsonl"
RECEIPT = Path.home() / ".sina" / "active-now-receipt-v1.json"

FIELD_RE = re.compile(r"^\*\*Current ([^*]+):\*\*\s*(.+?)\s*$", re.M)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_active_now() -> dict:
    if not ACTIVE_NOW.is_file():
        return {"ok": False, "error": "ACTIVE_NOW_MISSING", "path": str(ACTIVE_NOW)}
    text = ACTIVE_NOW.read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    for m in FIELD_RE.finditer(text):
        key = m.group(1).strip().lower().replace(" ", "_")
        fields[key] = m.group(2).strip()
    if not fields:
        return {"ok": False, "error": "ACTIVE_NOW_PARSE_EMPTY", "path": str(ACTIVE_NOW)}
    sa_raw = fields.get("sa_id", "")
    sa_m = re.search(r"(sa-\d+)", sa_raw, re.I)
    queue_m = re.search(r"(\d+)\s*/\s*(\d+)", sa_raw)
    autorun_off = "auto-run **off**" in text.lower() or "autorun **off**" in text.lower()
    mode_raw = fields.get("founder_mode", fields.get("mode", "")).lower()
    if "absent" in mode_raw:
        founder_mode = "founder_absent"
    else:
        founder_mode = "founder_busy"
    if "autorun off" in mode_raw or "auto-run off" in mode_raw:
        autorun_off = True
    sleep_raw = (fields.get("sleep_escalation") or "off").lower()
    sleep_escalation = sleep_raw.strip("`").startswith("on")
    cost_policy = fields.get("cost_policy", "cost_smart_default")
    return {
        "ok": True,
        "path": str(ACTIVE_NOW),
        "hash8": hashlib.sha256(text.encode()).hexdigest()[:8],
        "fields": fields,
        "current_goal": fields.get("goal", ""),
        "current_sprint": fields.get("sprint", ""),
        "current_queue": fields.get("queue", ""),
        "current_sa_id": sa_m.group(1).lower() if sa_m else "",
        "queue_pos": int(queue_m.group(1)) if queue_m else None,
        "queue_total": int(queue_m.group(2)) if queue_m else None,
        "current_blocker": fields.get("blocker", ""),
        "founder_mode": founder_mode,
        "sleep_escalation": sleep_escalation,
        "cost_policy": cost_policy,
        "autorun_off": autorun_off,
        "forbidden_footer": "everything else is forbidden" in text.lower(),
    }


def _log_heartbeat(*, caller: str, row: dict) -> None:
    HEARTBEAT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "at": _now(),
        "caller": caller,
        "hash8": row.get("hash8"),
        "current_sa_id": row.get("current_sa_id"),
        "current_goal": row.get("current_goal"),
        "autorun_off": row.get("autorun_off"),
    }
    with HEARTBEAT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    RECEIPT.write_text(json.dumps({**row, "caller": caller, "read_at": _now()}, indent=2) + "\n", encoding="utf-8")


def heartbeat(
    *,
    caller: str,
    enforce: bool = True,
    task_text: str = "",
    sa_id: str = "",
    phase: str = "",
) -> dict:
    """Mandatory first read — log + return parsed ACTIVE_NOW."""
    row = load_active_now()
    if not row.get("ok"):
        return {**row, "caller": caller, "heartbeat": False}
    _log_heartbeat(caller=caller, row=row)
    out = {**row, "caller": caller, "heartbeat": True}
    if enforce:
        from execution_law_enforce_v1 import validate_execution  # noqa: WPS433

        law = validate_execution(
            task_text=task_text,
            sa_id=sa_id if sa_id else "",
            phase=phase,
            caller=caller,
        )
        out["execution_law"] = law
        if not law.get("allowed"):
            out["ok"] = False
            out["heartbeat"] = False
            out["message"] = law.get("message")
    return out


def check_autorun_allowed(*, caller: str = "autorun") -> dict:
    row = heartbeat(caller=caller)
    if not row.get("ok"):
        return row
    if row.get("autorun_off") or (Path.home() / ".sina/auto-run-disabled-v1.flag").is_file():
        return {
            "ok": False,
            "action": "skip",
            "reason": "ACTIVE_NOW_AUTORUN_OFF",
            "active_now": row,
        }
    return {"ok": True, "active_now": row}


def sync_active_now_from_queue_head() -> dict:
    """Align ACTIVE_NOW with healthy-queue state head (gatekeeper queue SSOT)."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from healthy_queue_ssot_lib import (  # noqa: WPS433
        healthy_queue_state_path,
        load_healthy_queue,
        queue_items,
    )

    try:
        _, data = load_healthy_queue()
        items = queue_items(data)
        pos = 1
        sp = healthy_queue_state_path()
        if sp.is_file():
            pos = int(json.loads(sp.read_text(encoding="utf-8")).get("next_pos") or 1)
        pos = max(1, min(pos, len(items) or 1))
        item = items[pos - 1] if items else {}
        return sync_active_now_from_queue(
            pointer={
                "next_sa": item.get("sa_id"),
                "queue_role": item.get("queue_role"),
                "queue_pos": pos,
            }
        )
    except (OSError, json.JSONDecodeError, ValueError, TypeError, FileNotFoundError) as exc:
        return {"ok": False, "error": str(exc)}


def sync_active_now_from_queue(*, pointer: dict | None = None) -> dict:
    """Align ACTIVE_NOW.md sa_id + queue lines with pointer / healthy-queue SSOT."""
    ptr = pointer
    if ptr is None:
        ptr_path = Path.home() / ".sina" / "next-execution-pointer-v1.json"
        if not ptr_path.is_file():
            return {"ok": False, "error": "POINTER_MISSING"}
        try:
            ptr = json.loads(ptr_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"ok": False, "error": "POINTER_PARSE"}
    sa_id = str(ptr.get("next_sa") or "")
    if not sa_id.startswith("sa-"):
        return {"ok": False, "error": "POINTER_NO_SA"}
    role = str(ptr.get("queue_role") or "check").lower()
    pos = ptr.get("queue_pos")
    total = 30
    sa_range: list[str] = []
    queue_phase = ""
    queue_path = Path.home() / ".sina" / "healthy-queue-30-active.json"
    if queue_path.is_file():
        try:
            q = json.loads(queue_path.read_text(encoding="utf-8"))
            total = int(q.get("count") or len(q.get("queue") or []) or 30)
            sr = q.get("sa_range") or []
            if isinstance(sr, list) and len(sr) == 2:
                sa_range = [str(sr[0]), str(sr[1])]
            items = q.get("queue") or []
            if items:
                queue_phase = str(items[0].get("phase") or "").strip()
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            pass
    if pos is None:
        state_path = Path.home() / ".sina" / "healthy-queue-state-v1.json"
        if state_path.is_file():
            try:
                pos = int(json.loads(state_path.read_text()).get("next_pos") or 1)
            except (OSError, json.JSONDecodeError, ValueError, TypeError):
                pos = 1
    if not ACTIVE_NOW.is_file():
        return {"ok": False, "error": "ACTIVE_NOW_MISSING"}
    text = ACTIVE_NOW.read_text(encoding="utf-8")
    text = re.sub(
        r"\*\*Current sa_id:\*\*[^\n]*",
        f"**Current sa_id:** `{sa_id}` · `{role}` · pos `{pos}/{total}`",
        text,
        count=1,
    )
    if sa_range:
        phase_label = queue_phase or "phase-s1-eval-dispatch"
        text = re.sub(
            r"\*\*Current Queue:\*\*[^\n]*",
            (
                "**Current Queue:** `~/.sina/healthy-queue-30-active.json` · "
                f"`{phase_label}` · `{sa_range[0]}`–`{sa_range[1]}` · pack 2"
            ),
            text,
            count=1,
        )
    sina = Path.home() / ".sina"
    kill_flag = (sina / "auto-run-disabled-v1.flag").is_file()
    sleep_line = re.search(r"\*\*Current Sleep Escalation:\*\*[^\n]*", text)
    sleep_on = bool(sleep_line and "`on`" in sleep_line.group(0).lower())
    fn_line = ""
    try:
        from factory_control_v1 import load_factory_now  # noqa: WPS433

        fn = load_factory_now()
        fn_line = str(fn.get("line") or "").strip()
    except Exception:
        pass
    if kill_flag:
        base = "FREEZE — engines off · autorun kill flag ON · Worker INBOX ready"
        blocker = f"{base} · `{fn_line}`" if fn_line else base
    elif sleep_on and "absent" in text.lower():
        blocker = "none — overnight dispatcher armed"
    else:
        base = "none — Worker paste lane ready"
        blocker = f"{base} · `{fn_line}`" if fn_line else base
    text = re.sub(
        r"\*\*Current Blocker:\*\*[^\n]*",
        f"**Current Blocker:** {blocker}",
        text,
        count=1,
    )
    ACTIVE_NOW.write_text(text, encoding="utf-8")
    row = load_active_now()
    return {
        "ok": True,
        "sa_id": sa_id,
        "queue_role": role,
        "queue_pos": pos,
        "queue_total": total,
        "hash8": row.get("hash8"),
    }


def check_queue_path(path: Path) -> dict:
    """Warn if script uses a queue file that disagrees with ACTIVE_NOW."""
    row = load_active_now()
    if not row.get("ok"):
        return row
    expected = row.get("current_queue", "")
    path_s = str(path.resolve())
    home_q = str((Path.home() / ".sina/healthy-queue-30-active.json").resolve())
    if "~/.sina" in expected or "healthy-queue-30-active" in expected:
        if path_s != home_q and "commercial" in path_s.lower():
            return {
                "ok": False,
                "error": "ACTIVE_NOW_QUEUE_MISMATCH",
                "expected": home_q,
                "got": path_s,
                "law": "ACTIVE_NOW.md",
            }
    return {"ok": True}


def main() -> int:
    p = argparse.ArgumentParser(description="ACTIVE_NOW.md ecosystem heartbeat")
    p.add_argument("--heartbeat", action="store_true", help="Read first + log (mandatory)")
    p.add_argument("--caller", default="cli")
    p.add_argument("--check-autorun", action="store_true")
    p.add_argument("--show", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.check_autorun:
        row = check_autorun_allowed(caller=args.caller)
    elif args.heartbeat:
        row = heartbeat(caller=args.caller)
        if not row.get("heartbeat"):
            print(json.dumps(row, indent=2), file=sys.stderr)
            return 1
        if not args.json:
            print(f"ACTIVE_NOW_HEARTBEAT ok hash8={row.get('hash8')} sa={row.get('current_sa_id')} caller={args.caller}")
    else:
        row = load_active_now()

    if args.json or args.show:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
