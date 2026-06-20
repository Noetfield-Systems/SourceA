#!/usr/bin/env python3
"""Stranger agent safety live wire — ADMIT → PROBE → PANIC → WATCH → SERVE (session tier).

Law: docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md
Receipt: ~/.sina/stranger-agent-safety-live-wire-v1.json
Wraps stranger_agent_safety_pipeline_v1.py · cross_lane_edit_guard_v1 · panic flags.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
RECEIPT = SINA / "stranger-agent-safety-live-wire-v1.json"
SASCIP_RECEIPT = SINA / "stranger-agent-admission-receipt-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
WATCH_RECEIPT = SINA / "stranger-agent-watch-receipt-v1.json"
MAC_EMERGENCY = SINA / "mac-health-emergency-active-v1.flag"
CANCEL_FLAG = SINA / "agent-cancel-v1.flag"
PY = sys.executable
SESSION_BUDGET_SEC = 15

SENTINEL_PROBES: tuple[tuple[str, str, bool], ...] = (
    ("lane_ok", "scripts/stranger_agent_safety_lib_v1.py", True),
    ("ssot_blocked", "docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md", False),
    ("brain_blocked", "brain-os/laws/SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1.md", False),
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _parse_json(out: str) -> dict:
    i = out.find("{")
    if i < 0:
        return {}
    try:
        return json.loads(out[i:])
    except json.JSONDecodeError:
        return {}


def _age_sec(path: Path) -> float | None:
    if not path.is_file():
        return None
    try:
        return time.time() - path.stat().st_mtime
    except OSError:
        return None


def _run(cmd: list[str], *, timeout: int = 30) -> tuple[int, str]:
    try:
        out = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT), timeout=timeout
        )
        return 0, out
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output or ""
    except subprocess.TimeoutExpired as e:
        return 124, (e.output or "") + "\nTIMEOUT"


def _panic_state() -> dict:
    cancel = CANCEL_FLAG.is_file()
    emergency = MAC_EMERGENCY.is_file()
    cancel_line = ""
    if cancel:
        try:
            cancel_line = CANCEL_FLAG.read_text(encoding="utf-8").splitlines()[0][:120]
        except OSError:
            pass
    active = cancel or emergency
    return {
        "ok": not active,
        "active": active,
        "agent_cancel": cancel,
        "mac_emergency": emergency,
        "cancel_line": cancel_line,
    }


def _cross_lane_probe(*, agent: str, rel_path: str, expect_allowed: bool, explicit_order: str = "") -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from cross_lane_edit_guard_v1 import check_edit  # noqa: WPS433

    target = str(ROOT / rel_path)
    row = check_edit(agent=agent, path=target, explicit_order=explicit_order)
    allowed = bool(row.get("allowed"))
    ok = allowed == expect_allowed
    return {
        "probe": rel_path,
        "expect_allowed": expect_allowed,
        "allowed": allowed,
        "ok": ok,
        "reason": row.get("reason"),
    }


def _run_sentinel_probes(*, agent: str, explicit_order: str = "") -> dict:
    rows = [_cross_lane_probe(agent=agent, rel_path=p, expect_allowed=exp, explicit_order=explicit_order) for _, p, exp in SENTINEL_PROBES]
    ok = all(r.get("ok") for r in rows)
    return {"ok": ok, "probes": rows}


def _compose_safety_line(
    *,
    admission: dict,
    probes_ok: bool,
    panic_ok: bool,
    watch_ok: bool,
) -> str:
    cls = admission.get("classification") or {}
    inject = admission.get("inject") or {}
    tier = cls.get("trust_tier") or inject.get("trust_tier") or "?"
    resolved = cls.get("resolved_agent_id") or inject.get("resolved_agent_id") or "?"
    risk = (cls.get("risk") or {}).get("score")
    if risk is None:
        risk = inject.get("risk_score", 0)
    stranger = cls.get("stranger")
    if stranger is None:
        stranger = inject.get("stranger")
    badge = "QUARANTINE" if stranger else "ADMIT"
    wired = admission.get("ok") and probes_ok and panic_ok
    status = "WIRED" if wired else "DEGRADED"
    watch_bit = "watch=ok" if watch_ok else "watch=stale"
    return (
        f"SASCIP {status} · {resolved} · {tier} · risk {risk} · {badge} · "
        f"probes={'PASS' if probes_ok else 'FAIL'} · panic={'clear' if panic_ok else 'ON'} · {watch_bit}"
    )


def _patch_live_surfaces(*, safety_line: str, admission: dict, chains: dict) -> None:
    surf = _read_json(SURFACES)
    if not surf:
        return
    surf["sascip_line"] = safety_line
    surf["sascip_safety_line"] = safety_line
    inject = admission.get("inject") or {}
    surf["stranger_agent_safety"] = {
        "live_wire_receipt": str(RECEIPT),
        "admission_receipt": str(SASCIP_RECEIPT),
        "trust_tier": (admission.get("classification") or {}).get("trust_tier") or inject.get("trust_tier"),
        "resolved_agent_id": (admission.get("classification") or {}).get("resolved_agent_id") or inject.get("resolved_agent_id"),
        "stranger": (admission.get("classification") or {}).get("stranger") if "classification" in admission else inject.get("stranger"),
        "risk_score": ((admission.get("classification") or {}).get("risk") or {}).get("score") or inject.get("risk_score"),
        "cross_lane_policy": (admission.get("control") or {}).get("cross_lane_writes") or inject.get("cross_lane_policy"),
        "chains": chains,
        "synced_at": _now(),
    }
    SURFACES.write_text(json.dumps(surf, indent=2) + "\n", encoding="utf-8")


def run_stranger_agent_safety_live_wire(
    *,
    role: str = "any",
    agent_id: str = "cursor",
    tier: str = "session",
    skip_admission: bool = False,
    explicit_order: str = "",
    run_watch: bool | None = None,
) -> dict:
    t0 = time.monotonic()
    steps: list[dict] = []
    ok = True

    admission_age = _age_sec(SASCIP_RECEIPT)
    need_admit = tier == "full" or not skip_admission or admission_age is None or admission_age > 120
    if need_admit:
        cmd = [
            PY,
            str(SCRIPTS / "stranger_agent_safety_pipeline_v1.py"),
            "--role",
            role,
            "--agent",
            agent_id,
            "--json",
        ]
        if explicit_order.strip():
            cmd.extend(["--explicit-order", explicit_order])
        code, out = _run(cmd, timeout=45)
        admission = _parse_json(out)
        step_ok = code == 0 and str(admission.get("schema", "")).startswith("stranger-agent-admission")
        step_ok = step_ok or bool(admission.get("skipped"))
        steps.append(
            {
                "stage": "ADMIT",
                "step": "stranger_agent_safety_pipeline",
                "ok": step_ok,
                "exit": code,
                "trust_tier": (admission.get("classification") or {}).get("trust_tier"),
                "stranger": (admission.get("classification") or {}).get("stranger"),
                "admission_ok": admission.get("ok"),
            }
        )
        ok = ok and step_ok and bool(admission.get("ok", True) or admission.get("skipped"))
    else:
        admission = _read_json(SASCIP_RECEIPT)
        steps.append(
            {
                "stage": "ADMIT",
                "step": "stranger_agent_safety_pipeline",
                "ok": bool(admission.get("ok", True)),
                "exit": 0,
                "note": f"fresh age_sec={round(admission_age or 0, 1)}",
                "trust_tier": (admission.get("classification") or {}).get("trust_tier"),
            }
        )
        ok = ok and bool(admission.get("ok", True))

    cls = admission.get("classification") or {}
    resolved = cls.get("resolved_agent_id") or (admission.get("inject") or {}).get("resolved_agent_id") or agent_id
    probe_agent = resolved if resolved not in ("unknown", "") else agent_id

    probes = _run_sentinel_probes(agent=probe_agent, explicit_order=explicit_order)
    steps.append({"stage": "PROBE", "step": "cross_lane_sentinels", **probes})
    ok = ok and bool(probes.get("ok"))

    if tier == "session":
        sys.path.insert(0, str(SCRIPTS))
        from stranger_agent_safety_lib_v1 import clear_stale_unattended_panic  # noqa: WPS433

        panic_heal = clear_stale_unattended_panic()
        if panic_heal.get("cleared"):
            steps.append({"stage": "PANIC", "step": "clear_stale_unattended", **panic_heal})

    panic = _panic_state()
    steps.append({"stage": "PANIC", "step": "cancel_and_emergency_flags", **panic})
    if panic.get("active"):
        ok = False

    watch_ok = True
    watch_age = _age_sec(WATCH_RECEIPT)
    do_watch = run_watch if run_watch is not None else (tier == "full" or watch_age is None or watch_age > 600)
    if do_watch:
        sys.path.insert(0, str(SCRIPTS))
        try:
            from stranger_agent_safety_lib_v1 import run_watch_pulse  # noqa: WPS433

            watch = run_watch_pulse()
            watch_ok = bool(watch.get("ok", True))
            steps.append(
                {
                    "stage": "WATCH",
                    "step": "watch_pulse",
                    "ok": watch_ok,
                    "fingerprints": watch.get("fingerprint_count"),
                }
            )
        except Exception as exc:
            watch_ok = False
            steps.append({"stage": "WATCH", "step": "watch_pulse", "ok": False, "error": str(exc)})
            if tier == "full":
                ok = False
    else:
        steps.append(
            {
                "stage": "WATCH",
                "step": "watch_pulse",
                "ok": True,
                "note": f"skipped fresh age_sec={round(watch_age or 0, 1)}",
            }
        )

    if cls.get("trust_tier") == "T6_hostile_block":
        ok = False
        steps.append({"stage": "CONTROL", "step": "hostile_tier", "ok": False, "tier": "T6_hostile_block"})

    elapsed = round(time.monotonic() - t0, 2)
    within_budget = elapsed <= SESSION_BUDGET_SEC if tier == "session" else True
    if tier == "session" and not within_budget:
        ok = False

    chains = {
        "admission": bool(admission.get("ok", True) or admission.get("skipped")),
        "sentinel_probes": bool(probes.get("ok")),
        "panic_clear": bool(panic.get("ok")),
        "watch": watch_ok,
        "stranger_quarantine": bool(cls.get("stranger")) and not explicit_order.strip(),
    }
    safety_line = _compose_safety_line(
        admission=admission,
        probes_ok=bool(probes.get("ok")),
        panic_ok=bool(panic.get("ok")),
        watch_ok=watch_ok,
    )

    receipt = {
        "schema": "stranger-agent-safety-live-wire-v1",
        "ok": ok,
        "at": _now(),
        "role": role,
        "tier": tier,
        "law": "docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md",
        "sascip_safety_line": safety_line,
        "admission": {
            "ok": admission.get("ok"),
            "stranger": cls.get("stranger"),
            "trust_tier": cls.get("trust_tier"),
            "resolved_agent_id": resolved,
            "risk_score": (cls.get("risk") or {}).get("score"),
            "cross_lane_writes": (admission.get("control") or {}).get("cross_lane_writes"),
            "receipt_path": str(SASCIP_RECEIPT),
        },
        "panic": panic,
        "chains": chains,
        "elapsed_sec": elapsed,
        "within_budget": within_budget,
        "steps": steps,
        "pre_write_guard": "python3 scripts/pre_write_guard_v1.py check --agent <id> --path <target> --json",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    _patch_live_surfaces(safety_line=safety_line, admission=admission, chains=chains)
    return receipt


def live_wire_payload(*, refresh: bool = False, role: str = "any") -> dict:
    """Hub/API read — refresh only when receipt missing or stale."""
    age = _age_sec(RECEIPT)
    if refresh or age is None or age > 300:
        return run_stranger_agent_safety_live_wire(role=role, tier="session", skip_admission=age is not None and age <= 120)
    row = _read_json(RECEIPT)
    row.setdefault("schema", "stranger-agent-safety-live-wire-v1")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Stranger agent safety live wire")
    ap.add_argument("--role", default="any")
    ap.add_argument("--agent", default="cursor")
    ap.add_argument("--tier", default="session", choices=["session", "full"])
    ap.add_argument("--skip-admission", action="store_true")
    ap.add_argument("--explicit-order", default="")
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_stranger_agent_safety_live_wire(
        role=args.role,
        agent_id=args.agent,
        tier=args.tier,
        skip_admission=args.skip_admission,
        explicit_order=args.explicit_order,
        run_watch=True if args.watch else None,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("sascip_safety_line") or row.get("ok"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
