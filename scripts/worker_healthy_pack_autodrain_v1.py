#!/usr/bin/env python3
"""Headless healthy-pack drain — one broker turn per loop iteration (Worker law)."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
sys.path.insert(0, str(SCRIPTS))
from healthy_pack_bind_lib_v1 import clear_stale_turn_bind, heal_bind_mismatch  # noqa: E402
from healthy_queue_ssot_lib import REGISTRY_PATH, healthy_queue_path, healthy_queue_state_path, queue_items  # noqa: E402

# SA-specific disk validators (achievable pack — no live eval)
SA_VALIDATORS: dict[str, str] = {
    "sa-0099": "validate-eval-packet-v1b-strict-without-live-env-v1.sh",
    "sa-0109": "validate-graph-executor-pos-dispatch-v1.sh",
    "sa-0111": "validate-eval-packet-v1b-scorer-plan-paths-v1.sh",
    "sa-0112": "validate-eval-packet-v1b-retrieve-dispatch-grounding-v1.sh",
    "sa-0113": "validate-eval-packet-v1b-factory-runreceipt-grounding-v1.sh",
    "sa-0114": "validate-eval-packet-v1b-l8-hybrid-grounding-v1.sh",
    "sa-0116": "validate-eval-critic-synthesis-alignment-v1.sh",
    "sa-0117": "validate-eval-packet-v1b-strict-build-chain-v1.sh",
    "sa-0118": "validate-eval-critic-claim-v1.sh",
    "sa-0119": "validate-synthesis-eval-line-v1.sh",
    "sa-0120": "validate-council-strategic-brief-eval-v1.sh",
    "sa-0122": "validate-dispatch-classifier-task-ids-v1.sh",
    "sa-0123": "validate-graph-executor-gate-honesty-v1.sh",
    "sa-0124": "validate-governance-drift-v1.sh",
    "sa-0128": "validate-eval-packet-v1b-bugfix-gate-grounding-v1.sh",
    "sa-0130": "validate-dispatch-ready-lock-v1.sh",
    "sa-0132": "validate-governance-fleet-nudges-ssot-v1.sh",
    "sa-0133": "validate-dispatch-policy-classes-v1.sh",
    "sa-0134": "validate-graph-executor-pos-dispatch-v1.sh",
    "sa-0318": "validate-batch-sa-0318-0424-v1.sh",
    "sa-0320": "validate-batch-sa-0318-0424-v1.sh",
    "sa-0324": "validate-governance-fleet-v1.sh",
    "sa-0403": "validate-spine-bridge-founder-v1.sh",
    "sa-0413": "validate-graph-executor-pos-dispatch-v1.sh",
    "sa-0425": "validate-spine-proof-priority-v1.sh",
    "sa-0485": "validate-dispatch-classifier-task-ids-v1.sh",
}

_REGISTRY_CACHE: dict | None = None


def _registry_plans() -> dict[str, dict]:
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None:
        return _REGISTRY_CACHE
    try:
        reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        _REGISTRY_CACHE = {str(p.get("id") or ""): p for p in reg.get("plans") or []}
    except (OSError, json.JSONDecodeError):
        _REGISTRY_CACHE = {}
    return _REGISTRY_CACHE


def _validator_for_sa(sa_id: str) -> str | None:
    if sa_id in SA_VALIDATORS:
        return SA_VALIDATORS[sa_id]
    plan = _registry_plans().get(sa_id) or {}
    blob = " ".join(
        str(plan.get(k) or "")
        for k in ("verify", "title", "agent_prompt")
    )
    m = re.search(r"(validate-[\w-]+\.sh)", blob)
    if m and (SCRIPTS / m.group(1)).is_file():
        return m.group(1)
    return None


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 180) -> tuple[int, str]:
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd or SCRIPTS,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**dict(__import__("os").environ), "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"},
        )
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode, out.strip()
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"
    except OSError as exc:
        return 1, str(exc)


def _queue_item_at_cursor() -> dict:
    try:
        st = json.loads(healthy_queue_state_path().read_text(encoding="utf-8"))
        pos = int(st.get("next_pos") or 1)
        q = json.loads(healthy_queue_path().read_text(encoding="utf-8"))
        items = queue_items(q)
        if pos > len(items):
            return {}
        return items[pos - 1]
    except (OSError, json.JSONDecodeError, IndexError, ValueError):
        return {}


def _queue_cursor() -> tuple[str, str, bool]:
    item = _queue_item_at_cursor()
    if not item:
        try:
            st = json.loads(healthy_queue_state_path().read_text(encoding="utf-8"))
            pos = int(st.get("next_pos") or 1)
            q = json.loads(healthy_queue_path().read_text(encoding="utf-8"))
            if pos > len(queue_items(q)):
                return "", "", True
        except (OSError, json.JSONDecodeError, ValueError):
            pass
        return "", "", False
    return str(item.get("sa_id") or ""), str(item.get("queue_role") or ""), False


def _orch_status() -> dict:
    code, out = _run([sys.executable, str(SCRIPTS / "healthy-drain-orchestrator-v1.py"), "status"])
    if code != 0:
        return {"ok": False, "error": out[:500]}
    raw = json.loads(out)
    orch = raw.get("orchestrator") or raw
    return {
        "ok": raw.get("ok", True),
        "status": orch.get("status"),
        "expected_sa": orch.get("expected_sa"),
        "expected_role": orch.get("expected_role"),
        "stop_reason": orch.get("stop_reason"),
        "state": orch,
    }


def _run_sa_validator(sa_id: str) -> tuple[bool, str]:
    v = _validator_for_sa(sa_id)
    if not v:
        return True, "no mapped validator — disk preflight only"
    path = SCRIPTS / v
    if not path.is_file():
        return False, f"missing validator {v}"
    code, out = _run(["bash", v], timeout=120)
    line = out.splitlines()[-1] if out else ""
    return code == 0, line or out[-300:]


def _run_verify_bundle() -> tuple[bool, str]:
    code, out = _run(["bash", "worker_verify_ultra_v1.sh"], timeout=30)
    if code != 0:
        return False, f"worker_verify_ultra_v1 FAIL: {out[-400:]}"
    return True, out.splitlines()[-1] if out else "worker_verify_ultra ok"


def _read_queue_pos() -> int:
    try:
        st = json.loads(healthy_queue_state_path().read_text(encoding="utf-8"))
        return int(st.get("next_pos") or 1)
    except (OSError, json.JSONDecodeError, ValueError):
        return 1


def _advance_queue() -> dict:
    code, out = _run([sys.executable, str(SCRIPTS / "advance-healthy-queue-v1.py")], timeout=30)
    if code != 0:
        return {"ok": False, "error": out[:500]}
    try:
        row = json.loads(out)
        return {"ok": True, **row}
    except json.JSONDecodeError:
        return {"ok": False, "raw": out[:500]}


def _broker_submit(report: dict) -> dict:
    lines = ["status: WORKER_ROUND_REPORT"]
    for k, val in report.items():
        if k == "status":
            continue
        if isinstance(val, bool):
            lines.append(f"{k}: {'true' if val else 'false'}")
        elif isinstance(val, int):
            lines.append(f"{k}: {val}")
        else:
            s = str(val).replace('"', '\\"')
            if ":" in s or len(s) > 80:
                lines.append(f'{k}: "{s}"')
            else:
                lines.append(f"{k}: {s}")
    body = "\n".join(lines) + "\n"
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "goal1_lane_broker.py"), "worker-submit", "--stdin"],
        input=body,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=120,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        return {"ok": False, "error": out[:800]}
    if "ok: true" in out.lower() or "ok: True" in out:
        exhausted = "done_all_30: true" in out or "stop_reason: queue_exhausted" in out
        return {"ok": True, "raw": out[:2000], "done_all_30": exhausted, "exhausted": exhausted}
    return {"ok": False, "error": out[:800]}


def _sync_deliver() -> None:
    heal_bind_mismatch(force_deliver=True)


def _one_turn() -> dict:
    from factory_spawn_gate_v1 import turn_allowed  # noqa: WPS433

    gate = turn_allowed(caller="worker_healthy_pack_autodrain:turn")
    if not gate.get("ok"):
        return {"ok": False, "stopped_by_flag": True, "gate": gate}
    _sync_deliver()
    item = _queue_item_at_cursor()
    expected_sa, expected_role, exhausted = _queue_cursor()
    if exhausted:
        return {"ok": True, "exhausted": True}
    expected_role = expected_role.lower()
    if not expected_sa or not expected_role:
        st = _orch_status()
        if st.get("stop_reason") == "queue_exhausted":
            return {"ok": True, "exhausted": True}
        return {"ok": False, "error": "queue_cursor_empty"}

    phase = str(item.get("phase") or _registry_plans().get(expected_sa, {}).get("phase") or "phase-s1-eval-dispatch")

    sa_ok, sa_detail = _run_sa_validator(expected_sa)
    verify_ok, verify_detail = (True, "")
    if expected_role == "verify":
        verify_ok, verify_detail = _run_verify_bundle()
        task_v = _validator_for_sa(expected_sa)
        if task_v:
            code, out = _run(["bash", task_v], timeout=120)
            task_line = out.splitlines()[-1] if out else task_v
            if code != 0:
                verify_ok = False
                verify_detail = f"{task_v} FAIL: {out[-300:]}"
            else:
                sa_detail = task_line
                sa_ok = True

    passed = sa_ok and verify_ok
    summary_parts = [f"{expected_sa} {expected_role.upper()}"]
    summary_parts.append("PASS" if passed else "FAIL")
    if sa_detail:
        summary_parts.append(sa_detail[:120])

    built = expected_role == "verify" and passed
    report: dict = {
        "status": "WORKER_ROUND_REPORT",
        "sa_focus": expected_sa,
        "round_type": expected_role,
        "phase": phase,
        "summary": " — ".join(summary_parts),
        "critical_bugs": 0,
        "built": built,
        "gap": "none" if passed else "validator_fail",
        "disk_already_green": passed,
    }
    if expected_role == "check":
        report["next_action"] = "act" if passed else "NONE"
    elif expected_role == "act":
        report["next_action"] = "verify" if passed else "NONE"
    else:
        report["next_action"] = "NONE"
        if passed:
            v = _validator_for_sa(expected_sa) or "disk"
            report["summary"] = (
                f"{expected_sa} VERIFY — RECIPE: {v} · VALIDATION: {verify_detail[:200]} · "
                f"EVIDENCE: disk green · BUILT: true · closeout"
            )

    if not passed:
        report["critical_bugs"] = 1
        return {"ok": False, "passed": False, "report": report, "sa": expected_sa, "role": expected_role}

    pos_before = _read_queue_pos()
    clear_stale_turn_bind()
    br = _broker_submit(report)
    adv: dict = {}
    exhausted = False
    if br.get("ok"):
        pos_after = _read_queue_pos()
        if pos_after <= pos_before:
            adv = _advance_queue()
            nxt = adv.get("next_pos")
            total = int(adv.get("queue_total") or 0)
            if isinstance(nxt, int) and total and nxt > total:
                exhausted = True
        elif br.get("done_all_30"):
            exhausted = True
    brain_sync: dict = {}
    if expected_role == "verify" and br.get("ok"):
        try:
            from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

            brain_sync = sync_brain_snapshot(mode="light", caller=f"autodrain:{expected_sa}")
        except Exception as exc:
            brain_sync = {"ok": False, "error": str(exc)}
    if not exhausted:
        _, _, exhausted = _queue_cursor()
    return {
        "ok": br.get("ok"),
        "passed": True,
        "sa": expected_sa,
        "role": expected_role,
        "broker": br,
        "advanced": adv,
        "brain_sync": brain_sync,
        "exhausted": exhausted,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Autodrain healthy pack turns")
    p.add_argument("--max-turns", type=int, default=30)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    from factory_spawn_gate_v1 import exit_if_spawn_blocked  # noqa: WPS433

    exit_if_spawn_blocked("worker_healthy_pack_autodrain", json_mode=args.json)
    results = []
    for i in range(args.max_turns):
        r = _one_turn()
        results.append(r)
        if (i + 1) % 10 == 0:
            try:
                from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

                sync_brain_snapshot(mode="light", caller="autodrain:mid_pack")
            except Exception:
                pass
        if r.get("exhausted"):
            break
        if not r.get("ok") and not r.get("passed"):
            if args.json:
                print(json.dumps({"turn": i + 1, "results": results}, indent=2))
            return 1
    exhausted = results[-1].get("exhausted") if results else False
    brain_sync: dict = {}
    try:
        from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

        brain_sync = sync_brain_snapshot(
            mode="full" if exhausted else "light",
            caller="worker_healthy_pack_autodrain",
        )
    except Exception as exc:
        brain_sync = {"ok": False, "error": str(exc)}
    out = {
        "turns": len(results),
        "results": results,
        "exhausted": exhausted,
        "brain_sync": brain_sync,
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for r in results:
            print(f"{r.get('sa')} {r.get('role')} ok={r.get('ok')} exhausted={r.get('exhausted')}")
    return 0 if (not results or results[-1].get("exhausted") or all(x.get("ok") for x in results)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
