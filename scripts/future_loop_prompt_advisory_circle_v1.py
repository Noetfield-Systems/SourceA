#!/usr/bin/env python3
"""Future Loop Prompt Advisory Circle — deterministic next-prompt reasoning (no execution).

Law: docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md §2 commercial compile
Receipt: ~/.sina/future-loop-prompt-advisory-v1.json
execution_authority: false — advise only; Brain routes · Prompt Composer composes
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
PLAN = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"
RECEIPT = SINA / "future-loop-prompt-advisory-v1.json"
RULES_VERSION = "cl10-v2"
COMPILE_SEQUENCE = "SourceA Sina read → Noetfield compile → TrustField send"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _tier_score(tier: str) -> int:
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return order.get(str(tier or "P1").upper(), 9)


def _commercial_blockers(obs: dict, pulse: dict) -> list[str]:
    blockers: list[str] = []
    comm = obs.get("commercial") or {}
    if int(comm.get("commercial_red_count") or 0) > 0:
        for c in comm.get("reds") or []:
            if not c.get("ok"):
                blockers.append(str(c.get("id") or "?"))
    gates = (pulse.get("level_gates") or {}).get("gates") or {}
    if not gates.get("w3_sina_read"):
        blockers.append("w3_sina_read")
    if not gates.get("w3_send_ready"):
        blockers.append("w3_send_ready")
    return sorted(set(blockers))


def _is_outbound_drain(hq: dict) -> bool:
    return (
        str(hq.get("thread") or "") in ("OUTBOUND-FACTORY", "UNIFIED-PLANS")
        or str(hq.get("product") or "").startswith(("Outbound Factory", "Unified plans"))
        or bool(hq.get("plans_unified"))
        or bool(hq.get("upgrade_plan_schema"))
    )


def _queue_head_upgrade(*, plan: dict, hq: dict) -> dict | None:
    queue = hq.get("queue") or []
    if not queue:
        return None
    head = queue[0]
    uid = str(head.get("upgrade_id") or "")
    if not uid:
        return None
    sys.path.insert(0, str(SCRIPTS))
    from outbound_queue_coherence_v1 import _plan_row  # noqa: WPS433

    u = _plan_row(uid)
    if not u:
        u = {str(x.get("id") or ""): x for x in (plan.get("upgrades") or [])}.get(uid) or {}
    if not u or u.get("status") == "done":
        return None
    tier = str(u.get("tier") or head.get("sa_tier") or "P1")
    wave = str(u.get("wave") or hq.get("active_wave") or head.get("phase") or "")
    blockers: list[str] = []
    return {
        "upgrade_id": uid,
        "sa_id": str(head.get("sa_id") or u.get("worker_sa_id") or ""),
        "lane": str(u.get("lane_label") or u.get("lane") or ""),
        "tier": tier,
        "title": (u.get("title") or "")[:80],
        "rationale": f"{uid} · {tier} · queue_head · wave={wave} · {u.get('title', '')[:48]}",
        "confidence": 100,
        "blockers": blockers,
        "queue_head_pin": True,
        "wave": wave,
    }


def _rank_prompts(*, plan: dict, obs: dict, pulse: dict, hq: dict, limit: int = 5) -> list[dict]:
    upgrades = [u for u in (plan.get("upgrades") or []) if u.get("status") != "done"]
    outbound_drain = _is_outbound_drain(hq)
    head_pick = _queue_head_upgrade(plan=plan, hq=hq)
    # Drain queue SSOT wins over strategic active_wave (W3) while outbound thread active
    if outbound_drain and head_pick:
        active_wave = str(head_pick.get("wave") or "")
    else:
        active_wave = str(plan.get("active_wave") or pulse.get("active_wave") or "")
    waves = {w["id"]: w for w in (plan.get("waves") or []) if w.get("id")}
    wave_ids = set(waves.get(active_wave, {}).get("upgrade_ids") or []) if active_wave else set()
    blockers = _commercial_blockers(obs, pulse)
    by_sa: dict[str, dict] = {}
    for item in hq.get("queue") or []:
        uid = str(item.get("upgrade_id") or "")
        if uid:
            by_sa[uid] = item

    ranked: list[dict] = []
    for u in upgrades:
        uid = str(u.get("id") or "")
        if head_pick and uid == head_pick.get("upgrade_id"):
            continue
        in_wave = (not wave_ids) or (uid in wave_ids)
        if not in_wave and outbound_drain:
            continue
        if not in_wave:
            continue
        tier = str(u.get("tier") or "P1")
        sa_id = str(u.get("worker_sa_id") or (by_sa.get(uid) or {}).get("sa_id") or "")
        lane = str(u.get("lane_label") or u.get("lane") or "")
        confidence = 100 - _tier_score(tier) * 15
        if blockers:
            confidence -= min(40, 10 * len(blockers))
        confidence = max(5, min(100, confidence))
        rationale = f"{uid} · {tier} · wave={active_wave or '?'} · {u.get('title', '')[:48]}"
        ranked.append(
            {
                "upgrade_id": uid,
                "sa_id": sa_id,
                "lane": lane,
                "tier": tier,
                "title": (u.get("title") or "")[:80],
                "rationale": rationale,
                "confidence": confidence,
                "blockers": blockers[:4],
                "queue_head_pin": False,
            }
        )
    ranked.sort(key=lambda r: (-r["confidence"], _tier_score(r.get("tier", "P1")), r.get("upgrade_id", "")))
    if head_pick:
        head_pick["blockers"] = blockers[:4]
        if blockers:
            head_pick["confidence"] = max(60, 100 - min(30, 8 * len(blockers)))
        ranked = [head_pick] + ranked
    return ranked[:limit]


def _deterministic_hash(*, obs: dict, pulse: dict, ranked: list[dict]) -> str:
    payload = {
        "rules_version": RULES_VERSION,
        "obs_at": obs.get("at"),
        "pulse_at": pulse.get("at"),
        "active_wave": pulse.get("active_wave"),
        "drain_wave": (ranked[0] if ranked else {}).get("wave"),
        "queue_head_pin": bool((ranked[0] if ranked else {}).get("queue_head_pin")),
        "top_ids": [r.get("upgrade_id") for r in ranked[:3]],
        "compile_sequence": COMPILE_SEQUENCE,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def run_advisory(*, write: bool = True) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    obs = _read_json(SINA / "loop-observatory-report-v1.json")
    if not obs or obs.get("schema") != "loop-observatory-report-v1":
        try:
            from loop_observatory_report_v1 import run_report  # noqa: WPS433

            obs = run_report(write=True)
        except Exception:
            obs = obs or {}
    pulse = _read_json(SINA / "outbound-factory-upgrade-pulse-v1.json")
    plan = _read_json(PLAN)
    hq = _read_json(SINA / "healthy-queue-30-active.json")
    icp = _read_json(ROOT / "data" / "icp-output-compiler-v1.json")
    ranked = _rank_prompts(plan=plan, obs=obs, pulse=pulse, hq=hq)
    dhash = _deterministic_hash(obs=obs, pulse=pulse, ranked=ranked)
    top = ranked[0] if ranked else {}
    blockers = _commercial_blockers(obs, pulse)
    if not ranked:
        try:
            from execution_path_vocabulary_v1 import (  # noqa: WPS433
                commercial_smart_loop_line,
                post_outbound_smart_loop_active,
            )

            if post_outbound_smart_loop_active():
                line = f"advisory · outbound complete · {commercial_smart_loop_line()}"
            else:
                line = f"advisory · idle · {COMPILE_SEQUENCE}"
        except Exception:
            line = f"advisory · idle · {COMPILE_SEQUENCE}"
    elif blockers:
        line = f"advisory · top={top.get('upgrade_id', '?')} · blockers={','.join(blockers[:3])} · compile: {COMPILE_SEQUENCE}"
    else:
        line = f"advisory · next={top.get('upgrade_id', 'idle')} · conf={top.get('confidence', '?')} · {COMPILE_SEQUENCE}"
    row = {
        "schema": "future-loop-prompt-advisory-v1",
        "ok": True,
        "at": _now(),
        "execution_authority": False,
        "rules_version": RULES_VERSION,
        "deterministic_hash": dhash,
        "compile_sequence": COMPILE_SEQUENCE,
        "advisory_line": line,
        "ranked_prompts": ranked,
        "icp_compiler": {
            "present": bool(icp),
            "fleet_compile_pct": icp.get("fleet_compile_pct"),
        },
        "commercial_blockers": blockers,
        "queue_head_pin": bool((top or {}).get("queue_head_pin")),
        "drain_active": _is_outbound_drain(hq),
        "command": "python3 scripts/future_loop_prompt_advisory_circle_v1.py --json",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "future-loop-prompt-advisory-v1":
        row = run_advisory(write=True)
    top = (row.get("ranked_prompts") or [{}])[0]
    return {
        "schema": "worker-hub-future-prompt-advisory-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "advisory_line": row.get("advisory_line"),
        "deterministic_hash": row.get("deterministic_hash"),
        "top_pick": top,
        "ranked_prompts": row.get("ranked_prompts") or [],
        "compile_sequence": row.get("compile_sequence"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Future loop prompt advisory circle")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    args = ap.parse_args()
    if args.hub_slice:
        row = hub_slice()
    else:
        row = run_advisory(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("advisory_line") or "advisory ok")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
