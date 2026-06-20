#!/usr/bin/env python3
"""Factory control plane — mode · stop/resume · spawn gate · factory-now (one module)."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"

KILL_FLAG = SINA / "auto-run-disabled-v1.flag"
STOP_RECEIPT = SINA / "founder-stop-receipt-v1.json"
RESUME_TOKEN = SINA / "founder-resume-drain-v1.json"
MODE_PATH = SINA / "factory-mode-v1.json"
NOW_PATH = SINA / "factory-now-v1.json"
POISON_STALL = SINA / "poison-stall-v1.json"

DRAIN_MODES = frozenset({"SINGLE_SA", "FORGE_FACTORY"})
VALID_MODES = frozenset({"FREEZE", "AUDIT", "SINGLE_SA", "SHIP_MAINTAINER", "FORGE_FACTORY"})

_STOP_PATTERNS = (r"\bstop\b", r"\bhalt\b", r"stop all", r"why stuck", r"\binterrupt\b", r"freeze")
_RESUME_PATTERNS = (r"ASF:\s*resume drain", r"resume healthy drain", r"resume drain")

_GATE_TTL_SEC = 2.0
_NOW_TTL_SEC = 5.0
_gate_cache: dict[str, Any] = {"at": 0.0, "row": None}
_now_cache: dict[str, Any] = {"at": 0.0, "row": None}


def _scripts_path() -> None:
    p = str(SCRIPTS)
    if p not in sys.path:
        sys.path.insert(0, p)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write(path: Path, row: dict) -> None:
    """Write JSON atomically — pid-scoped temp + retry (hub concurrent load_factory_now)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, indent=2) + "\n"
    last_err: OSError | None = None
    for attempt in range(8):
        tmp = path.with_name(f"{path.stem}.{os.getpid()}.{attempt}.tmp")
        try:
            tmp.write_text(payload, encoding="utf-8")
            os.replace(tmp, path)
            return
        except OSError as exc:
            last_err = exc
            try:
                if tmp.is_file():
                    tmp.unlink()
            except OSError:
                pass
            time.sleep(0.015 * (attempt + 1))
    try:
        path.write_text(payload, encoding="utf-8")
    except OSError as exc:
        raise exc if last_err is None else last_err from exc


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# --- founder message class (inline — no extra module) ---

