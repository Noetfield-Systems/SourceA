#!/usr/bin/env python3
"""Outbound factory upgrade plan pulse — maturity level + active wave progress.

Reads: data/outbound-factory-100-upgrade-plan-v1.json (schema v2)
Writes: ~/.sina/outbound-factory-upgrade-pulse-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
PLAN = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"
PULSE = SINA / "outbound-factory-upgrade-pulse-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _tier_counts(upgrades: list[dict]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for u in upgrades:
        tier = str(u.get("tier") or "unknown")
        status = str(u.get("status") or "planned")
        out.setdefault(tier, {"done": 0, "planned": 0, "total": 0})
        out[tier]["total"] += 1
        if status == "done":
            out[tier]["done"] += 1
        else:
            out[tier]["planned"] += 1
    return out


def _next_items(upgrades: list[dict], *, wave_id: str | None, limit: int = 8) -> list[dict]:
    waves = {w["id"]: w for w in (_read_json(PLAN).get("waves") or [])}
    wave = waves.get(wave_id or "") if wave_id else None
    ids = set(wave.get("upgrade_ids") or []) if wave else set()
    pending = [u for u in upgrades if u.get("status") != "done"]
    if ids:
        pending = [u for u in pending if u.get("id") in ids]
    pending.sort(key=lambda u: u.get("id", ""))
    return [
        {"id": u["id"], "tier": u.get("tier"), "title": u.get("title"), "lane": u.get("lane")}
        for u in pending[:limit]
    ]


def _level_gates() -> dict:
    """Level 3 readiness — align with commercial-command-pulse SSOT when present."""
    comm_pulse = _read_json(SINA / "commercial-command-pulse-v1.json")
    l3 = comm_pulse.get("l3_gates") or {}
    if l3:
        gates = {
            "w3_oqg": bool(l3.get("w3_oqg")),
            "w3_sina_read": bool(l3.get("w3_sina_read")),
            "w3_mail_from": bool(l3.get("w3_mail_from")),
            "w3_send_ready": bool(l3.get("w3_confirm_sent")),
        }
        ready_pct = int(comm_pulse.get("l3_ready_pct") or 0)
        ready = bool(comm_pulse.get("l3_ready"))
        return {
            "target_level": 3,
            "label": "Founder Send Loop",
            "gates": gates,
            "ready_pct": ready_pct,
            "ready": ready,
            "ssot": "commercial-command-pulse-v1.json",
        }
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from execution_plane_honesty_v1 import assess_commercial_readiness  # noqa: WPS433

        comm = assess_commercial_readiness()
        gates = dict(comm.get("gates") or {})
        ready_pct = int(comm.get("ready_pct") or 0)
        ready = bool(comm.get("ready"))
    except Exception:
        gates = {"w3_oqg": False, "w3_sina_read": False, "w3_mail_from": False, "w3_send_ready": False}
        ready_pct = 0
        ready = False
    return {
        "target_level": 3,
        "label": "Founder Send Loop",
        "gates": gates,
        "ready_pct": ready_pct,
        "ready": ready,
    }


def _fleet_telemetry() -> dict:
    """L4 rolling 7d OQG + template fingerprint from better-loop."""
    oqg = _read_json(SINA / "best-loop-oqg-receipt-v1.json")
    trust = oqg.get("trust_mode_7d") or oqg.get("rolling_7d") or {}
    fleet_pct = trust.get("pass_pct") or trust.get("output_clean_pct") or oqg.get("fleet_output_clean_pct")
    return {
        "target_level": 4,
        "label": "Fleet Hardening",
        "fleet_oqg_7d_pct": fleet_pct,
        "fleet_oqg_bar": 90,
        "fleet_ok": bool(fleet_pct and int(fleet_pct) >= 90),
        "template_fingerprint": oqg.get("template_fingerprint"),
        "regional_overlay": oqg.get("regional_overlay"),
        "ready": bool(fleet_pct and int(fleet_pct) >= 90),
    }


def _volume_gate() -> dict:
    """L5 volume gate — reply + deposit proof before bulk."""
    comm = _read_json(SINA / "commercial-command-pulse-v1.json")
    confirm = _read_json(SINA / "w3-confirm-sent-receipt-v1.json")
    events = confirm.get("events") or []
    has_reply_proof = len(events) >= 1
    l3 = int(comm.get("l3_ready_pct") or 0)
    deferred = not (has_reply_proof and l3 >= 100)
    return {
        "target_level": 5,
        "label": "Volume Ready",
        "status": "deferred" if deferred else "active",
        "witness_reply_proof": has_reply_proof,
        "confirm_sent_count": len(events),
        "portfolio_routing": "portfolio-300-locked/W3_FIRST_QUEUE.yaml",
        "deposit_target_cad": 2000,
        "gate": "minimum 1 confirm-sent before volume unlock",
        "ready": not deferred,
    }


def _epic_bridge(maturity_level: int) -> dict:
    """Cross-link outbound maturity to 1000-step Part 3 epics."""
    mapping = {
        2: {"epic": "E02", "label": "Session & Queue Truth", "proof": "execution_plane_honesty"},
        3: {"epic": "E09", "label": "Commerce GTM Hub P0", "proof": "commercial-command-pulse-v1.json"},
        4: {"epic": "E05+E11", "label": "Crawl Graph + Fleet", "proof": "fleet_telemetry"},
        5: {"epic": "E10", "label": "RunReceipt Union", "proof": "volume_gate"},
    }
    row = mapping.get(maturity_level) or mapping[2]
    reg = _read_json(ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json")
    return {
        **row,
        "parent_plan": "docs/SOURCEA_1000_STEP_MASTER_UPGRADE_PLAN15JUNE_LOCKED_v1.md",
        "outbound_plan": "data/outbound-factory-100-upgrade-plan-v1.json",
        "mono_pack_ref": reg.get("mono_pack_ref"),
        "c4_factory_feed": "outbound-factory-upgrade-pulse-v2",
    }


def _execution_honesty() -> dict:
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from execution_plane_honesty_v1 import assess_execution_plane  # noqa: WPS433

        return assess_execution_plane()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _verified_done_count(upgrades: list[dict]) -> int:
    """Count done rows with on-disk canonical receipt (v3 execution_proof law)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from outbound_receipt_path_v1 import receipt_exists  # noqa: WPS433

    n = 0
    for u in upgrades:
        if u.get("status") != "done":
            continue
        proof = u.get("execution_proof") or {}
        if proof.get("bulk_wiring") or u.get("bulk_wiring"):
            continue
        done_at = str(u.get("done_at") or "")
        if done_at.startswith("2026-06-18T21:40") or done_at.startswith("2026-06-18T21:42"):
            continue
        uid = str(u.get("id") or "")
        sa_id = str(proof.get("sa_id") or u.get("worker_sa_id") or "")
        if uid and sa_id and receipt_exists(upgrade_id=uid, sa_id=sa_id):
            n += 1
    return n


