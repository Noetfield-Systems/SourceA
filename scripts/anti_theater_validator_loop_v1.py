#!/usr/bin/env python3
"""Anti-theater validator loop PRO — unified fail-closed orchestrator.

Receipt: ~/.sina/anti-theater-validator-loop-receipt-v1.json
Law: data/anti-theater-validator-loop-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "anti-theater-validator-loop-v1.json"
RECEIPT = SINA / "anti-theater-validator-loop-receipt-v1.json"
FIXTURES = ROOT / "scripts" / "fixtures" / "anti-theater-negative-v1"

GUARD_VALIDATORS: tuple[tuple[str, str, int], ...] = (
    ("form_founder_supremacy", "validate-form-founder-supremacy-v1.sh", 120),
    ("ui_zero_drift", "validate-ui-zero-drift-v1.sh", 180),
    ("founder_no_invitation", "validate-founder-no-invitation-v1.sh", 60),
    ("anti_staleness_vocab", "validate-anti-staleness-vocabulary-gate-v1.sh", 300),
)


def _bash_gate(check_id: str, script_name: str, *, timeout: int = 180) -> dict:
    import subprocess

    script = ROOT / "scripts" / script_name
    if not script.is_file():
        return {"id": check_id, "ok": False, "tail": f"missing {script_name}"}
    try:
        proc = subprocess.run(
            ["bash", str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        lines = (proc.stdout or proc.stderr or "").strip().splitlines()
        tail = lines[-1][:200] if lines else f"exit {proc.returncode}"
        return {"id": check_id, "ok": proc.returncode == 0, "exit": proc.returncode, "tail": tail}
    except subprocess.TimeoutExpired:
        return {"id": check_id, "ok": False, "exit": -1, "tail": "timeout"}
    except OSError as exc:
        return {"id": check_id, "ok": False, "exit": -1, "tail": str(exc)[:120]}


sys.path.insert(0, str(ROOT / "scripts"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def run_loop(*, write: bool = True, heal: bool = False) -> dict:
    ssot = _read(SSOT)
    checks: list[dict] = []
    violations: list[dict] = []

    if heal:
        from outbound_queue_coherence_v1 import heal_all  # noqa: WPS433

        heal_row = heal_all(write=True)
        checks.append(
            {
                "id": "queue_coherence_heal",
                "ok": bool((heal_row.get("coherence") or {}).get("ok")),
                "healed": heal_row.get("steps"),
            }
        )
        if not (heal_row.get("coherence") or {}).get("ok"):
            violations.append(
                {
                    "check": "queue_coherence_heal",
                    "issues": (heal_row.get("coherence") or {}).get("issues"),
                }
            )

    from validate_outbound_forbidden_sources_v1 import scan_paths as forbidden_scan  # noqa: WPS433

    fb = forbidden_scan()
    checks.append({"id": "forbidden_and_ship_scan", "ok": bool(fb.get("ok"))})
    if not fb.get("ok"):
        violations.extend(fb.get("violations") or [])

    from validate_ship_authority_v1 import validate as ship_validate  # noqa: WPS433

    ship = ship_validate()
    checks.append({"id": "ship_authority", "ok": bool(ship.get("ok"))})
    if not ship.get("ok"):
        violations.extend(ship.get("violations") or [])

    from execution_plane_honesty_v1 import assess_execution_plane  # noqa: WPS433

    honesty = assess_execution_plane()
    checks.append({"id": "execution_plane_honesty", "ok": bool(honesty.get("ok"))})
    if not honesty.get("ok"):
        violations.append({"check": "execution_plane_honesty", "issues": honesty.get("issues")})

    from validate_outbound_plan_execution_proof_v1 import validate as proof_validate  # noqa: WPS433

    proof = proof_validate()
    checks.append({"id": "outbound_plan_proof", "ok": bool(proof.get("ok"))})
    if not proof.get("ok"):
        violations.extend(proof.get("violations") or [])

    from outbound_queue_coherence_v1 import assess_queue_coherence  # noqa: WPS433

    coherence = assess_queue_coherence()
    checks.append({"id": "queue_coherence", "ok": bool(coherence.get("ok"))})
    if not coherence.get("ok"):
        violations.extend({"check": "queue_coherence", "issue": x} for x in (coherence.get("issues") or []))

    research_accounts = (ssot.get("loop_chain") or {}).get("research_accounts") or ["fundmore", "ocree"]
    from outbound_research_checklist_v1 import preflight  # noqa: WPS433

    research_ok = True
    research_rows: dict = {}
    for acct in research_accounts:
        pf = preflight(str(acct))
        research_rows[str(acct)] = pf
        if not pf.get("ok"):
            research_ok = False
    checks.append({"id": "research_checklist_preflight", "ok": research_ok, "accounts": research_rows})

    from best_loop_oqg_score_v1 import verify_noun_stack_regression  # noqa: WPS433

    noun = verify_noun_stack_regression()
    checks.append({"id": "oqg_noun_stack_smoke", "ok": bool(noun.get("ok"))})

    from agent_nerve_system_v1 import validate_rrl_not_ship_ready  # noqa: WPS433

    rrl_gate = validate_rrl_not_ship_ready()
    checks.append(
        {
            "id": "w3_rrl_ship_gate",
            "ok": bool(rrl_gate.get("ok")),
            "upgrade": rrl_gate.get("upgrade"),
            "w3_rrl_pass": rrl_gate.get("w3_rrl_pass"),
            "w3_send_ready": rrl_gate.get("w3_send_ready"),
        }
    )
    if not rrl_gate.get("ok"):
        violations.append({"check": "w3_rrl_ship_gate", "detail": rrl_gate})

    from commercial_email_send_defer_v1 import validate_defer_wire  # noqa: WPS433

    defer_gate = validate_defer_wire()
    checks.append(
        {
            "id": "email_send_defer",
            "ok": bool(defer_gate.get("ok")),
            "defer_active": defer_gate.get("defer_active"),
            "workers_online": defer_gate.get("workers_online"),
            "sites_online": defer_gate.get("sites_online"),
            "w3_send_ready": defer_gate.get("w3_send_ready"),
        }
    )
    if not defer_gate.get("ok"):
        violations.append({"check": "email_send_defer", "detail": defer_gate})

    try:
        from portfolio_fix_plan_pulse_v1 import run_pulse  # noqa: WPS433

        pf_row = run_pulse(wire=False)
        pf_ok = bool(pf_row.get("ok"))
        checks.append(
            {
                "id": "portfolio_fix_plan",
                "ok": pf_ok,
                "line": pf_row.get("portfolio_fix_line"),
                "phase": pf_row.get("phase"),
            }
        )
        if not pf_ok:
            violations.append({"check": "portfolio_fix_plan", "detail": pf_row.get("portfolio_fix_line")})
    except Exception as exc:
        checks.append({"id": "portfolio_fix_plan", "ok": False, "error": str(exc)[:120]})
        violations.append({"check": "portfolio_fix_plan", "detail": str(exc)[:120]})

    from founder_execution_model_v1 import assess as founder_exec_assess  # noqa: WPS433

    founder_gate = founder_exec_assess()
    checks.append(
        {
            "id": "founder_execution_model",
            "ok": bool(founder_gate.get("ok")),
            "mac_role": founder_gate.get("mac_role"),
            "cloud_role": founder_gate.get("cloud_role"),
            "founder_rules": founder_gate.get("founder_rules"),
        }
    )
    if not founder_gate.get("ok"):
        violations.append({"check": "founder_execution_model", "detail": founder_gate})

    from cloud_factories_online_only_v1 import assess as cloud_online_assess  # noqa: WPS433

    cloud_online_gate = cloud_online_assess(write=False)
    checks.append(
        {
            "id": "cloud_factories_online_only",
            "ok": bool(cloud_online_gate.get("ok")),
            "passed": cloud_online_gate.get("passed"),
            "total": cloud_online_gate.get("total"),
            "fbe_public_url": cloud_online_gate.get("fbe_public_url"),
        }
    )
    if not cloud_online_gate.get("ok"):
        violations.append({"check": "cloud_factories_online_only", "issues": cloud_online_gate.get("issues")})

    from mac_law_mandatory_v1 import assess as mac_law_assess  # noqa: WPS433

    mac_law_gate = mac_law_assess(enforce=False)
    checks.append(
        {
            "id": "mac_law_mandatory",
            "ok": bool(mac_law_gate.get("ok")),
            "control_plane": (mac_law_gate.get("control_plane") or {}).get("ok"),
            "health_mandates": (mac_law_gate.get("health_mandates") or {}).get("ok"),
        }
    )
    if not mac_law_gate.get("ok"):
        violations.append({"check": "mac_law_mandatory", "detail": mac_law_gate})

    from mac_law_universal_wire_v1 import assess as mac_uw_assess  # noqa: WPS433

    mac_uw_gate = mac_uw_assess()
    checks.append(
        {
            "id": "mac_law_universal_wire",
            "ok": bool(mac_uw_gate.get("ok")),
            "line": (mac_uw_gate.get("line") or "")[:120],
        }
    )
    if not mac_uw_gate.get("ok"):
        violations.append({"check": "mac_law_universal_wire", "issues": mac_uw_gate.get("issues")})

    from mac_law_agent_execution_plane_lock_v1 import assess as mac_lock_assess  # noqa: WPS433

    mac_lock_gate = mac_lock_assess(sync_stack=False)
    checks.append(
        {
            "id": "mac_law_agent_execution_plane_lock",
            "ok": bool(mac_lock_gate.get("ok")),
            "line": (mac_lock_gate.get("line") or "")[:120],
        }
    )
    if not mac_lock_gate.get("ok"):
        violations.append({"check": "mac_law_agent_execution_plane_lock", "issues": mac_lock_gate.get("issues")})

    for check_id, script_name, timeout_sec in GUARD_VALIDATORS:
        gate = _bash_gate(check_id, script_name, timeout=timeout_sec)
        checks.append(gate)
        if not gate.get("ok"):
            violations.append({"check": check_id, "tail": gate.get("tail")})

    passed = sum(1 for c in checks if c.get("ok"))
    total = len(checks)
    sina_pending = int(ship.get("sina_pending") or 0)
    forbidden_n = int((fb.get("forbidden_scan") or {}).get("violation_count") or 0)
    ok = passed == total and len(violations) == 0

    row = {
        "schema": "anti-theater-validator-loop-receipt-v1",
        "at": _now(),
        "ok": ok,
        "one_law": ssot.get("one_law"),
        "anti_theater_line": (
            f"Anti-theater · {passed}/{total} PASS · forbidden={forbidden_n} · "
            f"honesty={'OK' if honesty.get('ok') else 'RED'} · sina_pending={sina_pending}"
        ),
        "checks": checks,
        "passed": passed,
        "total": total,
        "forbidden_scan": fb,
        "ship_authority": ship,
        "execution_honesty": {
            "ok": honesty.get("ok"),
            "line": honesty.get("execution_honesty_line"),
            "passed": honesty.get("passed"),
            "total": honesty.get("total"),
        },
        "outbound_proof": {
            "ok": proof.get("ok"),
            "verified_done": proof.get("verified_done"),
            "done_total": proof.get("done_total"),
        },
        "queue_coherence": {"ok": coherence.get("ok"), "issues": coherence.get("issues")},
        "w3_rrl_ship_gate": rrl_gate,
        "email_send_defer": defer_gate,
        "sina_pending": sina_pending,
        "violation_count": len(violations),
        "violations": violations[:20],
        "ssot": str(SSOT.relative_to(ROOT)),
        "hub_api": "POST /api/anti-theater-loop/tick/v1",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def run_regression() -> dict:
    from validate_outbound_forbidden_sources_v1 import scan_forbidden_text  # noqa: WPS433

    fixture_paths = list(FIXTURES.glob("*")) if FIXTURES.is_dir() else []
    fixture_scan = (
        scan_forbidden_text(fixture_paths, exclude_subpaths=())
        if fixture_paths
        else {"ok": False, "violation_count": 0}
    )
    prod_scan = scan_forbidden_text(
        [
            ROOT / "scripts",
            ROOT / "data",
            SINA / "outbound",
        ]
    )
    ok = bool(fixture_scan.get("violation_count", 0) >= 1) and bool(prod_scan.get("ok"))
    return {
        "ok": ok,
        "fixture_must_fail": fixture_scan,
        "production_must_pass": prod_scan,
    }


def hub_slice() -> dict:
    row = _read(RECEIPT)
    if not row or row.get("schema") != "anti-theater-validator-loop-receipt-v1":
        row = run_loop(write=True)
    return {
        "schema": "worker-hub-anti-theater-loop-v1",
        "ok": bool(row.get("ok")),
        "anti_theater_line": row.get("anti_theater_line"),
        "passed": row.get("passed"),
        "total": row.get("total"),
        "sina_pending": row.get("sina_pending"),
        "violation_count": row.get("violation_count"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Anti-theater validator loop PRO")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--regression", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--heal", action="store_true", help="Heal queue coherence before assess")
    args = ap.parse_args()
    if args.regression:
        row = run_regression()
    elif args.hub_slice:
        row = hub_slice()
    else:
        row = run_loop(write=not args.no_write, heal=args.heal)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("anti_theater_line") or row.get("ok"))
    ok = bool(row.get("ok"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
