#!/usr/bin/env python3
"""Anti-staleness auto wire — L0.5 → L1 → L2 unified sync (always automatic).

Law: SOURCEA_ANTI_STALENESS_AUTO_WIRE_LAYER_SYNC_LOCKED_v1.md
Receipt: ~/.sina/anti-staleness-auto-wire-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
RECEIPT = SINA / "anti-staleness-auto-wire-v1.json"
SESSION_FLIGHT = SINA / "anti-staleness-session-flight-v1.json"
PY = sys.executable


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 120) -> tuple[int, str]:
    try:
        out = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT), timeout=timeout
        )
        return 0, out
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output or ""
    except subprocess.TimeoutExpired as e:
        return 124, (e.output or "") + "\nTIMEOUT"


def _parse_json(out: str) -> dict:
    i = out.find("{")
    if i < 0:
        return {}
    try:
        return json.loads(out[i:])
    except json.JSONDecodeError:
        return {}


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _session_flight_begin(*, tier: str) -> tuple[bool, dict | None]:
    """One session-tier wire at a time — prevents Mac heat from stacked gates."""
    if tier != "session":
        return True, None
    lock = _read_json(SESSION_FLIGHT)
    other_pid = int(lock.get("pid") or 0)
    if other_pid and other_pid != os.getpid() and _pid_alive(other_pid):
        cached = _read_json(RECEIPT)
        if cached.get("schema"):
            row = dict(cached)
            row["session_flight"] = "dedupe_active_run"
            row["session_flight_pid"] = other_pid
            return False, row
    SINA.mkdir(parents=True, exist_ok=True)
    SESSION_FLIGHT.write_text(
        json.dumps({"pid": os.getpid(), "at": _now(), "tier": tier}, indent=2) + "\n",
        encoding="utf-8",
    )
    return True, None


def _session_flight_end() -> None:
    lock = _read_json(SESSION_FLIGHT)
    if int(lock.get("pid") or 0) == os.getpid():
        SESSION_FLIGHT.unlink(missing_ok=True)


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _surface_live_lines() -> dict:
    """Read-only live lines for zero-latency inject (works under focus freeze)."""
    surf = _read_json(SINA / "agent-live-surfaces-v1.json")
    return {
        "factory_now_line": str(surf.get("factory_now_line") or ""),
        "queue_sa": str(surf.get("queue_sa") or ""),
        "zero_drift_line": str(surf.get("zero_drift_line") or ""),
        "better_loop_line": str(surf.get("better_loop_line") or ""),
        "best_loop_oqg_line": str(surf.get("best_loop_oqg_line") or ""),
        "sascip_safety_line": str(surf.get("sascip_safety_line") or surf.get("sascip_line") or ""),
        "surfaces_synced_at": str(surf.get("synced_at") or ""),
        "nerve_system_line": str(surf.get("nerve_system_line") or ""),
        "ui_upgrade_first_check_line": str(surf.get("ui_upgrade_first_check_line") or ""),
        "form_official_line": str(surf.get("form_official_line") or ""),
    }


def _merge_focus_freeze_receipt(cached: dict) -> dict:
    """Founder-work freeze skips heavy motors — still refresh live lines + lightweight queue unify."""
    fresh = _surface_live_lines()
    unify_ok = False
    unify_aligned = False
    queue_sa_unify = str(fresh.get("queue_sa") or "")
    unify_step = {"layer": "L0.5", "step": "queue_ssot_unify", "ok": False, "exit": 1, "mode": "focus_freeze_light"}
    code, out = _run([PY, str(SCRIPTS / "queue_ssot_unify_v1.py"), "--json", "--fast"], timeout=90)
    unify = _parse_json(out)
    unify_ok = code == 0 and bool(unify.get("ok"))
    head = (unify.get("steps") or {}).get("head") if isinstance(unify.get("steps"), dict) else {}
    if isinstance(head, dict) and head.get("sa_id"):
        queue_sa_unify = str(head.get("sa_id") or queue_sa_unify)
    unify_aligned = bool((unify.get("steps") or {}).get("aligned")) if isinstance(unify.get("steps"), dict) else False
    unify_step.update(
        {
            "ok": unify_ok,
            "exit": code,
            "queue_sa": queue_sa_unify,
            "aligned": unify_aligned,
        }
    )
    steps = list(cached.get("steps") or [])
    replaced = False
    for i, step in enumerate(steps):
        if step.get("step") == "queue_ssot_unify":
            steps[i] = unify_step
            replaced = True
            break
    if not replaced:
        steps.append(unify_step)
    row = {
        **cached,
        **fresh,
        "ok": True,
        "mode": "mac_focus_freeze",
        "skipped": True,
        "at": _now(),
        "queue_sa": queue_sa_unify or fresh.get("queue_sa") or cached.get("queue_sa") or "",
        "steps": steps,
    }
    row["layers"] = {
        **(cached.get("layers") or {}),
        "L0_5": {
            **((cached.get("layers") or {}).get("L0_5") or {}),
            "disk_live_wire": bool(fresh.get("factory_now_line")),
            "queue_unify": unify_ok or unify_aligned,
            "live_lines_refreshed": True,
        },
    }
    row["note"] = "focus freeze — live lines + queue_ssot_unify --fast"
    return row


def run_anti_staleness_auto_wire(*, role: str = "any", tier: str = "session") -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from mac_focus_freeze_v1 import is_focus_freeze, read_cached_json, skip_receipt  # noqa: WPS433

    proceed, deduped = _session_flight_begin(tier=tier)
    if not proceed and deduped is not None:
        return deduped

    if is_focus_freeze():
        cached = read_cached_json(RECEIPT)
        if cached.get("schema"):
            row = _merge_focus_freeze_receipt(cached)
            RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            _session_flight_end()
            return row
        row = skip_receipt(
            schema="anti-staleness-auto-wire-v1",
            script="anti_staleness_auto_wire_v1.py",
            note="focus freeze — using disk cache only",
        )
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        _session_flight_end()
        return row

    steps: list[dict] = []
    ok = True
    sys.path.insert(0, str(SCRIPTS))
    try:
        from stranger_agent_safety_lib_v1 import clear_stale_unattended_panic  # noqa: WPS433

        panic_heal = clear_stale_unattended_panic()
        if panic_heal.get("cleared"):
            steps.append({"step": "clear_stale_unattended_panic", "ok": True, **panic_heal})
    except Exception as exc:
        steps.append({"step": "clear_stale_unattended_panic", "ok": True, "skipped": str(exc)})
    dlw: dict = {}
    unify: dict = {}
    pipe: dict = {}
    monitor: dict = {}
    worker_heal: dict = {}

    # --- L0.5 machine pipeline ---
    code, out = _run([PY, str(SCRIPTS / "disk_live_wire_sync_v1.py"), "--role", role, "--json"], timeout=90)
    dlw = _parse_json(out)
    step_ok = code == 0 and dlw.get("ok")
    steps.append({"layer": "L0.5", "step": "disk_live_wire_sync", "ok": step_ok, "exit": code})
    ok = ok and step_ok

    try:
        sys.path.insert(0, str(SCRIPTS))
        from vocabulary_guard_v1 import run_vocabulary_gate  # noqa: WPS433

        vocab = run_vocabulary_gate(include_tooling=False)
        step_ok = bool(vocab.get("ok"))
        steps.append(
            {
                "layer": "L0.5",
                "step": "vocabulary_guard",
                "ok": step_ok,
                "exit": 0 if step_ok else 1,
                "violations": len(vocab.get("violations") or []),
                "factory_now_line": (vocab.get("checks") or [{}])[1].get("factory_now_line")
                if len(vocab.get("checks") or []) > 1
                else "",
            }
        )
        ok = ok and step_ok
    except Exception as exc:
        steps.append({"layer": "L0.5", "step": "vocabulary_guard", "ok": False, "error": str(exc)})
        ok = False

    unify_cmd = [PY, str(SCRIPTS / "queue_ssot_unify_v1.py"), "--json"]
    if tier == "session":
        unify_cmd.append("--fast")
    code, out = _run(unify_cmd, timeout=60)
    unify = _parse_json(out)
    step_ok = code == 0 and bool(unify.get("ok"))
    head = (unify.get("steps") or {}).get("head") if isinstance(unify.get("steps"), dict) else {}
    queue_sa_unify = head.get("sa_id") if isinstance(head, dict) else None
    steps.append(
        {
            "layer": "L0.5",
            "step": "queue_ssot_unify",
            "ok": step_ok,
            "exit": code,
            "queue_sa": queue_sa_unify,
            "aligned": (unify.get("steps") or {}).get("aligned") if isinstance(unify.get("steps"), dict) else None,
        }
    )
    ok = ok and step_ok

    try:
        sys.path.insert(0, str(SCRIPTS))
        from monitor_live_sync_v1 import sync_disk  # noqa: WPS433

        monitor = sync_disk(force=False, reason=f"anti_staleness_auto_wire:{tier}", light=True)
        step_ok = bool(monitor.get("ok", True))
    except Exception as exc:
        monitor = {"ok": True, "skipped": True, "error": str(exc)}
        step_ok = True
    steps.append({"layer": "L0.5", "step": "monitor_live_sync_light", "ok": step_ok})

    # --- L1 + L2 agentic pipeline ---
    pipe_tier = "full" if tier == "full" else "fast"
    pipe_cmd = [PY, str(SCRIPTS / "agentic_layer_pipeline_v2.py"), "--json", "--tier", pipe_tier]
    if pipe_tier == "fast":
        pipe_cmd.append("--no-sync")
    if tier == "full":
        pipe_cmd.append("--self-heal")
    code, out = _run(pipe_cmd, timeout=120)
    pipe = _parse_json(out)
    step_ok = code == 0 and pipe.get("schema") == "agentic-layer-pipeline-v2"
    if role in ("brain", "governance", "commercial", "brief", "any") and pipe_tier == "fast":
        step_ok = step_ok and (pipe.get("l1_summary") or {}).get("l1_to_brain", 0) >= 3
    if role in ("worker", "maintainer", "archive", "researcher") and pipe_tier == "fast":
        step_ok = step_ok and (pipe.get("brain_summary") or {}).get("l2_wired", 0) >= 4
    steps.append(
        {
            "layer": "L1+L2",
            "step": "agentic_layer_pipeline_v2",
            "ok": step_ok,
            "exit": code,
            "tier": pipe_tier,
            "health": (pipe.get("health") or {}).get("status"),
            "queue_head": (pipe.get("brain_summary") or {}).get("queue_head"),
            "l2_wired": (pipe.get("brain_summary") or {}).get("l2_wired"),
        }
    )
    ok = ok and step_ok

    # --- Brain receipt aligned with queue head (INCIDENT-033) ---
    code, out = _run(
        [PY, str(SCRIPTS / "brain_validate_goal1_v1.py"), "--write-receipt", "--json"],
        timeout=90,
    )
    brain_val = _parse_json(out)
    step_ok = code == 0 and brain_val.get("ok", True)
    steps.append(
        {
            "layer": "L1",
            "step": "brain_validate_write_receipt",
            "ok": step_ok,
            "exit": code,
            "queue_head": (brain_val.get("queue_head") or {}).get("sa_id"),
        }
    )
    ok = ok and step_ok

    # --- Worker tier: fast heal loop ---
    if tier == "worker":
        code, out = _run(
            [PY, str(SCRIPTS / "worker_anti_staleness_heal_v1.py"), "--reason", "auto-wire", "--force", "--json"],
            timeout=45,
        )
        worker_heal = _parse_json(out)
        step_ok = code == 0 and worker_heal.get("ok", True)
        steps.append({"layer": "L2", "step": "worker_anti_staleness_heal", "ok": step_ok, "exit": code})
        ok = ok and step_ok

    if tier == "full":
        code, out = _run(
            [PY, str(SCRIPTS / "brain_validate_goal1_v1.py"), "--write-receipt", "--json"],
            timeout=90,
        )
        brain_val = _parse_json(out)
        step_ok = code == 0 and brain_val.get("ok", True)
        steps.append({"layer": "L1", "step": "brain_validate_receipt", "ok": step_ok, "exit": code})
        ok = ok and step_ok

    code, _ = _run([PY, str(SCRIPTS / "worker_stale_prompt_scrub_v1.py"), "--json"], timeout=15)
    steps.append({"layer": "L0.5", "step": "worker_stale_prompt_scrub", "ok": code == 0, "exit": code})

    code, _ = _run([PY, str(SCRIPTS / "worker_live_context_v1.py"), "--json"], timeout=15)
    steps.append({"layer": "L0.5", "step": "worker_live_context", "ok": code == 0, "exit": code})

    code, _ = _run([PY, str(SCRIPTS / "brain_live_context_v1.py"), "--json"], timeout=15)
    steps.append({"layer": "L0.5", "step": "brain_live_context", "ok": code == 0, "exit": code})

    code, _ = _run([PY, str(SCRIPTS / "brain_stale_prompt_scrub_v1.py"), "--json"], timeout=15)
    steps.append({"layer": "L0.5", "step": "brain_stale_prompt_scrub", "ok": code == 0, "exit": code})

    surf_lines = _surface_live_lines()
    factory_line = dlw.get("factory_now_line") or surf_lines.get("factory_now_line") or ""
    queue_sa = (
        dlw.get("queue_sa")
        or queue_sa_unify
        or surf_lines.get("queue_sa")
        or (pipe.get("brain_summary") or {}).get("queue_head")
        or ""
    )

    receipt = {
        "schema": "anti-staleness-auto-wire-v1",
        "ok": ok,
        "at": _now(),
        "role": role,
        "tier": tier,
        "law": "SOURCEA_ANTI_STALENESS_AUTO_WIRE_LAYER_SYNC_LOCKED_v1.md",
        "factory_now_line": factory_line,
        "queue_sa": queue_sa,
        "zero_drift_line": surf_lines.get("zero_drift_line") or "",
        "better_loop_line": surf_lines.get("better_loop_line") or "",
        "best_loop_oqg_line": surf_lines.get("best_loop_oqg_line") or "",
        "nerve_system_line": surf_lines.get("nerve_system_line") or "",
        "sascip_safety_line": surf_lines.get("sascip_safety_line") or "",
        "surfaces_synced_at": surf_lines.get("surfaces_synced_at") or "",
        "layers": {
            "L0_5": {"disk_live_wire": dlw.get("ok"), "queue_unify": unify.get("aligned", unify.get("ok"))},
            "L1": {
                "l1_to_brain": (pipe.get("l1_summary") or {}).get("l1_to_brain"),
                "health": (pipe.get("health") or {}).get("L1"),
            },
            "L2": {
                "l2_wired": (pipe.get("brain_summary") or {}).get("l2_wired"),
                "health": (pipe.get("health") or {}).get("L2"),
            },
        },
        "paths": {
            "live_surfaces": str(SINA / "agent-live-surfaces-v1.json"),
            "pipeline_v2": str(SINA / "agentic-layer-pipeline-v2.json"),
            "brain_wire": str(SINA / "governance-brain-wire-v1.json"),
            "l1_pipeline": str(SINA / "l1-agent-pipeline-wire-v1.json"),
        },
        "steps": steps,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    _session_flight_end()
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Anti-staleness auto wire L0.5→L1→L2")
    ap.add_argument("--role", default="any")
    ap.add_argument("--tier", default="session", choices=["session", "worker", "full"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_anti_staleness_auto_wire(role=args.role, tier=args.tier)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"ANTI_STALENESS_AUTO_WIRE ok={row['ok']} tier={args.tier} "
            f"queue={row.get('queue_sa')} layers=L0.5+L1+L2"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
