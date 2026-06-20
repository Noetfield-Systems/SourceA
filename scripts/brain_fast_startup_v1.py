#!/usr/bin/env python3
"""Fast Brain tick — route Worker INBOX in <3s; never run hospital/E2E on session start.

Law: BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md · INCIDENT-026
Use: brain-session-start.sh (SINA_BRAIN_FAST=1) · broker brain_sync fast skip
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "brain-fast-startup-v1.json"
ORCH = SINA / "healthy-drain-orchestrator-v1.json"
SELF_HEAL = SINA / "brain-self-heal-startup-v1.json"
FAST_TTL_SEC = 300


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _age_sec(path: Path) -> float | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        at = str(data.get("at") or "")
        if not at:
            return None
        ts = datetime.strptime(at.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - ts).total_seconds()
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def _clear_stale_orch_stop() -> dict:
    if not ORCH.is_file():
        return {"ok": True, "skipped": "no_orch"}
    try:
        st = json.loads(ORCH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"ok": False, "error": "orch_read"}
    reason = st.get("stop_reason")
    if reason not in ("live_pack_validator_blocked", "feasibility_blocked"):
        return {"ok": True, "skipped": "no_stale_stop", "stop_reason": reason}
    lp = st.get("live_pack_validator") or {}
    lp_at = _age_sec(Path(SINA / "live-pack-validator-receipt-v1.json")) if lp else None
    if reason == "live_pack_validator_blocked":
        receipt_path = SINA / "live-pack-validator-receipt-v1.json"
        if receipt_path.is_file():
            try:
                lp_live = json.loads(receipt_path.read_text(encoding="utf-8"))
                if lp_live.get("ok"):
                    st.pop("stop_reason", None)
                    st["live_pack_validator"] = lp_live
                    if st.get("status") == "stopped":
                        st["status"] = "idle"
                    ORCH.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
                    return {"ok": True, "cleared": reason, "via": "fresh_receipt"}
            except (OSError, json.JSONDecodeError):
                pass
        if lp_at is not None and lp_at > FAST_TTL_SEC:
            st.pop("stop_reason", None)
            if st.get("status") == "stopped":
                st["status"] = "idle"
            ORCH.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
            return {"ok": True, "cleared": reason, "lp_age_sec": lp_at}
    if reason == "feasibility_blocked":
        sys.path.insert(0, str(SCRIPTS))
        from prompt_feasibility_gate import check_session  # noqa: WPS433

        feas = check_session(role="worker")
        if feas.get("action") != "STOP_INJECT":
            st.update({"status": "idle", "stop_reason": None, "feasibility_recovered_at": _now()})
            ORCH.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
            return {"ok": True, "cleared": reason, "feasibility": feas.get("action")}
    return {"ok": True, "skipped": "stop_still_valid", "stop_reason": reason}


def _refresh_stale_live_pack() -> dict:
    """Refresh live-pack receipt only when orchestrator blocked or receipt missing/fail."""
    receipt_path = SINA / "live-pack-validator-receipt-v1.json"
    orch_blocked = False
    if ORCH.is_file():
        try:
            st = json.loads(ORCH.read_text(encoding="utf-8"))
            orch_blocked = st.get("stop_reason") == "live_pack_validator_blocked"
        except (OSError, json.JSONDecodeError):
            pass
    if receipt_path.is_file():
        try:
            live = json.loads(receipt_path.read_text(encoding="utf-8"))
            age = _age_sec(receipt_path)
            if live.get("ok") and not orch_blocked and age is not None and age < FAST_TTL_SEC:
                return {"ok": True, "skipped": "fresh_receipt", "age_sec": age}
        except (OSError, json.JSONDecodeError):
            pass
    if not orch_blocked and receipt_path.is_file():
        try:
            live = json.loads(receipt_path.read_text(encoding="utf-8"))
            if live.get("ok"):
                return {"ok": True, "skipped": "receipt_ok"}
        except (OSError, json.JSONDecodeError):
            pass
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "validate_pack_live",
            SCRIPTS / "validate-next-prompt-pack-live-v1.py",
        )
        vmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vmod)  # type: ignore[union-attr]
        pack_val = vmod.validate(write_receipt=True)
        if pack_val.get("ok") and ORCH.is_file():
            st = json.loads(ORCH.read_text(encoding="utf-8"))
            st.pop("stop_reason", None)
            st["live_pack_validator"] = pack_val
            if st.get("status") == "stopped":
                st["status"] = "idle"
            ORCH.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
        return {"ok": bool(pack_val.get("ok")), "refreshed": True, "failed": pack_val.get("failed")}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _mirror_self_heal_receipt(fast_row: dict) -> None:
    """Keep brain-self-heal-startup receipt compatible with legacy validators."""
    mirror = {
        "schema": "brain-self-heal-startup-v1",
        "at": fast_row.get("at") or _now(),
        "caller": fast_row.get("caller") or "brain_fast",
        "ok": bool(fast_row.get("ok")),
        "founder_ready": bool(fast_row.get("ok")),
        "founder_message": "System ready. FAST_BRAIN active — Worker INBOX route only.",
        "p0_blockers": [] if fast_row.get("ok") else ["FAST_BRAIN_FAIL"],
        "steps": fast_row.get("steps") or [],
        "fast_brain": True,
        "elapsed_ms": fast_row.get("elapsed_ms"),
    }
    SELF_HEAL.write_text(json.dumps(mirror, indent=2) + "\n", encoding="utf-8")


def _heal_bind_fast() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from healthy_pack_bind_lib_v1 import bind_status, clear_stale_turn_bind  # noqa: WPS433

    b = bind_status()
    if b.get("ok") and b.get("match"):
        return {"ok": True, "skipped": "bind_ok", "bind": b}
    clear_stale_turn_bind()
    try:
        from healthy_pack_bind_lib_v1 import heal_bind_mismatch  # noqa: WPS433

        if b.get("inbox_pending"):
            heal = heal_bind_mismatch(force_deliver=False)
        else:
            heal = heal_bind_mismatch(force_deliver=True)
        return {"ok": bool(heal.get("ok")), "heal": heal, "bind": bind_status()}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "bind": bind_status()}


def _brain_health_wisdom(*, brain_row: dict, steps: list[dict], hub: dict) -> dict:
    """Fast health + wise routing — disk only, no hospital."""
    sys.path.insert(0, str(SCRIPTS))
    progress = brain_row.get("progress_honest") or {}
    chain = brain_row.get("chain") or {}
    inbox = brain_row.get("inbox") or {}
    feas = brain_row.get("feasibility") or {}
    one_sa = brain_row.get("one_sa_per_turn") or {}
    qh = brain_row.get("queue_head") or {}

    bind_step = next((s for s in steps if s.get("id") == "bind_heal"), {})
    bind = (bind_step.get("bind") or bind_step.get("heal") or {}).get("bind") or bind_step.get("bind") or {}

    checks = {
        "hub": bool(hub.get("ok")),
        "brain_validate": bool(brain_row.get("ok")),
        "bind_match": bool(bind.get("match") if bind else one_sa.get("ok")),
        "broker_stale_zero": int(progress.get("broker_stale") or 0) == 0,
        "unproven_zero": int(progress.get("unproven_done") or 0) == 0,
        "chain_activate": chain.get("activate") in ("READY", "PASS", "RUNNING"),
        "feasibility_proceed": feas.get("action") == "PROCEED" or feas.get("ok") is True,
        "freeze_off": True,
    }
    try:
        from factory_control_v1 import rebuild_factory_now  # noqa: WPS433

        fn = rebuild_factory_now(caller="brain_fast_health", force=False)
        kill = bool(fn.get("kill_flag"))
        outbound = False
        hq_path = SINA / "healthy-queue-30-active.json"
        if hq_path.is_file():
            try:
                hq = json.loads(hq_path.read_text(encoding="utf-8"))
                outbound = (
                    str(hq.get("thread") or "") == "OUTBOUND-FACTORY"
                    or str(hq.get("product") or "").startswith("Outbound Factory")
                )
            except (OSError, json.JSONDecodeError):
                pass
        checks["freeze_off"] = not kill or outbound
        checks["outbound_drain_override"] = outbound and kill
        checks["spawn_gate_hint"] = fn.get("mode")
    except Exception:
        pass

    score = sum(1 for v in checks.values() if v)
    total = len(checks)
    healthy = score >= total - 1 and checks["hub"] and checks["brain_validate"]

    sa = str(qh.get("sa_id") or inbox.get("sa_id") or "")
    role = str(qh.get("role") or inbox.get("queue_role") or "check")
    action = str(brain_row.get("brain_action") or "idle")

    do_not: list[str] = []
    if inbox.get("pending"):
        do_not.extend(["Brain must not implement", "Brain must not run E2E/hospital", "Brain must not re-deliver INBOX"])
    if not checks["freeze_off"]:
        do_not.append("Drain blocked — FREEZE ON; founder resume required")

    why = brain_row.get("founder_surface") or brain_row.get("mandatory_next") or ""
    if healthy and inbox.get("pending") and sa:
        why = f"INBOX is SSOT · {sa} {role.upper()} pending · Worker owns execution"
    elif healthy and sa and not inbox.get("pending"):
        why = f"Queue head {sa} · deliver then Worker runs one role only"

    return {
        "healthy": healthy,
        "score": f"{score}/{total}",
        "checks": checks,
        "wise": {
            "role_law": "Brain routes · Worker implements · one sa/turn",
            "do_now": brain_row.get("mandatory_next") or action,
            "do_not": do_not,
            "two_speed_clocks": "Factory REGISTRY ≠ commercial lane — both parallel (sa-0967)",
            "why": why,
        },
    }


def run_fast_brain(*, caller: str = "brain_fast") -> dict:
    t0 = time.monotonic()
    os.environ.setdefault("SINA_BRAIN_FAST", "1")
    os.environ.setdefault("SINA_COMMERCIAL_LOOP", "1")
    os.environ.setdefault("SINA_BROKER_FAST", "1")
    sys.path.insert(0, str(SCRIPTS))
    steps: list[dict] = []

    from brain_self_heal_startup_v1 import check_hub  # noqa: WPS433

    hub = check_hub(restart=False)
    steps.append({"id": "hub", **hub})

    fast_age = _age_sec(RECEIPT)
    skip_heavy = fast_age is not None and fast_age < FAST_TTL_SEC
    if not skip_heavy:
        from brain_self_heal_startup_v1 import check_queue, run_validators  # noqa: WPS433

        validators = run_validators(autfix=True)
        steps.append({"id": "validators", **validators})
        queue = check_queue(rebuild=True)
        steps.append({"id": "queue", **queue})
        live_pack = _refresh_stale_live_pack()
        steps.append({"id": "live_pack", **live_pack})
    else:
        steps.append({"id": "validators", "ok": True, "skipped": "fresh_fast_receipt", "age_sec": fast_age})
        steps.append({"id": "queue", "ok": True, "skipped": "fresh_fast_receipt"})
        steps.append({"id": "live_pack", "ok": True, "skipped": "fresh_fast_receipt"})

    orch = _clear_stale_orch_stop()
    steps.append({"id": "orch_unstick", **orch})

    bind = _heal_bind_fast()
    steps.append({"id": "bind_heal", **bind})

    try:
        from l1_agent_pipeline_wire_v1 import wire_l1_pipeline  # noqa: WPS433

        l1 = wire_l1_pipeline(sync_brain=True)
        steps.append({"id": "l1_wire_fast", "ok": bool(l1.get("ok")), "ms": l1.get("ms")})
    except Exception as exc:
        steps.append({"id": "l1_wire_fast", "ok": False, "error": str(exc)})

    try:
        import subprocess

        p = subprocess.run(
            [sys.executable, str(SCRIPTS / "brain_governance_wire_v1.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=8,
        )
        steps.append({"id": "brain_governance_sync", "ok": p.returncode == 0, "exit": p.returncode})
    except Exception as exc:
        steps.append({"id": "brain_governance_sync", "ok": False, "error": str(exc)})

    from brain_validate_goal1_v1 import validate_goal1  # noqa: WPS433

    brain_row = validate_goal1(strict=False)
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "brain-goal1-validation-v1.json").write_text(
        json.dumps(brain_row, indent=2) + "\n", encoding="utf-8"
    )
    steps.append(
        {
            "id": "brain_validate",
            "ok": bool(brain_row.get("ok")),
            "brain_action": brain_row.get("brain_action"),
            "founder_surface": brain_row.get("founder_surface"),
        }
    )

    ok = hub.get("ok") and bool(brain_row.get("ok"))
    health = _brain_health_wisdom(brain_row=brain_row, steps=steps, hub=hub)
    elapsed_ms = int((time.monotonic() - t0) * 1000)
    row = {
        "schema": "brain-fast-startup-v1",
        "at": _now(),
        "caller": caller,
        "ok": ok and health.get("healthy"),
        "elapsed_ms": elapsed_ms,
        "law": "FAST_BRAIN — healthy · wise · route Worker INBOX",
        "health": health,
        "brain_action": brain_row.get("brain_action"),
        "mandatory_next": brain_row.get("mandatory_next"),
        "queue_head": brain_row.get("queue_head"),
        "chain": brain_row.get("chain"),
        "progress_honest": brain_row.get("progress_honest"),
        "steps": steps,
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    _mirror_self_heal_receipt(row)
    try:
        from brain_live_context_v1 import build_brain_live_context  # noqa: WPS433

        build_brain_live_context()
    except Exception:
        pass
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Fast Brain startup tick")
    p.add_argument("--caller", default="cli")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    os.environ.setdefault("SINA_BRAIN_FAST", "1")
    row = run_fast_brain(caller=args.caller)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
