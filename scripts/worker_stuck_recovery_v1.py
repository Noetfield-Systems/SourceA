#!/usr/bin/env python3
"""Permanent Worker stuck recovery — kill hung validators, heal stale turns, replay INBOX.

Law: founder taps Hub **Unstick Worker** — never Terminal.
Executor may run on pickup, poll, and stop_goal1_loop.
"""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LOG = Path.home() / ".sina" / "worker-stuck-recovery-v1.jsonl"
ORCH_PATH = Path.home() / ".sina" / "healthy-drain-orchestrator-v1.json"
INBOX_JSON = Path.home() / ".sina" / "worker-prompt-inbox-v1.json"
ROUND_REPORT = Path.home() / ".sina" / "worker_round_report_v1.json"

HUNG_MARKERS = (
    "find_critical_bugs.py",
    "build-sina-command-panel.py",
    "validate-sourcea-e2e-full",
    "brain_execute_turn_v1.py",
    "goal1_worker_batch_loop_v1.py",
    "auto_run_worker_batch_v1.py",
)
DEFAULT_HUNG_AGE_SEC = 180
STALE_INBOX_SEC = 900
STALE_TURN_SEC = 600


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _parse_etime(etime: str) -> int | None:
    etime = (etime or "").strip()
    if not etime:
        return None
    if re.match(r"^\d+:\d{2}$", etime):
        m, s = etime.split(":")
        return int(m) * 60 + int(s)
    if re.match(r"^\d+:\d{2}:\d{2}$", etime):
        h, m, s = etime.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)
    if "-" in etime:
        day_part, rest = etime.split("-", 1)
        try:
            days = int(day_part)
        except ValueError:
            return None
        if rest.count(":") == 2:
            h, m, s = rest.split(":")
            return days * 86400 + int(h) * 3600 + int(m) * 60 + int(s)
        if rest.count(":") == 1:
            m, s = rest.split(":")
            return days * 86400 + int(m) * 60 + int(s)
    return None


def kill_hung_processes(*, max_age_sec: int = DEFAULT_HUNG_AGE_SEC) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from factory_validation_lock_v1 import protected_validation_pids  # noqa: WPS433

    protected = protected_validation_pids()
    proc = subprocess.run(
        ["ps", "-axo", "pid=,etime=,command="],
        capture_output=True,
        text=True,
        timeout=15,
    )
    killed: list[dict] = []
    skipped: list[dict] = []
    for line in (proc.stdout or "").splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) < 3:
            continue
        pid_s, etime, cmd = parts[0], parts[1], parts[2]
        if not any(m in cmd for m in HUNG_MARKERS):
            continue
        age = _parse_etime(etime)
        if age is None or age < max_age_sec:
            continue
        try:
            pid = int(pid_s)
        except ValueError:
            continue
        if pid in protected:
            skipped.append({"pid": pid, "age_sec": age, "reason": "factory_validation_lock"})
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append({"pid": pid, "age_sec": age, "cmd": cmd[:160]})
        except OSError:
            continue
    return {
        "ok": True,
        "killed": killed,
        "count": len(killed),
        "skipped_protected": skipped,
        "protected_pids": sorted(protected),
    }


