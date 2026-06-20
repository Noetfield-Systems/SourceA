#!/usr/bin/env python3
"""Advance phase-strict pack when current force_list is fully done in REGISTRY.

Law: SOURCEA_PHASE_STRICT_RUN_INBOX_LOCKED_v1.md · NEXT_FACTORY_CYCLE_ORGANIZED
Config: ~/.sina/phase-strict-drain-v1.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
CONFIG = SINA / "phase-strict-drain-v1.json"
STATE = SINA / "healthy-queue-state-v1.json"
REGISTRY = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"

# Cycle 3 Hub 2 machine packs (phase-s8 backlog — not Sina Command archive)
CYCLE3_H2_PACKS: list[tuple[str, list[str]]] = [
    ("s8-H2-P1", [f"sa-{n:04d}" for n in range(807, 817)]),
    ("s8-H2-P2", [f"sa-{n:04d}" for n in range(817, 833)]),
    ("s8-H2-P3", [f"sa-{n:04d}" for n in range(833, 843)]),
    ("s8-H2-P4", [f"sa-{n:04d}" for n in range(843, 859)]),
    ("s8-H2-P5", [f"sa-{n:04d}" for n in range(859, 869)]),
    ("s8-H2-P6", [f"sa-{n:04d}" for n in range(869, 885)]),
    ("s8-H2-P7", [f"sa-{n:04d}" for n in range(885, 895)]),
    ("s8-H2-P8", [f"sa-{n:04d}" for n in range(895, 901)]),
]

# Cycle 2 commercial packs (10 SAs each except P10)
CYCLE2_PACKS: list[tuple[str, str, str]] = [
    ("s5-P1-wire-runreceipt", "sa-0502", "sa-0511"),
    ("s5-P2-wire-commercial", "sa-0512", "sa-0521"),
    ("s5-P3-wire-commercial", "sa-0522", "sa-0531"),
    ("s5-P4-wire-commercial", "sa-0532", "sa-0541"),
    ("s5-P5-wire-commercial", "sa-0542", "sa-0551"),
    ("s5-P6-wire-commercial", "sa-0552", "sa-0561"),
    ("s5-P7-wire-commercial", "sa-0562", "sa-0571"),
    ("s5-P8-wire-commercial", "sa-0572", "sa-0581"),
    ("s5-P9-wire-commercial", "sa-0582", "sa-0591"),
    ("s5-P10-wire-commercial", "sa-0592", "sa-0597"),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sa_num(sa_id: str) -> int:
    try:
        return int(str(sa_id).split("-")[1])
    except (IndexError, ValueError):
        return 0


def _sa_range_list(start: str, end: str) -> list[str]:
    return [f"sa-{n:04d}" for n in range(_sa_num(start), _sa_num(end) + 1)]


def _plan_map() -> dict[str, dict]:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {p["id"]: p for p in reg.get("plans") or [] if p.get("id")}


def _open_in_list(sa_ids: list[str], plans: dict[str, dict]) -> list[str]:
    return [sa for sa in sa_ids if plans.get(sa, {}).get("status") != "done"]


def _current_pack_name(cfg: dict) -> str:
    resume = str(cfg.get("resume_pack") or "")
    if resume:
        return resume
    block = (cfg.get("execution_order") or [{}])[0]
    packs = block.get("packs") or []
    return str(packs[0] if packs else "")


def _pack_index(pack_name: str) -> int:
    for i, (name, _, _) in enumerate(CYCLE2_PACKS):
        if name == pack_name:
            return i
    return -1


def _record_pack_complete(cfg: dict, pack_name: str, start: str, end: str) -> None:
    history = list(cfg.get("cycle_history") or [])
    if any(h.get("pack") == pack_name for h in history):
        return
    history.append(
        {
            "cycle": cfg.get("cycle") or 2,
            "pack": pack_name,
            "completed_at": _now(),
            "sa_range": [start, end],
            "turns": len(_sa_range_list(start, end)) * 3,
            "note": f"{pack_name} exhausted — registry done",
        }
    )
    cfg["cycle_history"] = history


def _apply_h2_pack(cfg: dict, pack_name: str, force_ids: list[str]) -> dict:
    open_ids = _open_in_list(force_ids, _plan_map())
    achievable = len(open_ids) if open_ids else len(force_ids)
    block = {
        "phase": "s8",
        "phase_id": "phase-s8-hub-ui-ux",
        "packs": [pack_name],
        "pick_strategy": "force_list",
        "force_sa_ids": force_ids,
        "achievable_count": achievable,
        "allow_openrouter": False,
    }
    cfg["execution_order"] = [block]
    cfg["total_achievable_headless"] = achievable
    cfg["resume_pack"] = pack_name
    cfg["resume_sa"] = open_ids[0] if open_ids else force_ids[0]
    cfg["cycle"] = 3
    cfg["law"] = "cycle-3: Hub 2 machine drain — phase-s8 · Sina Command quarantine"
    if "s8" in (cfg.get("skip_phases") or []):
        cfg["skip_phases"] = [p for p in cfg["skip_phases"] if p != "s8"]
    cfg["updated_at"] = _now()
    return cfg


def _h2_pack_index(pack_name: str) -> int:
    for i, (name, _) in enumerate(CYCLE3_H2_PACKS):
        if name == pack_name:
            return i
    return -1


def _apply_pack(cfg: dict, pack_name: str, start: str, end: str) -> dict:
    force_ids = _sa_range_list(start, end)
    open_ids = _open_in_list(force_ids, _plan_map())
    achievable = len(open_ids) if open_ids else len(force_ids)

    block = {
        "phase": "s5",
        "phase_id": "phase-s5-commercial-lanes",
        "packs": [pack_name],
        "pick_strategy": "force_list",
        "force_sa_ids": force_ids,
        "achievable_count": achievable,
        "allow_openrouter": False,
    }
    cfg["execution_order"] = [block]
    cfg["total_achievable_headless"] = achievable
    cfg["resume_pack"] = pack_name
    cfg["resume_sa"] = open_ids[0] if open_ids else start
    cfg["updated_at"] = _now()
    return cfg


def advance_exhausted_pack(*, write: bool = True) -> dict:
    """If current force_list has zero open SAs, advance to next cycle-2 pack."""
    if not CONFIG.is_file():
        return {"ok": False, "error": "missing_config"}
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if not cfg.get("enabled"):
        return {
            "ok": True,
            "advanced": False,
            "reason": cfg.get("idle_reason") or "phase_strict_idle",
            "enabled": False,
        }

    plans = _plan_map()
    block = (cfg.get("execution_order") or [{}])[0]
    force = list(block.get("force_sa_ids") or [])
    open_ids = _open_in_list(force, plans)

    if open_ids:
        return {
            "ok": True,
            "advanced": False,
            "reason": "pack_still_open",
            "open_count": len(open_ids),
            "resume_sa": open_ids[0],
        }

    cur = _current_pack_name(cfg)
    h2_idx = _h2_pack_index(cur)
    if h2_idx >= 0:
        if force:
            _record_pack_complete(cfg, cur, force[0], force[-1])
        next_h2 = h2_idx + 1
        if next_h2 >= len(CYCLE3_H2_PACKS):
            cfg["updated_at"] = _now()
            cfg["enabled"] = False
            cfg["idle_at"] = _now()
            cfg["idle_reason"] = "cycle3_h2_complete"
            if write:
                CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
            return {
                "ok": True,
                "advanced": False,
                "reason": "cycle3_h2_complete",
                "completed_pack": cur,
            }
        next_name, next_ids = CYCLE3_H2_PACKS[next_h2]
        cfg = _apply_h2_pack(cfg, next_name, next_ids)
        if write:
            CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
            STATE.write_text(
                json.dumps(
                    {
                        "next_pos": 1,
                        "last_advanced_at": _now(),
                        "last_completed_pos": 0,
                        "reset_by": "phase_strict_pack_advance_v1",
                        "reason": f"advanced {cur} → {next_name}",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        open_next = _open_in_list(next_ids, plans)
        return {
            "ok": True,
            "advanced": True,
            "from_pack": cur,
            "to_pack": next_name,
            "resume_sa": cfg.get("resume_sa"),
            "open_count": len(open_next),
            "sa_range": [next_ids[0], next_ids[-1]] if next_ids else [],
        }

    idx = _pack_index(cur)
    if idx < 0:
        # Infer from force list start
        if force:
            start = force[0]
            for i, (_, ps, pe) in enumerate(CYCLE2_PACKS):
                if _sa_num(start) >= _sa_num(ps) and _sa_num(start) <= _sa_num(pe):
                    idx = i
                    cur = CYCLE2_PACKS[i][0]
                    break

    if idx < 0:
        open_s8 = _open_in_list(CYCLE3_H2_PACKS[0][1], plans)
        if open_s8:
            next_name, next_ids = CYCLE3_H2_PACKS[0]
            cfg = _apply_h2_pack(cfg, next_name, next_ids)
            if write:
                CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
                STATE.write_text(
                    json.dumps(
                        {
                            "next_pos": 1,
                            "last_advanced_at": _now(),
                            "reset_by": "phase_strict_pack_advance_v1",
                            "reason": "bootstrap_hub2_p1",
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
            return {
                "ok": True,
                "advanced": True,
                "from_pack": cur,
                "to_pack": next_name,
                "resume_sa": cfg.get("resume_sa"),
                "open_count": len(open_s8),
                "reason": "bootstrap_hub2_p1",
            }
        return {"ok": False, "error": "unknown_current_pack", "resume_pack": cur}

    if force:
        _record_pack_complete(cfg, cur, force[0], force[-1])

    next_idx = idx + 1
    if next_idx >= len(CYCLE2_PACKS):
        if force:
            _record_pack_complete(cfg, cur, force[0], force[-1])
        next_name, next_ids = CYCLE3_H2_PACKS[0]
        cfg = _apply_h2_pack(cfg, next_name, next_ids)
        if write:
            CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
            STATE.write_text(
                json.dumps(
                    {
                        "next_pos": 1,
                        "last_advanced_at": _now(),
                        "last_completed_pos": 0,
                        "reset_by": "phase_strict_pack_advance_v1",
                        "reason": f"cycle2_complete → {next_name}",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        open_next = _open_in_list(next_ids, plans)
        return {
            "ok": True,
            "advanced": True,
            "from_pack": cur or "cycle2_complete",
            "to_pack": next_name,
            "resume_sa": cfg.get("resume_sa"),
            "open_count": len(open_next),
            "sa_range": [next_ids[0], next_ids[-1]] if next_ids else [],
            "reason": "cycle2_complete_to_hub2",
        }

    next_name, next_start, next_end = CYCLE2_PACKS[next_idx]
    cfg = _apply_pack(cfg, next_name, next_start, next_end)

    if write:
        CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        state = {
            "next_pos": 1,
            "last_advanced_at": _now(),
            "last_completed_pos": 0,
            "skip_sa_slice": False,
            "skipped_positions": 0,
            "reset_by": "phase_strict_pack_advance_v1",
            "reason": f"advanced {cur} → {next_name}",
        }
        STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    open_next = _open_in_list(_sa_range_list(next_start, next_end), plans)
    return {
        "ok": True,
        "advanced": True,
        "from_pack": cur,
        "to_pack": next_name,
        "resume_sa": cfg.get("resume_sa"),
        "open_count": len(open_next),
        "sa_range": [next_start, next_end],
    }


def heal_exhausted_pack() -> dict:
    """Advance if needed, then rebuild phase-strict queue (or write idle when cycle complete)."""
    adv = advance_exhausted_pack(write=True)
    if not adv.get("ok"):
        return adv
    rebuild = bool(
        adv.get("advanced")
        or adv.get("reason") in ("pack_still_open", "cycle3_h2_complete", "phase_strict_idle")
        or adv.get("reason", "").endswith("_complete")
    )
    if rebuild:
        idle_reasons = {"cycle3_h2_complete", "phase_strict_idle"}
        if adv.get("reason") in idle_reasons or not adv.get("enabled", True):
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from healthy_queue_ssot_lib import write_phase_strict_idle_queue  # noqa: WPS433

            idle = write_phase_strict_idle_queue(
                reason=str(adv.get("reason") or "cycle3_h2_complete"), write=True
            )
            return {"ok": True, "advance": adv, "build": {"ok": True, "idle": True, "idle_queue": idle}}
        import subprocess

        builder = Path(__file__).resolve().parent / "build_phase_strict_queue_v1.py"
        if builder.is_file():
            proc = subprocess.run(
                [sys.executable, str(builder), "--json", "--no-activate"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if proc.returncode != 0:
                return {"ok": False, "advance": adv, "build_error": (proc.stderr or proc.stdout)[:500]}
            try:
                build = json.loads(proc.stdout or "{}")
            except json.JSONDecodeError:
                build = {"raw": (proc.stdout or "")[:200]}
            return {"ok": True, "advance": adv, "build": build}
    return {"ok": True, "advance": adv, "build_skipped": True}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Advance phase-strict pack when exhausted")
    p.add_argument("--json", action="store_true")
    p.add_argument("--heal", action="store_true", help="Advance + rebuild queue")
    args = p.parse_args()
    row = heal_exhausted_pack() if args.heal else advance_exhausted_pack()
    if args.json or args.heal:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