def _bulk_done_count(upgrades: list[dict]) -> int:
    """Structural bulk wiring rows — not Worker-proven (anti-theater F010)."""
    n = 0
    for u in upgrades:
        if u.get("status") != "done":
            continue
        proof = u.get("execution_proof") or {}
        if proof.get("bulk_wiring") or u.get("bulk_wiring"):
            n += 1
            continue
        done_at = str(u.get("done_at") or "")
        if done_at.startswith("2026-06-18T21:40") or done_at.startswith("2026-06-18T21:42"):
            n += 1
    return n


def run_pulse(*, write: bool = True) -> dict:
    plan = _read_json(PLAN)
    upgrades = plan.get("upgrades") or []
    maturity = plan.get("maturity") or {}
    current = int(maturity.get("current_level") or 1)
    active_wave = str(plan.get("active_wave") or "W1")
    tiers = _tier_counts(upgrades)
    done_total = sum(1 for u in upgrades if u.get("status") == "done")
    verified_done = _verified_done_count(upgrades)
    bulk_done = _bulk_done_count(upgrades)
    exec_honesty = _execution_honesty()
    level_gates = _level_gates()
    fleet = _fleet_telemetry()
    volume = _volume_gate()
    epic = _epic_bridge(current)
    row = {
        "schema": "outbound-factory-upgrade-pulse-v2",
        "at": _now(),
        "plan_schema": plan.get("schema"),
        "plan_version": plan.get("version"),
        "maturity_level": current,
        "maturity_label": next(
            (l.get("label") for l in (maturity.get("levels") or []) if l.get("level") == current),
            "Salvage Lint",
        ),
        "level_gates": level_gates,
        "fleet_telemetry": fleet,
        "volume_gate": volume,
        "epic_bridge": epic,
        "execution_honesty": exec_honesty,
        "execution_honesty_line": exec_honesty.get("execution_honesty_line"),
        "governance_cart": str(SINA / "governance-gate-cart-v1.json"),
        "active_wave": active_wave,
        "progress": {
            "done_total": done_total,
            "verified_done": verified_done,
            "bulk_done": bulk_done,
            "worker_proven": verified_done,
            "done_without_receipt": max(0, done_total - verified_done),
            "total": len(upgrades),
            "pct": round(100 * done_total / len(upgrades)) if upgrades else 0,
            "verified_pct": round(100 * verified_done / len(upgrades)) if upgrades else 0,
            "by_tier": tiers,
        },
        "next_wave_items": _next_items(upgrades, wave_id=active_wave),
        "pulse_line": (
            f"upgrade-plan · L{current} · wave={active_wave} · "
            f"worker={verified_done} bulk={bulk_done}/{len(upgrades)} · "
            f"P0 {tiers.get('P0', {}).get('done', 0)}/{tiers.get('P0', {}).get('total', 0)} · "
            f"L3ready={level_gates['ready_pct']}% · "
            f"exec={'OK' if exec_honesty.get('ok') else 'RED'}"
        ),
        "commands": {
            "fleet_compile": "python3 scripts/icp_output_compiler_v1.py --fleet --json",
            "founder_show": "python3 scripts/w3_founder_review_v1.py --show",
            "translation_lint": "python3 scripts/validate_email_translation_v1.py",
            "research_checklist": "python3 scripts/outbound_research_checklist_v1.py --account <id> --json",
            "forbidden_sources": "bash scripts/validate-outbound-forbidden-sources-v1.sh",
        },
    }
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from anti_theater_validator_loop_v1 import run_loop as _anti_theater_run  # noqa: WPS433

        at = _anti_theater_run(write=True)
        row["anti_theater_loop"] = {
            "ok": at.get("ok"),
            "passed": at.get("passed"),
            "total": at.get("total"),
            "sina_pending": at.get("sina_pending"),
        }
        row["anti_theater_line"] = at.get("anti_theater_line")
        row["salvage_line"] = at.get("anti_theater_line")
    except Exception as exc:
        row["anti_theater_loop"] = {"ok": False, "error": str(exc)}
        row["anti_theater_line"] = "Anti-theater · ERROR"
        row["salvage_line"] = row["anti_theater_line"]
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        PULSE.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice(*, refresh: bool = False) -> dict:
    receipt = _read_json(PULSE)
    if refresh or not receipt or receipt.get("schema") != "outbound-factory-upgrade-pulse-v2":
        receipt = run_pulse(write=True)
    progress = receipt.get("progress") or {}
    level_gates = receipt.get("level_gates") or {}
    return {
        "schema": "worker-hub-outbound-factory-upgrade-v1",
        "ok": True,
        "at": receipt.get("at"),
        "pulse_line": receipt.get("pulse_line"),
        "maturity_level": receipt.get("maturity_level"),
        "maturity_label": receipt.get("maturity_label"),
        "active_wave": receipt.get("active_wave"),
        "done_total": progress.get("done_total"),
        "verified_done": progress.get("verified_done"),
        "bulk_done": progress.get("bulk_done"),
        "worker_proven": progress.get("worker_proven"),
        "total": progress.get("total"),
        "pct": progress.get("pct"),
        "by_tier": progress.get("by_tier"),
        "level_gates": level_gates,
        "ready_pct": level_gates.get("ready_pct"),
        "next_wave_items": receipt.get("next_wave_items") or [],
        "law": "data/outbound-factory-100-upgrade-plan-v1.json",
        "pulse_command": "python3 scripts/outbound_factory_upgrade_pulse_v1.py --json",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Outbound factory upgrade pulse")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = run_pulse(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("pulse_line"))
        for item in row.get("next_wave_items") or []:
            print(f"  next · {item.get('id')} · {item.get('title')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