def heal_stale_worker_turn(*, inbox_sa: str = "") -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from worker_turn_lib import close_turn, turn_open_block, turn_state  # noqa: WPS433

    block = turn_open_block()
    if not block:
        return {"healed": False, "reason": "no_open_turn"}

    open_sa = str(block.get("open_sa") or "")
    opened_at = str((turn_state() or {}).get("opened_at") or "")
    age_sec = None
    if opened_at:
        try:
            dt = datetime.fromisoformat(opened_at.replace("Z", "+00:00"))
            age_sec = int((datetime.now(timezone.utc) - dt).total_seconds())
        except ValueError:
            pass

    report = {}
    if ROUND_REPORT.is_file():
        try:
            report = json.loads(ROUND_REPORT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            report = {}

    if inbox_sa and open_sa == inbox_sa:
        return {"healed": False, "reason": "same_sa_ok", "open_sa": open_sa}

    if report.get("turn_closed") and str(report.get("sa_focus") or "") == open_sa:
        close_turn(sa_id=open_sa, force=True)
        return {"healed": True, "reason": "report_closed", "closed_sa": open_sa}

    if age_sec is not None and age_sec >= STALE_TURN_SEC:
        close_turn(sa_id=open_sa, force=True)
        return {"healed": True, "reason": "stale_turn_timeout", "closed_sa": open_sa, "age_sec": age_sec}

    return {"healed": False, "reason": "turn_still_active", "open_sa": open_sa, "age_sec": age_sec}


def heal_orchestrator_inbox_drift() -> dict:
    """When INBOX pending but orchestrator idle — align expected_sa/role (replay/reset drift)."""
    if not ORCH_PATH.is_file() or not INBOX_JSON.is_file():
        return {"ok": False, "error": "missing_state"}
    try:
        ib = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
        st = json.loads(ORCH_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}

    if not ib.get("pending"):
        return {"ok": True, "healed": False, "reason": "inbox_not_pending"}

    meta = ib.get("meta") or {}
    sa = str(meta.get("sa_id") or ib.get("sa_id") or "")
    role = str(meta.get("queue_role") or "")
    pos = int(meta.get("queue_pos") or 0)
    if not sa.startswith("sa-") or not role:
        return {"ok": False, "error": "inbox_meta_incomplete", "sa_id": sa, "role": role}

    needs = st.get("status") in ("idle", "stopped", "done") or (
        st.get("status") == "awaiting_worker"
        and (st.get("expected_sa") != sa or st.get("expected_role") != role)
    )
    if not needs:
        return {"ok": True, "healed": False, "reason": "orchestrator_aligned", "status": st.get("status")}

    st.update(
        {
            "status": "awaiting_worker",
            "expected_sa": sa,
            "expected_role": role,
            "expected_pos": pos or st.get("expected_pos"),
            "stop_reason": None,
            "feasibility": None,
            "recovered_at": _now(),
            "recovery_reason": "orchestrator_inbox_drift",
        }
    )
    ORCH_PATH.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "healed": True, "sa_id": sa, "role": role, "pos": pos}


def replay_pending_inbox() -> dict:
    """Refresh INBOX.md + rule from pending JSON — no new deliver pile."""
    if not INBOX_JSON.is_file():
        return {"ok": False, "error": "no_inbox_json"}
    try:
        data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
    if not data.get("pending"):
        return {"ok": True, "skipped": True, "reason": "inbox_not_pending"}

    prompt = str(data.get("prompt") or "")
    meta = data.get("meta") or {}
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import INBOX_MD, write_active_inbox_rule  # noqa: WPS433

    data["replayed_at"] = _now()
    INBOX_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    pos = meta.get("queue_pos", "?")
    total = meta.get("queue_total", "?")
    role = meta.get("queue_role", "?")
    sa = meta.get("sa_id", "?")
    md = f"""<!-- WORKER_INBOX pending=1 source=stuck_recovery_replay queue={pos}/{total} role={role} sa={sa} -->
# SourceA Worker — prompt ready (INBOX replay)

**Replayed:** {data["replayed_at"]} — same turn, no duplicate inject.

---

{prompt}
"""
    INBOX_MD.parent.mkdir(parents=True, exist_ok=True)
    INBOX_MD.write_text(md, encoding="utf-8")
    write_active_inbox_rule(prompt, meta=meta)
    orch_heal = heal_orchestrator_inbox_drift()
    return {
        "ok": True,
        "replayed": True,
        "sa_id": sa,
        "role": role,
        "inbox_md": str(INBOX_MD),
        "orchestrator_heal": orch_heal,
    }