def classify_founder_message(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return "ASF_QUESTION"
    low = t.lower()
    if re.search(r"EDIT ALLOWED:", t, re.I):
        return "EDIT_ALLOWED"
    for pat in _RESUME_PATTERNS:
        if re.search(pat, t, re.I):
            return "ASF_RESUME"
    for pat in _STOP_PATTERNS:
        if re.search(pat, low, re.I):
            return "ASF_STOP"
    if re.search(r"\bwhy\b|what happened", low):
        return "ASF_QUESTION"
    return "ASF_ORDER"


# --- mode ---

def current_mode() -> str:
    row = _read_json(MODE_PATH)
    if not row:
        return "FREEZE"
    mode = str(row.get("mode") or "FREEZE")
    return mode if mode in VALID_MODES else "FREEZE"


def _set_mode_file(mode: str, *, set_by: str, reason: str = "") -> dict:
    row = {
        "schema": "factory-mode-v1",
        "mode": mode,
        "since": _now(),
        "set_by": set_by,
        "reason": reason,
    }
    _atomic_write(MODE_PATH, row)
    return row


def freeze(*, set_by: str, reason: str = "ASF_STOP") -> dict:
    row = {"ok": True, **_set_mode_file("FREEZE", set_by=set_by, reason=reason)}
    KILL_FLAG.touch()
    rebuild_factory_now(caller="freeze", force=True)
    return row


def allow_single_sa(*, set_by: str, reason: str = "ASF_RESUME") -> dict:
    return {"ok": True, **_set_mode_file("SINGLE_SA", set_by=set_by, reason=reason)}


# --- stop / resume ---

def load_stop_receipt() -> dict | None:
    return _read_json(STOP_RECEIPT)


def stop_receipt_open() -> bool:
    row = load_stop_receipt()
    return bool(row and not row.get("cleared_by_asf"))


def load_resume_token() -> dict | None:
    row = _read_json(RESUME_TOKEN)
    if not row or row.get("schema") != "founder-resume-drain-v1":
        return None
    expires = row.get("expires_at")
    if expires:
        try:
            exp = datetime.fromisoformat(str(expires).replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > exp:
                return None
        except ValueError:
            return None
    return row


def write_stop_receipt(*, trigger: str, set_by: str = "stop_goal1_auto_run") -> dict:
    row = {
        "schema": "founder-stop-receipt-v1",
        "at": _now(),
        "trigger": trigger,
        "cleared_by_asf": False,
        "cleared_at": None,
        "set_by": set_by,
        "law": "ASF_ORDER > plan todo",
    }
    _atomic_write(STOP_RECEIPT, row)
    KILL_FLAG.touch()
    _set_mode_file("FREEZE", set_by=set_by, reason=trigger)
    _invalidate_caches()
    rebuild_factory_now(caller="stop_receipt", force=True)
    hub_sync: dict = {}
    try:
        from hub_projection_sync_v1 import sync_hub_projection  # noqa: WPS433

        hub_sync = sync_hub_projection(caller="stop_receipt")
    except Exception as exc:
        hub_sync = {"ok": False, "error": str(exc)}
    return {"ok": True, "hub_projection_sync": hub_sync, **row}


def write_resume_token(
    *,
    max_turns: int = 1,
    max_packs: int = 1,
    trigger: str = "ASF: resume drain",
    ttl_minutes: int = 30,
    set_by: str = "founder_resume_drain",
) -> dict:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    row = {
        "schema": "founder-resume-drain-v1",
        "at": _now(),
        "trigger": trigger,
        "max_turns": max(1, int(max_turns)),
        "max_packs": max(1, int(max_packs)),
        "expires_at": expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "set_by": set_by,
        "law": "bounded resume only — receipt required",
    }
    _atomic_write(RESUME_TOKEN, row)
    stop_row = _read_json(STOP_RECEIPT) or {"schema": "founder-stop-receipt-v1"}
    stop_row.update({"cleared_by_asf": True, "cleared_at": _now(), "cleared_by": set_by})
    _atomic_write(STOP_RECEIPT, stop_row)
    KILL_FLAG.unlink(missing_ok=True)
    _set_mode_file("SINGLE_SA", set_by=set_by, reason=trigger)
    _invalidate_caches()
    rebuild_factory_now(caller="resume_token", force=True)
    hub_sync: dict = {}
    try:
        from hub_projection_sync_v1 import sync_hub_projection  # noqa: WPS433

        hub_sync = sync_hub_projection(caller="resume_token")
    except Exception as exc:
        hub_sync = {"ok": False, "error": str(exc)}
    return {"ok": True, "hub_projection_sync": hub_sync, **row}


# --- factory-now ---

def format_line(row: dict | None = None) -> str:
    r = row or load_factory_now()
    era = _load_factory_era()
    if era.get("current_era") == "forge_factory_cycle2":
        return (
            f"factory-now · FORGE FACTORY · cycle2 · "
            f"mode {r.get('mode', '?')} · "
            f"queue {r.get('queue_sa', '?')}"
        )
    return (
        f"factory-now · Valid YES {r.get('valid_yes', '?')} · "
        f"brain {r.get('brain_vy', '?')} · "
        f"dual_proof {r.get('dual_proof_ok', '?')} · "
        f"mode {r.get('mode', '?')} · "
        f"queue {r.get('queue_sa', '?')}"
    )


def _load_factory_era() -> dict:
    for path in (SINA / "factory-era-v1.json", ROOT / "data" / "factory-era-v1.json"):
        row = _read_json(path)
        if row.get("schema") == "factory-era-v1":
            return row
    return {}


def load_factory_now(*, max_age_sec: float = _NOW_TTL_SEC) -> dict:
    global _now_cache
    age = time.monotonic() - float(_now_cache.get("at") or 0)
    cached = _now_cache.get("row")
    if cached and age < max_age_sec:
        return cached
    row = _read_json(NOW_PATH)
    if row and row.get("schema") == "factory-now-v1":
        file_at = row.get("at")
        if file_at:
            try:
                written = datetime.fromisoformat(str(file_at).replace("Z", "+00:00"))
                file_age = (datetime.now(timezone.utc) - written).total_seconds()
                if file_age < max_age_sec:
                    _now_cache = {"at": time.monotonic(), "row": row}
                    return row
                row["_k1_stale"] = True
                row["_k1_age_sec"] = round(file_age, 1)
            except ValueError:
                pass
    return rebuild_factory_now(caller="load", force=True)


def rebuild_factory_now(*, caller: str = "rebuild", force: bool = False) -> dict:
    global _now_cache
    if not force:
        age = time.monotonic() - float(_now_cache.get("at") or 0)
        if _now_cache.get("row") and age < _NOW_TTL_SEC:
            return _now_cache["row"]

    _scripts_path()
    valid_yes = brain_vy = 0
    dual_proof_ok = False
    try:
        from monitor_honesty_lib_v1 import audit_monitor, load_dual_proof_system  # noqa: WPS433

        m = audit_monitor(filter_mode="road")
        prog = m.get("progress") or {}
        valid_yes = int(prog.get("valid_yes") or 0)
        hy_ok = bool(m.get("ok")) and int(m.get("unproven_done") or 0) == 0
        dual = load_dual_proof_system(valid_yes=valid_yes, hygiene_ok=hy_ok)
        brain_vy = int((dual.get("brain") or {}).get("valid_yes") or 0)
        dual_proof_ok = bool(dual.get("dual_proof_ok"))
    except Exception:
        pass

    queue_sa = inbox_sa = ""
    try:
        from queue_ssot_unify_v1 import queue_head  # noqa: WPS433

        head = queue_head()
        if head.get("queue_exhausted") and not head.get("sa_id"):
            queue_sa = ""
            inbox_sa = ""
        else:
            queue_sa = str(head.get("sa_id") or "")
    except Exception:
        pass
    if not queue_sa:
        try:
            from healthy_pack_bind_lib_v1 import bind_status  # noqa: WPS433

            bs = bind_status()
            queue_sa = str(bs.get("queue_sa") or "")
            inbox_sa = str(bs.get("inbox_sa") or "")
        except Exception:
            pass
    elif not inbox_sa:
        try:
            from healthy_pack_bind_lib_v1 import bind_status  # noqa: WPS433

            inbox_sa = str(bind_status().get("inbox_sa") or "")
        except Exception:
            pass

    row = {
        "schema": "factory-now-v1",
        "at": _now(),
        "era": (_load_factory_era().get("current_era") or ""),
        "brand": (_load_factory_era().get("current_brand") or ""),
        "valid_yes": valid_yes,
        "valid_yes_note": "archived_goal1_bootstrap" if _load_factory_era().get("current_era") == "forge_factory_cycle2" else "",
        "backlog": max(0, 1000 - valid_yes),
        "brain_vy": brain_vy,
        "dual_proof_ok": dual_proof_ok,
        "mode": current_mode(),
        "kill_flag": KILL_FLAG.is_file(),
        "stop_receipt_open": stop_receipt_open(),
        "queue_sa": queue_sa,
        "inbox_sa": inbox_sa,
        "orchestrator_status": "idle",
        "broker_status": "idle",
        "poison_stall": POISON_STALL.is_file(),
        "rebuilt_by": caller,
        "law": "cite this line only in chat",
    }
    row["line"] = format_line(row)
    _atomic_write(NOW_PATH, row)
    _now_cache = {"at": time.monotonic(), "row": row}
    _sync_active_now_from_factory_now()
    try:
        from sync_sourcea_priority_machine_truth_v1 import sync_priority_machine_truth  # noqa: WPS433

        sync_priority_machine_truth()
    except Exception:
        pass
    return row


def _sync_active_now_from_factory_now() -> None:
    try:
        sync_script = Path(__file__).resolve().parent / "active_now_sync_from_factory_now_v1.py"
        if sync_script.is_file():
            subprocess.run(
                [sys.executable, str(sync_script), "--json"],
                cwd=str(Path(__file__).resolve().parents[1]),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
    except Exception:
        pass


def _invalidate_caches() -> None:
    global _gate_cache, _now_cache
    _gate_cache = {"at": 0.0, "row": None}
    _now_cache = {"at": 0.0, "row": None}


# --- spawn gate ---

def _blocked(*, reason: str, action: str, caller: str, extra: dict | None = None) -> dict:
    row = {
        "ok": False,
        "blocked": True,
        "reason": reason,
        "action": action,
        "caller": caller,
        "law": "ASF_ORDER > plan todo · FREEZE default",
    }
    if extra:
        row.update(extra)
    return row


def _gate_inputs() -> dict:
    global _gate_cache
    age = time.monotonic() - float(_gate_cache.get("at") or 0)
    if _gate_cache.get("row") and age < _GATE_TTL_SEC:
        return _gate_cache["row"]

    stall = _read_json(POISON_STALL)
    row = {
        "kill_flag": KILL_FLAG.is_file(),
        "resume": load_resume_token(),
        "stop_open": stop_receipt_open(),
        "mode": current_mode(),
        "stall": stall if stall and stall.get("auto_resume_forbidden") else None,
    }
    _gate_cache = {"at": time.monotonic(), "row": row}
    return row


def drain_spawn_allowed(*, caller: str, require_bind: bool = True) -> dict:
    try:
        from mac_control_plane_v1 import spawn_blocked_on_mac  # noqa: WPS433

        cp = spawn_blocked_on_mac(caller=caller)
        if cp.get("blocked"):
            return cp
    except Exception:
        pass

    g = _gate_inputs()
    resume = g["resume"]
    if g["stall"]:
        return _blocked(
            reason="poison_stall",
            action="Heal bind/sa_mismatch + ASF clear before resume",
            caller=caller,
            extra={"stall": g["stall"]},
        )
    if g["stop_open"] and not resume:
        return _blocked(
            reason="stop_receipt_open",
            action="ASF: resume drain — max N — receipt required",
            caller=caller,
        )
    if g["kill_flag"] and not resume:
        return _blocked(reason="kill_flag", action="Hub Stop or ASF: resume drain", caller=caller)
    if g["mode"] not in DRAIN_MODES and not resume:
        return _blocked(
            reason=f"factory_mode_{g['mode'].lower()}",
            action="ASF: resume drain — max 1 — receipt required",
            caller=caller,
            extra={"mode": g["mode"]},
        )
    if require_bind:
        _scripts_path()
        try:
            from healthy_pack_bind_lib_v1 import bind_status  # noqa: WPS433

            bs = bind_status()
            if bs.get("queue_sa") and not bs.get("match"):
                return _blocked(
                    reason="bind_mismatch",
                    action="Run heal_bind_mismatch or Hub Refresh before drain",
                    caller=caller,
                    extra={"bind": bs},
                )
        except Exception:
            pass
    return {
        "ok": True,
        "blocked": False,
        "caller": caller,
        "kill_flag": g["kill_flag"],
        "resume_token": bool(resume),
        "stop_receipt_open": g["stop_open"],
    }


def exit_if_spawn_blocked(
    caller: str,
    *,
    json_mode: bool = False,
    require_bind: bool = True,
) -> None:
    gate = drain_spawn_allowed(caller=caller, require_bind=require_bind)
    if gate.get("ok"):
        return
    if json_mode:
        print(json.dumps(gate, indent=2))
    else:
        print(
            f"SPAWN_BLOCKED reason={gate.get('reason')} action={gate.get('action')}",
            file=sys.stderr,
        )
    raise SystemExit(1)


def turn_allowed(*, caller: str) -> dict:
    g = _gate_inputs()
    if g["kill_flag"] and not g["resume"]:
        return _blocked(reason="kill_flag", action="STOPPED_BY_FLAG", caller=caller)
    if g["stall"]:
        return _blocked(reason="poison_stall", action="STOPPED_BY_POISON", caller=caller)
    return {"ok": True, "caller": caller}


def kill_flag_active() -> bool:
    return KILL_FLAG.is_file()


def clear_poison_stall(*, set_by: str = "ASF") -> dict:
    POISON_STALL.unlink(missing_ok=True)
    _invalidate_caches()
    return {"ok": True, "cleared_by": set_by}


def write_poison_stall(*, class_name: str, expected_sa: str = "", queue_sa: str = "") -> dict:
    row = {
        "schema": "poison-stall-v1",
        "class": class_name,
        "at": _now(),
        "expected_sa": expected_sa,
        "queue_sa": queue_sa,
        "heal_required": True,
        "auto_resume_forbidden": True,
    }
    _atomic_write(POISON_STALL, row)
    KILL_FLAG.touch()
    _set_mode_file("FREEZE", set_by="poison_stall", reason=class_name)
    _invalidate_caches()
    rebuild_factory_now(caller="poison_stall", force=True)
    return {"ok": True, **row}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="factory control plane")
    p.add_argument("cmd", nargs="?", default="now", choices=("now", "gate", "stop", "resume", "classify"))
    p.add_argument("--caller", default="cli")
    p.add_argument("--trigger", default="cli")
    p.add_argument("--max-turns", type=int, default=1)
    p.add_argument("--text", default="")
    p.add_argument("--rebuild", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--line", action="store_true", help="print factory-now line only (logs)")
    args = p.parse_args()

    if args.cmd == "now":
        out = rebuild_factory_now(caller="cli", force=args.rebuild) if args.rebuild else load_factory_now()
        if args.line:
            print(out.get("line") or format_line(out))
            return 0
    elif args.cmd == "gate":
        out = drain_spawn_allowed(caller=args.caller)
    elif args.cmd == "stop":
        out = write_stop_receipt(trigger=args.trigger)
    elif args.cmd == "resume":
        out = write_resume_token(max_turns=args.max_turns, trigger=args.trigger)
    else:
        out = {"class": classify_founder_message(args.text)}
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
