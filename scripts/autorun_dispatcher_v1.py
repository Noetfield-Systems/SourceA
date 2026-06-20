#!/usr/bin/env python3
"""SourceA Autorun Dispatcher — smart engine routing.

Routes each queue item to the right engine:
  CHECK / verify / audit / review  → API Agent (Haiku, fast, headless, no CLI overhead)
  ACT / implement / build / fix    → CLI Agent (Sonnet, real tools, Bash/Write/Edit)

Kill switch: touch ~/.sina/auto-run-disabled-v1.flag
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT    = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
from healthy_queue_ssot_lib import (  # noqa: E402
    first_open_queue_pos,
    healthy_queue_state_path,
    is_commercial_default_queue,
    load_healthy_queue,
    queue_items,
    registry_status_for_sa,
    sync_home_queue_from_repo,
)
FLAG        = Path.home() / ".sina" / "auto-run-disabled-v1.flag"
CLI_FLAG    = Path.home() / ".sina" / "cli-disabled-v1.flag"
LOG         = Path.home() / ".sina" / "dispatcher-v1.jsonl"

CLI_ROLES = {"act", "implement", "build", "fix", "patch", "create", "write", "exec"}
API_ROLES = {"check", "verify", "audit", "review", "test", "validate", "read", "assess"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps({**row, "at": _now()}) + "\n")


def _queue() -> list[dict]:
    _, raw = load_healthy_queue()
    if is_commercial_default_queue(raw):
        raise RuntimeError(
            "INCIDENT-004: commercial queue forbidden as autorun default — use ~/.sina eval-dispatch"
        )
    return queue_items(raw)


def _current_pos() -> int:
    state = healthy_queue_state_path()
    if state.is_file():
        try:
            return int(json.loads(state.read_text()).get("next_pos") or 1)
        except Exception:
            pass
    return 1


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    from operating_mode_enforce_v1 import check_autorun_policy  # noqa: WPS433

    from single_boss_loop_v1 import check_exclusive  # noqa: WPS433

    loop_gate = check_exclusive(mode="overnight")
    if not loop_gate.get("ok"):
        holder = (loop_gate.get("holder") or {}).get("mode", "?")
        print(f"[{_now()}] DISPATCHER PAUSED — other boss loop active: {holder}")
        return 0

    policy = check_autorun_policy(caller="autorun_dispatcher")
    if not policy.get("valid"):
        reason = policy.get("reason", "AUTORUN_FORBIDDEN")
        print(f"[{_now()}] DISPATCHER PAUSED — {reason} (FOUNDER_BUSY_OPERATING_MODEL).")
        return 0

    # Kill switch (redundant with founder_busy law — kept for emergency)
    if FLAG.is_file():
        print(f"[{_now()}] DISPATCHER PAUSED — kill flag present. Remove to resume.")
        return 0

    from agent_cancel_guard_v1 import agent_cancel_active, agent_cancel_skip, write_cancel_receipt  # noqa: WPS433

    if agent_cancel_active():
        write_cancel_receipt(caller="autorun_dispatcher")
        skip = agent_cancel_skip(caller="autorun_dispatcher")
        print(f"[{_now()}] DISPATCHER PAUSED — agent-cancel flag ({skip.get('cancel_line', '')[:80]})")
        return 0

    sync = sync_home_queue_from_repo()
    if sync.get("synced"):
        print(
            f"[{_now()}] QUEUE_SYNC home←repo head={sync.get('repo_head')} "
            f"(replaced {sync.get('replaced_head')})"
        )

    queue = _queue()
    if not queue:
        print(f"[{_now()}] QUEUE EMPTY")
        return 0

    # Free pointer sync — never spend API on already-done REGISTRY tasks.
    import subprocess as _sp

    open_pos = first_open_queue_pos()
    cur_pos = _current_pos()
    # Forward-only reconcile — never rewind mid-slice (check→act→verify).
    if open_pos > cur_pos:
        proc = _sp.run(
            [sys.executable, str(SCRIPTS / "reconcile-queue-from-registry-v1.py"), "--apply"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        try:
            rec = json.loads(proc.stdout)
            print(
                f"[{_now()}] RECONCILE forward {cur_pos}→{rec.get('target_pos')} "
                f"(first_open={rec.get('first_open_pos')} rewind_blocked={rec.get('rewind_blocked')})"
            )
        except json.JSONDecodeError:
            print(f"[{_now()}] RECONCILE applied (non-json stdout)")
        queue = _queue()

    pos = _current_pos()
    total = len(queue)
    if pos < 1 or pos > total:
        pos = 1

    item = queue[pos - 1]
    role = (item.get("queue_role") or "act").lower().strip()
    sa_id = item.get("sa_id", f"sa-{pos:04d}")

    from overnight_turn_guard_v1 import (  # noqa: WPS433
        acquire_dispatch_lock,
        check_duplicate_turn,
        record_turn,
        release_dispatch_lock,
        role_engine,
    )

    lock = acquire_dispatch_lock(caller="autorun_dispatcher")
    if not lock.get("ok"):
        print(
            f"[{_now()}] DISPATCHER SKIP — {lock.get('reason')} "
            f"holder={lock.get('holder_pid')} age={lock.get('age_sec')}s ($0)"
        )
        _log({"event": "DISPATCH_SKIP", "reason": lock.get("reason"), "sa_id": sa_id, "pos": pos})
        return 0

    dup = check_duplicate_turn(sa_id=sa_id, role=role, pos=pos)
    if dup.get("skip"):
        release_dispatch_lock()
        print(
            f"[{_now()}] DISPATCHER SKIP — duplicate {sa_id} role={role} pos={pos} "
            f"registry_done={dup.get('registry_done')} ($0)"
        )
        _log({"event": "DUPLICATE_SKIP", **dup})
        return 0

    if registry_status_for_sa(sa_id) == "done":
        print(f"[{_now()}] SKIP_DONE_REGISTRY {sa_id} pos={pos} — advance slice, no API spend")
        _sp.run(
            [sys.executable, str(SCRIPTS / "advance-healthy-queue-v1.py"), "--skip-sa-slice"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        _log({"event": "SKIP_DONE_REGISTRY", "sa_id": sa_id, "pos": pos})
        release_dispatch_lock()
        return 0

    # Hard law: CHECK/verify → API (Haiku). ACT → CLI (Sonnet). Never Sonnet on CHECK.
    # CLI disable flag: if ~/.sina/cli-disabled-v1.flag exists, force all roles to API.
    if CLI_FLAG.exists():
        print(f"[{_now()}] CLI_DISABLED — forcing API engine for role={role} sa={sa_id}")
        _log({"event": "CLI_DISABLED", "sa_id": sa_id, "role": role})
        engine = "API"
    else:
        engine = role_engine(role)
    agent = "claude_api_agent_v1" if engine == "API" else "claude_code_agent_v1"

    # CLI = paid Sonnet — only queue_role act/implement. Never check/verify.
    if engine == "CLI":
        from overnight_turn_guard_v1 import is_cli_act_role  # noqa: WPS433

        if not is_cli_act_role(role):
            release_dispatch_lock()
            print(f"[{_now()}] CLI REJECT — role={role} is not ACT ($0)")
            _log({"event": "CLI_REJECT_NOT_ACT", "sa_id": sa_id, "role": role, "pos": pos})
            return 0

        receipt = ROOT / "receipts" / f"{sa_id}-receipt.json"
        if receipt.is_file():
            try:
                if json.loads(receipt.read_text()).get("status") == "DONE":
                    _sp.run(
                        [sys.executable, str(SCRIPTS / "advance-healthy-queue-v1.py")],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    release_dispatch_lock()
                    print(f"[{_now()}] CLI SKIP — receipt DONE for {sa_id}, advance ($0)")
                    _log({"event": "CLI_SKIP_RECEIPT_DONE", "sa_id": sa_id, "pos": pos})
                    return 0
            except (OSError, json.JSONDecodeError):
                pass

    # CLI ACT must not run blind while Scout (B) is off / prep missing.
    if engine == "CLI":
        from sidecar_gate_v1 import ensure_scout_prep_for_act  # noqa: WPS433

        sg = ensure_scout_prep_for_act(sa_id=sa_id)
        if not sg.get("ok"):
            release_dispatch_lock()
            print(
                f"[{_now()}] CLI BLOCKED — Scout/prep not ready for {sa_id} ($0). "
                f"scout_ok={sg.get('scout_ok')} prep_ok={sg.get('prep_ok')}"
            )
            _log({"event": "CLI_BLOCKED_NO_SCOUT", **sg})
            return 0

    print(f"[{_now()}] DISPATCHER → {engine} engine  sa={sa_id}  role={role}  pos={pos}/{total}")
    _log({"event": "DISPATCH", "engine": engine, "sa_id": sa_id, "role": role, "pos": pos})

    orch = _load_mod("orchestrator", SCRIPTS / "healthy-drain-orchestrator-v1.py")
    deliver = orch.deliver_current(force=True)
    if not deliver.get("ok"):
        print(f"[{_now()}] DISPATCHER ABORT — deliver failed: {deliver.get('error')}")
        release_dispatch_lock()
        return 1

    try:
        sys.path.insert(0, str(SCRIPTS))
        mod = _load_mod(agent, SCRIPTS / f"{agent}.py")

        result = mod.run_turn()
        result["engine"] = engine
        handle = orch.handle_turn_result(result)
        ok = result.get("ok", False) or bool(handle.get("overnight_skip")) or bool(
            handle.get("overnight_complete")
        )

        print(f"[{_now()}] DISPATCHER DONE  engine={engine}  ok={ok}  sa={sa_id}")
        if handle.get("overnight_skip"):
            print(
                f"[{_now()}] OVERNIGHT_SKIP advanced sa={handle.get('sa_id')} "
                f"next_pos={(handle.get('advanced') or {}).get('next_pos')}"
            )
        if handle.get("overnight_complete"):
            print(
                f"[{_now()}] OVERNIGHT_COMPLETE advanced sa={handle.get('sa_id')} "
                f"next_pos={(handle.get('advanced') or {}).get('next_pos')}"
            )
        _log({"event": "DISPATCH_DONE", "engine": engine, "ok": ok, "sa_id": sa_id, **{
            k: result.get(k) for k in ("status", "cost_usd", "tokens_in", "tokens_out", "elapsed")
            if result.get(k) is not None
        }})
        record_turn(
            sa_id=sa_id,
            role=role,
            pos=pos,
            engine=engine,
            ok=ok,
            cost_usd=float(result.get("cost_usd") or 0),
            status=str(result.get("status") or ""),
        )
    finally:
        release_dispatch_lock()

    # ── Always run registry updater after every turn ─────────────────────────
    # This is what moves the counter. Receipts alone don't update REGISTRY.json.
    try:
        reg_mod = _load_mod("registry_updater_v1", SCRIPTS / "registry_updater_v1.py")
        reg_result = reg_mod.run(dry_run=False)
        updated = reg_result.get("updated", 0)
        done    = reg_result.get("registry_done", "?")
        total   = reg_result.get("registry_total", "?")
        print(f"[{_now()}] REGISTRY  {done}/{total} done  (+{updated} this turn)")
        _log({"event": "REGISTRY_UPDATE", "done": done, "total": total, "updated": updated})
    except Exception as exc:
        print(f"[{_now()}] REGISTRY UPDATE ERROR: {exc}")

    # Event-driven Mac caretaker — only on sleep dispatch (no timer poll)
    try:
        care = _load_mod("caretaker", SCRIPTS / "sleep_mac_caretaker_v1.py")
        cr = care.tick(caller="autorun_dispatcher", trigger="post_dispatch")
        if cr.get("actions"):
            print(f"[{_now()}] CARETAKER {cr.get('actions')}")
        _log({"event": "CARETAKER", **{k: cr.get(k) for k in ("trigger", "actions", "ok")}})
    except Exception as exc:
        print(f"[{_now()}] CARETAKER SKIP: {exc}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
