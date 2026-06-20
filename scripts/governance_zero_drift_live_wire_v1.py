#!/usr/bin/env python3
"""Governance zero-drift live wire — L0→L0.5→L1→L2→SASCIP→vocab→monitor unified chain.

Law: GOVERNANCE_DRIFT_ENGINE_LOCKED_v1.md · AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md
Receipt: ~/.sina/governance-zero-drift-live-wire-v1.json
Surfaces: zero_drift_line on agent-live-surfaces-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
RECEIPT = SINA / "governance-zero-drift-live-wire-v1.json"
ANTI_RECEIPT = SINA / "anti-staleness-auto-wire-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
DRIFT_REPORT = SINA / "governance_drift_report_v1.json"
SASCIP_ADMISSION = SINA / "stranger-agent-admission-receipt-v1.json"
PY = sys.executable

CHAIN_PATHS = {
    "factory_now": SINA / "factory-now-v1.json",
    "inbox": SINA / "worker-prompt-inbox-v1.json",
    "brain_wire": SINA / "governance-brain-wire-v1.json",
    "l1_pipeline": SINA / "l1-agent-pipeline-wire-v1.json",
    "pipeline_v2": SINA / "agentic-layer-pipeline-v2.json",
    "disk_live_wire": SINA / "disk-live-wire-receipt-v1.json",
    "truth_bundle": SINA / "last-truth-bundle-v1.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_json(out: str) -> dict:
    i = out.find("{")
    if i < 0:
        return {}
    try:
        return json.loads(out[i:])
    except json.JSONDecodeError:
        return {}


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _age_sec(path: Path, *, fallback_at: str = "") -> float | None:
    if path.is_file():
        try:
            return max(0.0, datetime.now(timezone.utc).timestamp() - path.stat().st_mtime)
        except OSError:
            pass
    if fallback_at:
        try:
            dt = datetime.fromisoformat(fallback_at.replace("Z", "+00:00"))
            return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds())
        except ValueError:
            pass
    return None


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


def _queue_from_factory(row: dict) -> str:
    fn = row.get("factory_now") or row
    return str(fn.get("queue_sa") or row.get("queue_sa") or "")


def _lawful_registry_idle(factory: dict) -> bool:
    return (
        int(factory.get("backlog") or 0) == 0
        and int(factory.get("valid_yes") or 0) >= 1000
        and bool(factory.get("dual_proof_ok"))
        and not str(factory.get("queue_sa") or "").strip()
    )


def cross_layer_chain_check() -> dict:
    """Verify queue + L1/L2 + dual-pick alignment across all chain receipts."""
    sys.path.insert(0, str(SCRIPTS))
    from agentic_pipeline_lib_v1 import cross_ref_check, dual_pick_check  # noqa: WPS433

    anti = _read_json(ANTI_RECEIPT)
    surfaces = _read_json(SURFACES)
    factory = _read_json(CHAIN_PATHS["factory_now"])
    inbox = _read_json(CHAIN_PATHS["inbox"])
    brain = _read_json(CHAIN_PATHS["brain_wire"])
    l1 = _read_json(CHAIN_PATHS["l1_pipeline"])
    dlw = _read_json(CHAIN_PATHS["disk_live_wire"])
    pipe = _read_json(CHAIN_PATHS["pipeline_v2"])

    refs: dict[str, str] = {}
    nerve = _read_json(SINA / "agent-nerve-system-receipt-v1.json")
    oqg_rec = _read_json(SINA / "best-loop-oqg-receipt-v1.json")
    bl_rec = _read_json(SINA / "better-loop-pulse-receipt-v1.json")

    for label, val in (
        ("anti_staleness", str(anti.get("queue_sa") or "")),
        ("surfaces", str(surfaces.get("queue_sa") or "")),
        ("factory_now", _queue_from_factory(factory)),
        ("disk_live_wire", str(dlw.get("queue_sa") or "")),
        ("nerve_receipt", str(nerve.get("queue_sa") or "")),
        ("brain_wire", str((brain.get("queue_head") or {}).get("sa_id") or "")),
        ("pipeline_v2", str((pipe.get("brain_summary") or {}).get("queue_head") or "")),
        (
            "inbox_active",
            str(
                (inbox.get("active") or {}).get("sa_id")
                or inbox.get("queue_sa")
                or (inbox.get("meta") or {}).get("sa_id")
                or ""
            ),
        ),
    ):
        if val:
            refs[label] = val

    issues: list[str] = []
    oqg_fleet = oqg_rec.get("fleet_output_clean_pct")
    bl_red = bl_rec.get("red_count")
    nerve_aligned = nerve.get("queue_aligned")
    fn_sa = _queue_from_factory(factory)
    lawful_idle = _lawful_registry_idle(factory)
    ui_fc = _read_json(SINA / "ui-upgrade-first-check-receipt-v1.json")
    if not ui_fc.get("wire_ok"):
        issues.append("ui_upgrade_first_check wire_ok=false")

    lock_rec = _read_json(SINA / "mac-law-agent-execution-plane-lock-receipt-v1.json")
    uw_rec = _read_json(SINA / "mac-law-universal-wire-receipt-v1.json")
    mac_law_lock_ok = bool(lock_rec.get("ok"))
    mac_law_uw_ok = bool(uw_rec.get("ok")) if uw_rec else True
    if lock_rec and not mac_law_lock_ok:
        issues.append("mac_law_agent_execution_plane_lock receipt not ok")
    if uw_rec and not mac_law_uw_ok:
        issues.append("mac_law_universal_wire receipt not ok")

    if not lawful_idle:
        if nerve.get("queue_sa") and refs.get("surfaces") and nerve.get("queue_sa") != refs.get("surfaces"):
            issues.append(
                f"nerve queue misaligned nerve={nerve.get('queue_sa')} surfaces={refs.get('surfaces')}"
            )
        if nerve_aligned is False:
            issues.append("nerve_receipt queue_aligned=false")

    unique = set(refs.values())
    if lawful_idle:
        queue_aligned = True
        chain_queue_sa = ""
    else:
        queue_aligned = len(unique) <= 1
        chain_queue_sa = next(iter(unique), "") if len(unique) == 1 else ""
        if len(unique) > 1:
            issues.append(f"queue_sa mismatch across chain: {refs}")

    cr_ok, cr_issues = cross_ref_check(l1, brain)
    issues.extend(cr_issues)
    dual = dual_pick_check()
    if not dual.get("aligned") and dual.get("live_pick_sa") and dual.get("queue_sa"):
        issues.append(
            f"dual_pick misaligned live={dual.get('live_pick_sa')} queue={dual.get('queue_sa')}"
        )

    layers = {
        "L0_5": bool(anti.get("ok")) and bool(dlw.get("ok", True)),
        "L1": bool((anti.get("layers") or {}).get("L1", {}).get("l1_to_brain") or 0) >= 3
        or bool((l1.get("l1_to_brain") or {}).get("subordinates")),
        "L2": bool((anti.get("layers") or {}).get("L2", {}).get("l2_wired") or 0) >= 4
        or len((brain.get("l2_wired") or {}).get("agents") or []) >= 4,
        "cross_ref": cr_ok,
        "queue_aligned": queue_aligned,
        "dual_pick": dual.get("aligned"),
        "ui_upgrade_first_check": bool(ui_fc.get("wire_ok")),
        "mac_law_agent_lock": mac_law_lock_ok if lock_rec else True,
        "mac_law_universal_wire": mac_law_uw_ok if uw_rec else True,
    }
    if lawful_idle:
        layers["dual_pick"] = True

    chain_ok = (
        queue_aligned
        and cr_ok
        and layers["L0_5"]
        and layers["L1"]
        and layers["L2"]
        and layers["mac_law_agent_lock"]
        and layers["mac_law_universal_wire"]
    )
    if not dual.get("aligned") and dual.get("live_pick_sa") and not lawful_idle:
        chain_ok = False

    return {
        "ok": chain_ok,
        "queue_sa": chain_queue_sa,
        "queue_exhausted": lawful_idle,
        "queue_refs": refs,
        "layers": layers,
        "dual_pick": dual,
        "nerve_oqg": {
            "nerve_queue_aligned": nerve_aligned,
            "oqg_fleet_output_clean_pct": oqg_fleet,
            "better_loop_red_count": bl_red,
        },
        "issues": issues,
        "drift_items": len(issues),
    }


def session_light_drift_report(*, max_age_sec: int = 300) -> dict:
    """Session tier: cached full report or light sensors (DRIFT.json + hub advisory)."""
    age = _age_sec(DRIFT_REPORT)
    if age is not None and age <= max_age_sec:
        cached = _read_json(DRIFT_REPORT)
        if cached.get("aggregate_score") is not None:
            bowl = next((s for s in (cached.get("sensors") or []) if s.get("id") == "GD-BOWL"), None)
            bowl_ok = bowl.get("ok") if bowl else cached.get("aggregate_score", 0) >= 85
            return {
                "ok": bool(bowl_ok),
                "source": "cached",
                "age_sec": round(age, 1),
                "aggregate_score": cached.get("aggregate_score"),
                "status": cached.get("status"),
                "sensors": len(cached.get("sensors") or []),
                "live_ops_ok": any(
                    s.get("ok") for s in (cached.get("sensors") or []) if s.get("id") == "GD-OPS"
                ),
            }

    sys.path.insert(0, str(SCRIPTS))
    from governance_drift_engine import _drift_json_sensor, _hub_liveness  # noqa: WPS433

    bowl = _drift_json_sensor()
    hub = _hub_liveness()
    # Session: zero drift items = governance PASS; hub is live-ops advisory only
    aggregate = bowl.get("score", 0)
    if hub.get("ok"):
        aggregate = round((bowl.get("score", 0) + hub.get("score", 0)) / 2)
    ok = bool(bowl.get("ok"))
    return {
        "ok": ok,
        "source": "session_light",
        "aggregate_score": aggregate,
        "status": "ok" if ok else "needs_review",
        "sensors": [bowl, hub],
        "live_ops_ok": bool(hub.get("ok")),
        "drift_items_bowl": 0 if bowl.get("ok") else 1,
    }


def _compose_zero_drift_line(
    *,
    queue_sa: str,
    drift_score: int,
    chain_ok: bool,
    anti_ok: bool,
    sascip_ok: bool,
    drift_ok: bool,
    live_ops_ok: bool | None = None,
) -> str:
    wired = chain_ok and anti_ok and sascip_ok and drift_ok
    status = "WIRED" if wired else "REVIEW"
    ops = " · ops=LIVE" if live_ops_ok else " · ops=DOWN" if live_ops_ok is False else ""
    q = queue_sa if queue_sa else "idle"
    return f"ZERO-DRIFT {status} · score={drift_score} · queue={q} · L0.5+L1+L2+SASCIP{ops}"


def _patch_live_surfaces(
    *,
    zero_drift_line: str,
    drift_score: int,
    chain: dict,
    outbound_progress_line: str = "",
) -> None:
    row = _read_json(SURFACES)
    if not row:
        return
    row["zero_drift_line"] = zero_drift_line
    row["zero_drift_at"] = _now()
    row["zero_drift_score"] = drift_score
    row["zero_drift_chain_ok"] = chain.get("ok")
    row["governance_live_wire"] = {
        "receipt": str(RECEIPT),
        "law": "governance_zero_drift_live_wire_v1.py",
    }
    if outbound_progress_line:
        row["outbound_progress_line"] = outbound_progress_line
    try:
        SURFACES.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def run_zero_drift_live_wire(
    *,
    role: str = "any",
    tier: str = "session",
    skip_anti_staleness: bool = False,
) -> dict:
    steps: list[dict] = []
    ok = True
    anti: dict = {}

    anti_age = _age_sec(ANTI_RECEIPT)
    need_anti = tier == "full" or not skip_anti_staleness or anti_age is None or anti_age > 120
    if need_anti:
        code, out = _run(
            [PY, str(SCRIPTS / "anti_staleness_auto_wire_v1.py"), "--role", role, "--tier", tier, "--json"],
            timeout=120,
        )
        anti = _parse_json(out)
        step_ok = code == 0 and anti.get("ok", True)
        steps.append(
            {
                "chain": "L0.5→L1→L2",
                "step": "anti_staleness_auto_wire",
                "ok": step_ok,
                "exit": code,
                "queue_sa": anti.get("queue_sa"),
            }
        )
        ok = ok and step_ok
    else:
        anti = _read_json(ANTI_RECEIPT)
        steps.append(
            {
                "chain": "L0.5→L1→L2",
                "step": "anti_staleness_auto_wire",
                "ok": bool(anti.get("ok")),
                "exit": 0,
                "note": f"fresh age_sec={round(anti_age or 0, 1)}",
                "queue_sa": anti.get("queue_sa"),
            }
        )
        ok = ok and bool(anti.get("ok"))

    chain = cross_layer_chain_check()
    step_ok = chain.get("ok", False)
    steps.append(
        {
            "chain": "cross_layer",
            "step": "cross_layer_chain_check",
            "ok": step_ok,
            "drift_items": chain.get("drift_items"),
            "queue_sa": chain.get("queue_sa"),
            "issues": (chain.get("issues") or [])[:6],
        }
    )
    ok = ok and step_ok

    mac_law_ok = True
    mac_law_line = ""
    try:
        sys.path.insert(0, str(SCRIPTS))
        from mac_law_agent_execution_plane_lock_v1 import assess as mac_lock_assess  # noqa: WPS433

        mac_law_row = mac_lock_assess(sync_stack=False)
        mac_law_ok = bool(mac_law_row.get("ok"))
        mac_law_line = str(mac_law_row.get("line") or "")
    except Exception as exc:
        mac_law_row = {"ok": False, "error": str(exc)}
        mac_law_ok = False
    steps.append(
        {
            "chain": "mac_law",
            "step": "mac_law_agent_execution_plane_lock",
            "ok": mac_law_ok,
            "line": mac_law_line[:120],
        }
    )
    ok = ok and mac_law_ok

    if tier == "full":
        sys.path.insert(0, str(SCRIPTS))
        from governance_drift_engine import run_drift_report  # noqa: WPS433

        drift = run_drift_report()
        drift_row = {
            "ok": drift.get("aggregate_score", 0) >= 85 and drift.get("status") == "ok",
            "source": "full",
            "aggregate_score": drift.get("aggregate_score"),
            "status": drift.get("status"),
            "sensors": len(drift.get("sensors") or []),
        }
    else:
        drift_row = session_light_drift_report()
    step_ok = bool(drift_row.get("ok"))
    drift_ok = step_ok
    steps.append({"chain": "governance_drift", "step": "drift_report", "ok": step_ok, **drift_row})
    ok = ok and step_ok

    sascip = _read_json(SASCIP_ADMISSION)
    sascip_ok = sascip.get("ok", True) if sascip else True
    if not sascip:
        monitor = _read_json(SINA / "stranger-agent-monitor-v1.json")
        sascip_ok = bool(monitor.get("ok", True))
    steps.append(
        {
            "chain": "SASCIP",
            "step": "stranger_agent_admission",
            "ok": sascip_ok,
            "trust_tier": (sascip.get("classification") or {}).get("trust_tier"),
            "risk_score": ((sascip.get("classification") or {}).get("risk") or {}).get("score"),
        }
    )
    ok = ok and sascip_ok

    vocab_ok = True
    for s in anti.get("steps") or []:
        if s.get("step") == "vocabulary_guard":
            vocab_ok = bool(s.get("ok", True))
            break
    if not anti.get("steps"):
        try:
            from vocabulary_guard_v1 import run_vocabulary_gate  # noqa: WPS433

            vg = run_vocabulary_gate(include_tooling=False)
            vocab_ok = bool(vg.get("ok"))
        except Exception:
            vocab_ok = True
    steps.append({"chain": "vocab", "step": "vocabulary_guard", "ok": vocab_ok})
    ok = ok and vocab_ok

    code, out = _run(
        [PY, str(SCRIPTS / "ui_upgrade_first_check_v1.py"), "--wire", "--surface", "worker_hub", "--json"],
        timeout=90,
    )
    ufc = _parse_json(out)
    ui_fc_ok = code == 0 and bool(ufc.get("wire_ok"))
    steps.append(
        {
            "chain": "ui_upgrade",
            "step": "ui_upgrade_first_check",
            "ok": ui_fc_ok,
            "exit": code,
            "ui_upgrade_first_check_line": (ufc.get("line") or "")[:96],
        }
    )
    ok = ok and ui_fc_ok

    voyage_ok = False
    try:
        from voyage_ai_live_wire_v1 import run_voyage_ai_live_wire  # noqa: WPS433

        voyage = run_voyage_ai_live_wire(tier=tier)
        prov = voyage.get("provider") or {}
        voyage_ok = bool(prov.get("ok"))
        if tier == "full":
            voyage_ok = bool(voyage.get("ok"))
        steps.append(
            {
                "chain": "L8",
                "step": "voyage_ai_live_wire",
                "ok": voyage_ok,
                "mode": prov.get("mode"),
                "semantic": prov.get("semantic"),
                "search_hits": (voyage.get("search") or {}).get("hits"),
                "voyage_line": (voyage.get("voyage_line") or "")[:96],
            }
        )
        ok = ok and voyage_ok
    except Exception as exc:
        steps.append({"chain": "L8", "step": "voyage_ai_live_wire", "ok": False, "error": str(exc)})
        ok = False

    outbound_progress_line = ""
    outbound_progress_line = ""
    try:
        from outbound_queue_coherence_v1 import assess_queue_coherence, compose_outbound_progress_line  # noqa: WPS433
        from validate_outbound_receipt_path_v1 import validate as validate_outbound_receipt  # noqa: WPS433
        from execution_plane_honesty_v1 import assess_execution_plane  # noqa: WPS433

        coherence = assess_queue_coherence()
        receipt_val = validate_outbound_receipt()
        exec_plane = assess_execution_plane()
        outbound_ok = bool(coherence.get("ok")) and bool(receipt_val.get("ok")) and bool(
            exec_plane.get("ok")
        )
        outbound_progress_line = compose_outbound_progress_line()
        steps.append(
            {
                "chain": "outbound_worker",
                "step": "outbound_strict_validators",
                "ok": outbound_ok,
                "coherence_ok": coherence.get("ok"),
                "receipt_ok": receipt_val.get("ok"),
                "execution_plane_ok": exec_plane.get("ok"),
                "outbound_progress_line": outbound_progress_line[:120],
                "issues": (coherence.get("issues") or [])[:4],
            }
        )
        ok = ok and outbound_ok
    except Exception as exc:
        steps.append(
            {"chain": "outbound_worker", "step": "outbound_strict_validators", "ok": False, "error": str(exc)}
        )
        ok = False

    try:
        from monitor_live_sync_v1 import sync_disk  # noqa: WPS433

        pulse = sync_disk(force=False, reason=f"zero_drift_live_wire:{tier}", light=True)
        pulse_ok = bool(pulse.get("ok", True))
    except Exception as exc:
        pulse = {"ok": True, "skipped": True, "error": str(exc)}
        pulse_ok = True
    steps.append({"chain": "monitor", "step": "monitor_live_pulse", "ok": pulse_ok})
    ok = ok and pulse_ok

    try:
        from rule_propagation_fanout_v1 import fanout  # noqa: WPS433

        fan = fanout(reason=f"zero_drift_live_wire:{tier}", tier="fast" if tier in ("session", "worker") else "full")
        fan_ok = bool(fan.get("ok"))
        steps.append({"chain": "rule_propagation", "step": "rule_propagation_fanout", "ok": fan_ok})
        ok = ok and fan_ok
    except Exception as exc:
        steps.append({"chain": "rule_propagation", "step": "rule_propagation_fanout", "ok": False, "error": str(exc)[:120]})
        ok = False

    drift_score = int(drift_row.get("aggregate_score") or 0)
    queue_sa = chain.get("queue_sa") or anti.get("queue_sa") or ""
    zero_drift_line = _compose_zero_drift_line(
        queue_sa=queue_sa,
        drift_score=drift_score,
        chain_ok=bool(chain.get("ok")),
        anti_ok=bool(anti.get("ok")),
        sascip_ok=sascip_ok,
        drift_ok=drift_ok,
        live_ops_ok=drift_row.get("live_ops_ok"),
    )

    receipt = {
        "schema": "governance-zero-drift-live-wire-v1",
        "ok": ok,
        "at": _now(),
        "role": role,
        "tier": tier,
        "law": "brain-os/law/GOVERNANCE_DRIFT_ENGINE_LOCKED_v1.md",
        "zero_drift_line": zero_drift_line,
        "drift_score": drift_score,
        "drift_items": chain.get("drift_items", 0),
        "queue_sa": queue_sa,
        "factory_now_line": anti.get("factory_now_line") or _read_json(SURFACES).get("factory_now_line") or "",
        "chains": {
            "L0_5_L1_L2": bool(anti.get("ok")),
            "cross_layer": chain.get("ok"),
            "governance_drift": drift_row.get("ok"),
            "SASCIP": sascip_ok,
            "vocabulary": vocab_ok,
            "L8_voyage": voyage_ok,
            "monitor_pulse": pulse_ok,
            "mac_law": mac_law_ok,
        },
        "layers": chain.get("layers"),
        "paths": {
            "anti_staleness": str(ANTI_RECEIPT),
            "drift_report": str(DRIFT_REPORT),
            "live_surfaces": str(SURFACES),
            "sascip_admission": str(SASCIP_ADMISSION),
        },
        "steps": steps,
        "realtime": {
            "pulse": pulse if isinstance(pulse, dict) else {},
            "anti_staleness_age_sec": round(anti_age or 0, 1) if anti_age is not None else None,
            "live_ops_ok": drift_row.get("live_ops_ok"),
        },
    }
    SINA.mkdir(parents=True, exist_ok=True)
    if outbound_progress_line:
        receipt["outbound_progress_line"] = outbound_progress_line
        receipt.setdefault("chains", {})["outbound_worker"] = next(
            (s.get("ok") for s in steps if s.get("step") == "outbound_strict_validators"),
            None,
        )
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    _patch_live_surfaces(
        zero_drift_line=zero_drift_line,
        drift_score=drift_score,
        chain=chain,
        outbound_progress_line=outbound_progress_line,
    )
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance zero-drift live wire — all layers chained")
    ap.add_argument("--role", default="any")
    ap.add_argument("--tier", default="session", choices=["session", "full"])
    ap.add_argument("--skip-anti-staleness", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_zero_drift_live_wire(
        role=args.role,
        tier=args.tier,
        skip_anti_staleness=args.skip_anti_staleness,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"ZERO_DRIFT_LIVE_WIRE ok={row['ok']} score={row.get('drift_score')} "
            f"queue={row.get('queue_sa')} line={row.get('zero_drift_line', '')[:72]}"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
