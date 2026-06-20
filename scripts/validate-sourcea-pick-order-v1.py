#!/usr/bin/env python3
"""Validate sourcea pick order — phase-first drain; forbid tier-global cross-phase skip."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"

sys.path.insert(0, str(ROOT / "scripts"))
from sourcea_pick_lib import PHASE_ORDER, pick_backlog_plans  # noqa: E402


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def main() -> None:
    if not REG.is_file():
        _fail("REGISTRY.json missing")

    data = json.loads(REG.read_text(encoding="utf-8"))
    plans = data["plans"]

    backlog_count = sum(1 for pl in plans if pl.get("status") == "backlog")
    live = pick_backlog_plans(plans, tiers=["T0", "T1", "T2", "T3"], limit=1, order="phase-first")
    if not live:
        if backlog_count == 0:
            print("OK: live phase-first pick — backlog empty (registry all done)")
            head = None
        else:
            _fail("no phase-first pick from live REGISTRY")
    else:
        head = live[0]
        print(f"OK: live phase-first pick 1 = {head['id']} ({head.get('phase')} {head.get('tier')})")

    # Historical Brain bug: tier-global skipped s2 T1/T2/T3 while s3 T0 backlog existed.
    sim = deepcopy(plans)
    backlog_ids = {f"sa-{i:04d}" for i in range(213, 318)}  # 0213-0317 only
    for pl in sim:
        pl["status"] = "done"
    for pl in sim:
        if pl["id"] in backlog_ids:
            pl["status"] = "backlog"

    tier_global = pick_backlog_plans(
        sim, tiers=["T0", "T1", "T2", "T3"], limit=30, order="tier-global"
    )
    tg_ids = [p["id"] for p in tier_global]
    if "sa-0301" in tg_ids and "sa-0226" not in tg_ids:
        print("OK: regression fixture — tier-global skips sa-0226..0300 (documented bad order)")

    phase_first = pick_backlog_plans(
        sim, tiers=["T0", "T1", "T2", "T3"], limit=30, order="phase-first"
    )
    pf_ids = [p["id"] for p in phase_first]
    if "sa-0301" in pf_ids:
        idx_301 = pf_ids.index("sa-0301")
        if any(f"sa-{i:04d}" in pf_ids[:idx_301] for i in range(226, 301)):
            pass
        else:
            _fail("phase-first pick 30 still jumps to sa-0301 before s2 T1/T2/T3 band")
    if pf_ids[12] != "sa-0225":
        _fail(f"expected sa-0225 at #13 in phase-first sim, got {pf_ids[12] if len(pf_ids) > 12 else 'short'}")
    if pf_ids[13] != "sa-0226":
        _fail(f"expected sa-0226 at #14 in phase-first sim, got {pf_ids[13] if len(pf_ids) > 13 else 'short'}")
    print("OK: phase-first pick 30 simulation drains sa-0226 before sa-0301")

    up = pick_backlog_plans(plans, tiers=["T0", "T1", "T2", "T3"], limit=5, order="phase-first")
    if head is not None:
        earliest = None
        for ph in PHASE_ORDER:
            if any(p.get("phase") == ph and p.get("status") == "backlog" for p in plans):
                earliest = ph
                break
        if head.get("phase") != earliest:
            _fail(f"live head phase {head.get('phase')} != earliest backlog phase {earliest}")

    try:
        s6 = PHASE_ORDER.index("phase-s6-wtm-pre-llm")
        s5 = PHASE_ORDER.index("phase-s5-commercial-lanes")
    except ValueError as exc:
        _fail(f"PHASE_ORDER missing hierarchy phases: {exc}")
    if s5 <= s6:
        _fail("phase-s5-commercial-lanes must rank after phase-s6-wtm-pre-llm (GOAL_HIERARCHY)")

    if up:
        print(f"OK: up_next 5 phase-first = {', '.join(p['id'] for p in up)}")
    else:
        print("OK: up_next 5 phase-first — backlog empty")
    print("SOURCEA-PICK-ORDER VALID phase-first=ok")


if __name__ == "__main__":
    main()
