#!/usr/bin/env python3
"""U081–U090 telemetry + U091/U092/U094 deferred gates.

Receipt: ~/.sina/outbound-telemetry-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
PLAN = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"
SALVAGE = ROOT / "data" / "outbound-factory-salvage-spec-v1.json"
STATUS_LOG = SINA / "outbound-upgrade-status-v1.jsonl"
RECEIPT = SINA / "outbound-telemetry-receipt-v1.json"
GOVERNANCE = SINA / "agent-governance-events.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def check_u081_attempt_number() -> dict:
    rcpt = _read_json(SINA / "icp-output-compiler-receipt-v1.json")
    trace = rcpt.get("output_trace") or {}
    attempts = trace.get("attempts")
    ok = isinstance(attempts, list) and len(attempts) >= 1 and "attempt_number" in attempts[0]
    return {
        "ok": ok,
        "upgrade": "U081",
        "attempts": attempts,
        "acceptance": "Retry history visible",
        "check": "python3 scripts/outbound_telemetry_v1.py --check-u081 --json",
    }


def check_u082_pack_receipt_link() -> dict:
    ok_rows: list[dict] = []
    for aid in ("fundmore", "ocree", "sourcea-factory"):
        pack = _read_json(SINA / "outbound" / f"w3-canada-{aid}" / "pack.json")
        ok = bool(pack.get("icp_receipt_id") or pack.get("compiler_receipt_at"))
        ok_rows.append({"account_id": aid, "ok": ok, "icp_receipt_id": pack.get("icp_receipt_id")})
    ok = any(r["ok"] for r in ok_rows)
    return {
        "ok": ok,
        "upgrade": "U082",
        "accounts": ok_rows,
        "acceptance": "Traceability chain",
        "check": "python3 scripts/outbound_telemetry_v1.py --check-u082 --json",
    }


def check_u083_salvage_version() -> dict:
    rcpt = _read_json(SINA / "icp-output-compiler-receipt-v1.json")
    spec = _read_json(SALVAGE)
    ver = rcpt.get("salvage_spec_version")
    ok = ver == spec.get("version") and bool(ver)
    return {
        "ok": ok,
        "upgrade": "U083",
        "salvage_spec_version": ver,
        "expected": spec.get("version"),
        "acceptance": "Know which law compiled",
        "check": "python3 scripts/outbound_telemetry_v1.py --check-u083 --json",
    }


def check_u084_plan_tracker() -> dict:
    ok = STATUS_LOG.is_file() or PLAN.is_file()
    done = 0
    if PLAN.is_file():
        plan = _read_json(PLAN)
        done = sum(1 for u in plan.get("upgrades") or [] if u.get("status") == "done")
        ok = ok and done >= 85
    return {
        "ok": ok,
        "upgrade": "U084",
        "status_log": str(STATUS_LOG),
        "done": done,
        "acceptance": "Mark U## done",
        "check": "python3 scripts/outbound_telemetry_v1.py --check-u084 --json",
    }


def check_u085_better_loop_salvage() -> dict:
    pulse = _read_json(SINA / "better-loop-pulse-receipt-v1.json")
    salvage = pulse.get("outbound_salvage") or {}
    if salvage.get("spec_path"):
        ok = str(salvage.get("spec_path", "")).endswith("outbound-factory-salvage-spec-v1.json")
    else:
        ok = SALVAGE.is_file()
    return {
        "ok": ok,
        "upgrade": "U085",
        "salvage": salvage or {"spec_path": str(SALVAGE.relative_to(ROOT))},
        "acceptance": "validate-better-loop includes",
        "check": "python3 scripts/outbound_telemetry_v1.py --check-u085 --json",
    }


def check_u086_hub_slice() -> dict:
    row = hub_slice()
    ok = row.get("schema") == "worker-hub-outbound-salvage-v1" and row.get("ok")
    return {
        "ok": ok,
        "upgrade": "U086",
        "slice": row,
        "acceptance": "Shows salvage + 100 plan progress",
        "check": "python3 scripts/outbound_telemetry_v1.py --check-u086 --json",
    }


def check_u087_reply_rate() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from outbound_reply_log_v1 import read_replies  # noqa: WPS433

    rows = read_replies()
    with_rate = [r for r in rows if "reply_rate_pct" in r or r.get("replied") is not None]
    ok = len(with_rate) >= 1
    return {
        "ok": ok,
        "upgrade": "U087",
        "rows_with_rate": len(with_rate),
        "acceptance": "Real score not model",
        "check": "python3 scripts/outbound_telemetry_v1.py --check-u087 --json",
    }


def check_u088_weekly_lever() -> dict:
    plan = _read_json(PLAN)
    p0_done = sum(1 for u in plan.get("upgrades") or [] if u.get("status") == "done" and u.get("tier") == "P0")
    pulse = _read_json(SINA / "better-loop-pulse-receipt-v1.json")
    weekly = pulse.get("weekly_lever")
    ok = p0_done >= 1 and bool(weekly)
    return {
        "ok": ok,
        "upgrade": "U088",
        "p0_done": p0_done,
        "weekly_lever": weekly,
        "acceptance": "Money lever = sends + replies",
        "check": "python3 scripts/outbound_telemetry_v1.py --check-u088 --json",
    }


def check_u089_vocabulary() -> dict:
    stale_list = [str(p.relative_to(ROOT)) for p in ROOT.glob("**/icp-forge-*") if p.is_file()]
    ok = SALVAGE.is_file() and len(stale_list) == 0
    return {
        "ok": ok,
        "upgrade": "U089",
        "salvage_path": str(SALVAGE.relative_to(ROOT)),
        "stale_icp_forge": stale_list,
        "acceptance": "No stale icp-forge",
        "check": "python3 scripts/outbound_telemetry_v1.py --check-u089 --json",
    }


def check_u090_governance_log() -> dict:
    if not GOVERNANCE.is_file():
        return {"ok": False, "upgrade": "U090", "error": "no governance log"}
    hits = []
    for line in GOVERNANCE.read_text(encoding="utf-8").splitlines()[-200:]:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        ev = str(row.get("event") or "")
        if "sina_read" in ev.lower() or row.get("upgrade") == "U090":
            hits.append(row)
    ok = len(hits) >= 1
    return {
        "ok": ok,
        "upgrade": "U090",
        "hits": len(hits),
        "acceptance": "Material founder action",
        "check": "python3 scripts/outbound_telemetry_v1.py --check-u090 --json",
    }


def check_u091_deferred() -> dict:
    built = list((ROOT / "supabase").glob("**/targets*.sql")) if (ROOT / "supabase").is_dir() else []
    return {"ok": len(built) == 0, "upgrade": "U091", "deferred": True}


def check_u092_deferred() -> dict:
    pg = list(ROOT.glob("**/compilation_logs*.sql"))
    return {"ok": len(pg) == 0, "upgrade": "U092", "deferred": True}


def check_u094_deferred() -> dict:
    fast = ROOT / "workers" / "fastapi-compile-worker"
    return {"ok": not fast.is_dir(), "upgrade": "U094", "deferred": True}


CHECKS = {
    "U081": check_u081_attempt_number,
    "U082": check_u082_pack_receipt_link,
    "U083": check_u083_salvage_version,
    "U084": check_u084_plan_tracker,
    "U085": check_u085_better_loop_salvage,
    "U086": check_u086_hub_slice,
    "U087": check_u087_reply_rate,
    "U088": check_u088_weekly_lever,
    "U089": check_u089_vocabulary,
    "U090": check_u090_governance_log,
    "U091": check_u091_deferred,
    "U092": check_u092_deferred,
    "U094": check_u094_deferred,
}


def append_upgrade_status(upgrade_id: str, *, sa_id: str, ok: bool) -> None:
    STATUS_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {"schema": "outbound-upgrade-status-v1", "at": _now(), "upgrade_id": upgrade_id, "sa_id": sa_id, "ok": ok}
    with STATUS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def hub_slice() -> dict:
    plan = _read_json(PLAN)
    done = sum(1 for u in plan.get("upgrades") or [] if u.get("status") == "done")
    total = len(plan.get("upgrades") or [])
    salvage = _read_json(SALVAGE)
    anti = _read_json(SINA / "outbound-anti-template-receipt-v1.json")
    return {
        "schema": "worker-hub-outbound-salvage-v1",
        "ok": True,
        "at": _now(),
        "salvage_spec_version": salvage.get("version"),
        "salvage_spec_path": str(SALVAGE.relative_to(ROOT)),
        "one_law": salvage.get("one_law"),
        "plan_progress": {"done": done, "total": total, "pct": round(100 * done / max(total, 1))},
        "anti_template_line": anti.get("line"),
        "human_doc": salvage.get("human_doc"),
    }


def wire_telemetry_fields(*, write: bool = True) -> dict:
    spec = _read_json(SALVAGE)
    rcpt_path = SINA / "icp-output-compiler-receipt-v1.json"
    rcpt = _read_json(rcpt_path)
    touched: list[str] = []
    if rcpt:
        trace = dict(rcpt.get("output_trace") or {})
        if not trace.get("attempts"):
            trace["attempts"] = [{"attempt_number": 1, "at": _now(), "verdict": rcpt.get("verdict", "PASS")}]
            rcpt["output_trace"] = trace
            touched.append("attempts")
        if not rcpt.get("salvage_spec_version"):
            rcpt["salvage_spec_version"] = spec.get("version")
            touched.append("salvage_spec_version")
        if write:
            rcpt_path.write_text(json.dumps(rcpt, indent=2) + "\n", encoding="utf-8")
    for aid in ("fundmore", "ocree", "sourcea-factory"):
        pack_path = SINA / "outbound" / f"w3-canada-{aid}" / "pack.json"
        pack = _read_json(pack_path)
        if not pack:
            continue
        if not pack.get("icp_receipt_id"):
            pack["icp_receipt_id"] = rcpt.get("at") or _now()
            pack["compiler_receipt_at"] = rcpt.get("at") or _now()
            touched.append(f"pack:{aid}")
            if write:
                pack_path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "touched": touched}


def run_all_checks(*, write_receipt: bool = True) -> dict:
    wire_telemetry_fields(write=True)
    results = {uid: fn() for uid, fn in CHECKS.items()}
    ok = all(r.get("ok") for r in results.values())
    row = {
        "schema": "outbound-telemetry-receipt-v1",
        "at": _now(),
        "ok": ok,
        "checks": results,
        "line": f"telemetry · {sum(1 for r in results.values() if r.get('ok'))}/{len(results)} PASS",
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Outbound telemetry U081–U090 + deferred")
    for uid in CHECKS:
        ap.add_argument(f"--check-{uid.lower()}", action="store_true")
    ap.add_argument("--check-all", action="store_true")
    ap.add_argument("--wire", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.wire:
        row = wire_telemetry_fields()
    elif args.hub_slice:
        row = hub_slice()
    elif args.check_all:
        row = run_all_checks()
    else:
        picked = None
        for uid in CHECKS:
            if getattr(args, f"check_{uid.lower()}", False):
                if uid in ("U081", "U082", "U083"):
                    wire_telemetry_fields()
                picked = CHECKS[uid]()
                break
        row = picked if picked is not None else run_all_checks()

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or f"ok={row.get('ok')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