def sync_orchestrator_from_queue() -> dict:
    """When INBOX cleared — align orchestrator expected_* to healthy-queue next_pos."""
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import _queue_head_for_cleared_inbox  # noqa: WPS433

    if not ORCH_PATH.is_file():
        return {"ok": False, "error": "no_orchestrator_state"}
    sa_id, role, pos, total = _queue_head_for_cleared_inbox()
    try:
        st = json.loads(ORCH_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
    ghost_on_idle = not sa_id and bool(st.get("last_completed_sa"))
    if (
        st.get("status") == "idle"
        and int(st.get("expected_pos") or 0) == pos
        and str(st.get("expected_sa") or "") == sa_id
        and str(st.get("expected_role") or "") == role
        and not ghost_on_idle
    ):
        return {"ok": True, "synced": False, "reason": "already_aligned", "expected_sa": sa_id, "expected_role": role}
    state_path = Path.home() / ".sina" / "healthy-queue-state-v1.json"
    if state_path.is_file():
        try:
            qs = json.loads(state_path.read_text(encoding="utf-8"))
            lcp = int(qs.get("last_completed_pos") or 0)
            st["last_completed_pos"] = lcp
            qpath = Path.home() / ".sina" / "healthy-queue-30-active.json"
            items: list = []
            thread = ""
            hq: dict = {}
            if qpath.is_file():
                hq = json.loads(qpath.read_text(encoding="utf-8"))
                items = hq.get("queue") or []
                thread = str(hq.get("thread") or "")
            exhausted = bool(qs.get("queue_exhausted")) or bool(hq.get("queue_exhausted")) or not items
            if exhausted and not sa_id:
                st["last_completed_sa"] = ""
                st["last_completed_role"] = ""
                st["last_completed_pos"] = 0
            elif lcp == 0 or thread == "OUTBOUND-FACTORY":
                rr_path = Path.home() / ".sina" / "worker_round_report_v1.json"
                rr: dict = {}
                if rr_path.is_file():
                    try:
                        rr = json.loads(rr_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        rr = {}
                if (
                    thread == "OUTBOUND-FACTORY"
                    and not exhausted
                    and rr.get("turn_closed")
                    and rr.get("sa_focus")
                ):
                    st["last_completed_sa"] = str(rr.get("sa_focus") or "")
                    st["last_completed_role"] = str(rr.get("round_type") or "act")
                    st["last_completed_pos"] = max(lcp, int(st.get("expected_pos") or 1) - 1)
                elif lcp == 0:
                    st["last_completed_sa"] = ""
                    st["last_completed_role"] = ""
            elif 1 <= lcp <= len(items):
                done = items[lcp - 1]
                st["last_completed_sa"] = done.get("sa_id")
                st["last_completed_role"] = done.get("queue_role")
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            pass
    st.update(
        {
            "status": "idle",
            "expected_pos": pos,
            "expected_sa": sa_id,
            "expected_role": role,
            "updated_at": _now(),
            "recovery_reason": "sync_orchestrator_from_queue",
        }
    )
    ORCH_PATH.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "synced": True, "expected_sa": sa_id, "expected_role": role, "expected_pos": pos, "queue_total": total}


def sync_orchestrator_from_inbox() -> dict:
    """When INBOX pending but orchestrator idle — align expected_sa (stuck_recovery class)."""
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import inbox_status  # noqa: WPS433

    inbox = inbox_status()
    if not inbox.get("pending"):
        return {"ok": True, "synced": False, "reason": "inbox_not_pending"}
    if not ORCH_PATH.is_file():
        return {"ok": False, "error": "no_orchestrator_state"}
    try:
        st = json.loads(ORCH_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
    meta = inbox.get("meta") or {}
    sa = str(inbox.get("sa_id") or meta.get("sa_id") or "")
    role = str(inbox.get("queue_role") or meta.get("queue_role") or "")
    pos = int(meta.get("queue_pos") or 0)
    if (
        st.get("status") == "awaiting_worker"
        and str(st.get("expected_sa") or "") == sa
        and str(st.get("expected_role") or "") == role
    ):
        return {"ok": True, "synced": False, "reason": "already_aligned", "expected_sa": sa}
    st.update(
        {
            "status": "awaiting_worker",
            "expected_sa": sa,
            "expected_role": role,
            "expected_pos": pos or st.get("expected_pos"),
            "delivered_at": inbox.get("delivered_at") or st.get("delivered_at") or _now(),
            "recovery_reason": "sync_orchestrator_from_inbox",
            "updated_at": _now(),
        }
    )
    ORCH_PATH.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "synced": True, "expected_sa": sa, "expected_role": role}


def heal_orchestrator_timeout(*, redeliver: bool = True) -> dict:
    if not ORCH_PATH.is_file():
        return {"ok": False, "error": "no_orchestrator_state"}
    try:
        st = json.loads(ORCH_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}

    status = st.get("status")
    delivered = st.get("delivered_at") or ""
    elapsed = None
    if delivered:
        try:
            dt = datetime.fromisoformat(delivered.replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - dt).total_seconds()
        except ValueError:
            pass

    needs_heal = status in ("stopped",) and st.get("stop_reason") == "turn_timeout"
    needs_heal = needs_heal or (
        status == "awaiting_worker"
        and elapsed is not None
        and elapsed >= float(st.get("await_timeout_sec") or 3600) * 0.75
    )
    if not needs_heal:
        return {"ok": True, "healed": False, "reason": "orchestrator_ok", "status": status, "elapsed_sec": elapsed}

    st.update(
        {
            "status": "idle",
            "stop_reason": None,
            "recovered_at": _now(),
            "recovery_reason": "worker_stuck_recovery_v1",
        }
    )
    ORCH_PATH.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")

    deliver = None
    if redeliver:
        import importlib.util

        spec = importlib.util.spec_from_file_location("orch", SCRIPTS / "healthy-drain-orchestrator-v1.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        deliver = mod.deliver_current(force=True)

    return {
        "ok": True,
        "healed": True,
        "prior_status": status,
        "elapsed_sec": elapsed,
        "deliver": deliver,
    }


def run_recovery(*, redeliver: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from duplicate_inject_guard_v1 import clear_inject_lock  # noqa: WPS433
    from goal1_stuck_watchdog_v1 import run_watchdog  # noqa: WPS433
    from worker_inject_lib import inbox_status  # noqa: WPS433

    inbox = inbox_status()
    inbox_sa = str(inbox.get("sa_id") or (inbox.get("meta") or {}).get("sa_id") or "")

    steps = {
        "killed_hung": kill_hung_processes(),
        "watchdog": run_watchdog(max_age_sec=300),
        "inject_lock": clear_inject_lock(),
        "stale_turn": heal_stale_worker_turn(inbox_sa=inbox_sa),
        "orchestrator_inbox": heal_orchestrator_inbox_drift(),
        "orchestrator": heal_orchestrator_timeout(redeliver=redeliver),
        "inbox_replay": replay_pending_inbox() if inbox.get("pending") else {"skipped": True},
        "orch_inbox_sync": sync_orchestrator_from_inbox(),
    }
    out = {
        "ok": True,
        "schema": "worker-stuck-recovery-v1",
        "inbox_pending": inbox.get("pending"),
        "inbox_sa": inbox_sa,
        "steps": steps,
        "founder_action": "Open SourceA Worker chat → say: run inbox (once)",
    }
    _log(out)
    return out


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Worker stuck recovery — executor/hub only")
    p.add_argument("--json", action="store_true")
    p.add_argument("--redeliver", action="store_true", help="After timeout heal, force deliver next slice")
    args = p.parse_args()
    out = run_recovery(redeliver=args.redeliver)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        killed = out["steps"]["killed_hung"].get("count", 0)
        replay = out["steps"].get("inbox_replay", {})
        print(
            f"OK: worker-stuck-recovery · killed={killed} · "
            f"inbox_sa={out.get('inbox_sa')} · replay={replay.get('replayed', False)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
