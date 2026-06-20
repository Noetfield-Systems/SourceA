#!/usr/bin/env python3
"""Investigator Circle — always track loop health · route to specialists.

Law: docs/SOURCEA_INVESTIGATOR_JUDGE_LOOP_ROOM_LOCKED_v1.md
Receipt: ~/.sina/loop-health-investigation-receipt-v1.json
execution_authority: false
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "loop-health-investigation-receipt-v1.json"
ROUTING = ROOT / "data" / "investigator-specialist-routing-v1.json"
HEAL_CATALOG = ROOT / "data" / "investigator-self-heal-catalog-v1.json"
VERDICTS = frozenset({"GREEN", "YELLOW", "RED"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_routing() -> dict:
    row = _read_json(ROUTING)
    return row if row.get("schema") == "investigator-specialist-routing-v1" else {}


def _load_heal_catalog() -> dict:
    row = _read_json(HEAL_CATALOG)
    return row if row.get("schema") == "investigator-self-heal-catalog-v1" else {}


def _deterministic_hash(*, obs: dict, verdict: str, routes: list[dict]) -> str:
    payload = {
        "obs_at": obs.get("at"),
        "verdict": verdict,
        "route_ids": [r.get("id") for r in routes[:5]],
        "queue_sa": (obs.get("product") or {}).get("queue_sa"),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _match_routes(*, obs: dict) -> list[dict]:
    routing = _load_routing()
    labels = routing.get("specialist_labels") or {}
    matched: list[dict] = []
    comm = obs.get("commercial") or {}
    product = obs.get("product") or {}
    system = obs.get("system") or {}
    freeze = obs.get("freeze") or {}
    dual = product.get("dual_pick") or {}
    bugs = system.get("critical_bugs") or {}
    gates = (comm.get("level_gates") or {}).get("gates") or {}

    checks: list[tuple[str, bool]] = [
        ("commercial_reds", int(comm.get("commercial_red_count") or 0) > 0),
        ("w3_sina_read_fail", gates.get("w3_sina_read") is False),
        ("system_reds", int(comm.get("system_red_count") or 0) > 0),
        ("dual_pick_fail", not dual.get("ok")),
        ("critical_bugs", int(bugs.get("critical_count") or 0) > 0),
        ("drift_low", int(system.get("drift_score") or 100) < 85),
        ("freeze_block", bool(freeze.get("prompt_blocked_by_freeze"))),
    ]
    by_id = {r["id"]: r for r in (routing.get("routes") or []) if r.get("id")}
    for rid, fired in checks:
        if not fired:
            continue
        spec = by_id.get(rid)
        if not spec:
            continue
        matched.append(
            {
                **spec,
                "primary_label": labels.get(spec.get("primary"), spec.get("primary")),
                "secondary_label": labels.get(spec.get("secondary"), spec.get("secondary")),
            }
        )
    return matched


def _verdict(*, obs: dict, routes: list[dict]) -> str:
    system = obs.get("system") or {}
    product = obs.get("product") or {}
    bugs = system.get("critical_bugs") or {}
    dual = product.get("dual_pick") or {}
    if int(bugs.get("critical_count") or 0) > 0:
        return "RED"
    if not dual.get("ok"):
        return "RED"
    if int(system.get("drift_score") or 100) < 85:
        return "RED"
    if int((obs.get("commercial") or {}).get("system_red_count") or 0) > 0 and not obs.get("ok"):
        return "RED"
    if routes:
        return "YELLOW"
    return "GREEN"


def _suggested_heals(*, route_ids: list[str]) -> list[dict]:
    catalog = _load_heal_catalog()
    out: list[dict] = []
    for act in catalog.get("acts") or []:
        when = set(act.get("when") or [])
        if when.intersection(route_ids):
            out.append(
                {
                    "id": act.get("id"),
                    "label": act.get("label"),
                    "risk": act.get("risk"),
                    "founder_action": act.get("founder_action"),
                    "cmd": act.get("cmd"),
                }
            )
    return out


def _investigation_line(*, verdict: str, routes: list[dict], obs: dict) -> str:
    primary = routes[0].get("primary_label") if routes else "none"
    obs_bit = str(obs.get("founder_one_line") or "")[:72]
    return f"investigator · {verdict} · routes={len(routes)} · →{primary} · {obs_bit}"


def _run_heal(act_id: str) -> dict:
    catalog = _load_heal_catalog()
    for act in catalog.get("acts") or []:
        if act.get("id") != act_id:
            continue
        cmd = act.get("cmd")
        if not cmd:
            return {"ok": True, "skipped": True, "reason": "founder_gate", "id": act_id}
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {"ok": proc.returncode == 0, "id": act_id, "exit": proc.returncode}
        except Exception as exc:
            return {"ok": False, "id": act_id, "error": str(exc)}
    return {"ok": False, "error": "unknown_act", "id": act_id}


def run_investigation(*, write: bool = True, apply_heal: str | None = None) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    try:
        from loop_observatory_report_v1 import run_report  # noqa: WPS433

        obs = run_report(write=True)
    except Exception as exc:
        obs = _read_json(SINA / "loop-observatory-report-v1.json")
        obs.setdefault("ok", False)
        obs["error"] = str(exc)

    routes = _match_routes(obs=obs)
    verdict = _verdict(obs=obs, routes=routes)
    route_ids = [str(r.get("id")) for r in routes]
    heals = _suggested_heals(route_ids=route_ids)
    heal_results: list[dict] = []
    if apply_heal:
        heal_results.append(_run_heal(apply_heal))

    insights: list[str] = []
    if verdict == "GREEN":
        insights.append("Loop signals aligned — advisory + specialist may tick observe-only")
    for r in routes:
        insights.append(f"{r.get('id')}: {r.get('action')} → {r.get('primary_label')}")
    comm = obs.get("commercial") or {}
    if comm.get("founder_action"):
        insights.append(f"next: {comm.get('founder_action')}")

    row = {
        "schema": "loop-health-investigation-receipt-v1",
        "ok": verdict != "RED" or bool(routes),
        "at": _now(),
        "execution_authority": False,
        "investigation_verdict": verdict,
        "deterministic_hash": _deterministic_hash(obs=obs, verdict=verdict, routes=routes),
        "observatory_at": obs.get("at"),
        "observatory_ok": obs.get("ok"),
        "specialist_routes": routes,
        "insights": insights[:8],
        "suggested_heals": heals,
        "heal_results": heal_results,
        "commercial_founder_action": comm.get("founder_action"),
        "investigator_line": "",
        "command": "python3 scripts/investigator_circle_run_v1.py --json",
        "hub_api": "POST /api/investigator-circle/tick/v1",
    }
    row["investigator_line"] = _investigation_line(verdict=verdict, routes=routes, obs=obs)
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "loop-health-investigation-receipt-v1":
        row = run_investigation(write=True)
    return {
        "schema": "worker-hub-investigator-room-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "investigation_verdict": row.get("investigation_verdict"),
        "investigator_line": row.get("investigator_line"),
        "specialist_routes": row.get("specialist_routes") or [],
        "insights": row.get("insights") or [],
        "suggested_heals": row.get("suggested_heals") or [],
        "hub_api": "POST /api/investigator-circle/tick/v1",
    }


def handle_hub_post(body: dict | None = None) -> dict:
    body = body or {}
    apply_heal = str(body.get("apply_heal") or "").strip() or None
    return run_investigation(write=True, apply_heal=apply_heal)


def main() -> int:
    ap = argparse.ArgumentParser(description="Investigator Circle run")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--apply-heal", metavar="ACT_ID", help="Bounded heal from catalog")
    args = ap.parse_args()
    if args.hub_slice:
        row = hub_slice()
    else:
        row = run_investigation(
            write=not args.no_write,
            apply_heal=args.apply_heal,
        )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("investigator_line") or row.get("investigation_verdict"))
    return 0 if row.get("investigation_verdict") in VERDICTS else 1


if __name__ == "__main__":
    raise SystemExit(main())
