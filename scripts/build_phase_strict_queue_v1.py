#!/usr/bin/env python3
"""Build healthy queue from phase-strict manifest — s7 → s9 (s8 hub skipped).

Canonical copy (was ~/.sina only). Auto-advances pack when force_list exhausted.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from healthy_queue_ssot_lib import (  # noqa: E402
    QUEUE_HOME,
    QUEUE_REPO,
    REGISTRY_PATH,
    write_phase_strict_idle_queue,
)  # noqa: E402
from prompt_feasibility_gate import check_text  # noqa: E402

SINA = Path.home() / ".sina"
CONFIG = SINA / "phase-strict-drain-v1.json"
MANIFEST_DIR = SINA / "pack-manifests"

VERIFY_ACHIEVABLE = "cd scripts && bash worker_verify_ultra_v1.sh"
MANDATORY = [
    "brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
    "brain-os/law/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md",
    "brain-os/system/GOAL_EXECUTION_ACTIVE_LOCKED_v1.md",
    "brain-os/plan-registry/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md",
    ".cursor/rules/000-entry-gate.mdc",
]
ROLES = ("check", "act", "verify")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sa_num(sa_id: str) -> int:
    try:
        return int(str(sa_id).split("-")[1])
    except (IndexError, ValueError):
        return 0


def _load_config() -> dict:
    if not CONFIG.is_file():
        raise SystemExit(f"FAIL: missing {CONFIG}")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def _plan_map() -> dict[str, dict]:
    reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {p["id"]: p for p in reg.get("plans") or [] if p.get("id")}


def _achievable_s9_exclude(cfg: dict) -> set[str]:
    return set(cfg.get("exclude_s9_blocked") or [])


def _skip_phase_set(cfg: dict) -> set[str]:
    return {str(p).strip().lower() for p in (cfg.get("skip_phases") or []) if str(p).strip()}


def _collect_sa_ids(cfg: dict, plans: dict[str, dict]) -> list[str]:
    exclude_s9 = _achievable_s9_exclude(cfg)
    skip_phases = _skip_phase_set(cfg)
    out: list[str] = []
    for block in cfg.get("execution_order") or []:
        if str(block.get("phase") or "").lower() in skip_phases:
            continue
        if block.get("pick_strategy") == "force_list":
            for sa in block.get("force_sa_ids") or []:
                pl = plans.get(sa)
                if not pl:
                    continue
                if pl.get("status") == "done":
                    continue
                out.append(sa)
            continue
        start = _sa_num(block.get("sa_start") or "")
        end = _sa_num(block.get("sa_end") or "")
        phase_id = block.get("phase_id") or ""
        for n in range(start, end + 1):
            sa = f"sa-{n:04d}"
            pl = plans.get(sa)
            if not pl:
                continue
            if pl.get("phase") != phase_id:
                continue
            if pl.get("status") == "done":
                continue
            if block.get("phase") == "s9" and sa in exclude_s9:
                continue
            title = pl.get("title") or ""
            prompt = pl.get("agent_prompt") or ""
            feas = check_text(f"{title} {prompt}")
            if not feas.get("ok"):
                continue
            out.append(sa)
    return out


def _role_instruction(role: str, sa: dict, *, allow_openrouter: bool = False) -> str:
    pid, path, title = sa["id"], sa.get("path") or "", sa.get("title") or ""
    if role == "check":
        return (
            f"CHECK ONLY — read `{path}`. Run session-start + spine + find_critical_bugs. "
            f"Report gaps vs task: {title[:80]}. Do NOT implement. Do NOT closeout."
        )
    if role == "act":
        if allow_openrouter:
            return (
                f"ACT — OpenRouter LIVE allowed for `{pid}` only. Implement per .md. "
                f"Task: {title[:80]}. Run validate-eval-packet-v1b-live when instructed. "
                f"One sa only."
            )
        return (
            f"ACT ONLY — implement `{pid}` per its .md. Minimal diff. "
            f"Task: {title[:80]}. One sa only. "
            f"Use disk validators only — NO OpenRouter, NO live eval, NO eval_1b_gate_ok true requirement."
        )
    if allow_openrouter:
        return (
            f"VERIFY + CLOSEOUT — `{pid}` OpenRouter activation. "
            f"Run task verify from .md; broker receipt required. WORKER_ROUND_REPORT → STOP."
        )
    return (
        f"VERIFY + CLOSEOUT — `{pid}` only. Run: {VERIFY_ACHIEVABLE}. "
        f"REGISTRY done · PRIORITY row · WORKER_ROUND_REPORT → STOP."
    )


def _write_pack_manifests(cfg: dict, sa_ids: list[str], plans: dict[str, dict]) -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    idx = 0
    for block in cfg.get("execution_order") or []:
        packs = block.get("packs") or []
        count = int(block.get("achievable_count") or 0)
        chunk = sa_ids[idx : idx + count]
        idx += count
        pos = 0
        for pack_name in packs:
            take = 10 if pack_name != packs[-1] or len(chunk) % 10 == 0 else len(chunk) - pos
            if pack_name == packs[-1] and len(chunk) - pos < 10:
                take = len(chunk) - pos
            pack_sas = chunk[pos : pos + take]
            pos += take
            if not pack_sas:
                continue
            doc = {
                "schema": "pack-manifest-v1",
                "pack_id": pack_name,
                "phase": block.get("phase"),
                "phase_id": block.get("phase_id"),
                "sa_ids": pack_sas,
                "sa_range": [pack_sas[0], pack_sas[-1]],
                "turns": len(pack_sas) * 3,
                "law": "PHASE_STRICT — load this pack only when prior achievable backlog zero",
            }
            (MANIFEST_DIR / f"{pack_name}.json").write_text(
                json.dumps(doc, indent=2) + "\n", encoding="utf-8"
            )


def _sa_allow_openrouter(cfg: dict, sa_id: str) -> bool:
    for block in cfg.get("execution_order") or []:
        if block.get("pick_strategy") == "force_list":
            if sa_id in (block.get("force_sa_ids") or []):
                return bool(block.get("allow_openrouter"))
        start = _sa_num(block.get("sa_start") or "")
        end = _sa_num(block.get("sa_end") or "")
        n = _sa_num(sa_id)
        if start and end and start <= n <= end:
            return bool(block.get("allow_openrouter"))
    return False


def build_queue(*, write: bool = True, run_activate: bool = True) -> dict:
    cfg = _load_config()
    if not cfg.get("enabled"):
        from healthy_queue_ssot_lib import load_healthy_queue, write_phase_strict_idle_queue  # noqa: WPS433

        _, q = load_healthy_queue()
        if q.get("queue_exhausted") or q.get("phase_strict_complete"):
            return {"ok": True, "idle": True, "reason": "phase_strict_disabled_idle", "count": 0}
        idle = write_phase_strict_idle_queue(reason="phase_strict_disabled", write=write)
        return {"ok": True, "idle": True, "reason": "phase_strict_disabled", "idle_queue": idle}

    plans = _plan_map()
    picks = _collect_sa_ids(cfg, plans)

    if not picks:
        from phase_strict_pack_advance_v1 import advance_exhausted_pack  # noqa: WPS433

        adv = advance_exhausted_pack(write=True)
        if adv.get("advanced"):
            cfg = _load_config()
            picks = _collect_sa_ids(cfg, plans)

    expected = int(cfg.get("total_achievable_headless") or 0)
    if expected and len(picks) != expected:
        print(
            f"WARN: expected {expected} achievable SAs, got {len(picks)}",
            file=sys.stderr,
        )

    if not picks:
        idle = write_phase_strict_idle_queue(reason="no_achievable_sas", write=write)
        return {
            "ok": True,
            "idle": True,
            "error": "no_achievable_sas",
            "resume_pack": cfg.get("resume_pack"),
            "hint": "phase_strict_pack_advance_v1.py --heal",
            "idle_queue": idle,
        }

    queue: list[dict] = []
    pos = 0
    for sa_id in picks:
        sa = plans[sa_id]
        or_ok = _sa_allow_openrouter(cfg, sa_id)
        forbidden = [
            "UNATTENDED BATCH",
            "pick 30",
            "implement on CHECK turn",
            "closeout on ACT turn",
        ]
        if not or_ok:
            forbidden.extend(["OpenRouter", "eval_1b_gate_ok true"])
        for role in ROLES:
            pos += 1
            queue.append(
                {
                    "queue_pos": pos,
                    "hp_id": f"hq-{pos:03d}",
                    "queue_role": role,
                    "step_type": {"check": "check", "act": "implement", "verify": "verify_backend"}[role],
                    "sa_id": sa_id,
                    "sa_path": sa.get("path"),
                    "sa_title": sa.get("title"),
                    "sa_tier": sa.get("tier"),
                    "phase": sa.get("phase"),
                    "title": f"[{role.upper()}] {sa_id} — {(sa.get('title') or '')[:60]}",
                    "instruction": _role_instruction(role, sa, allow_openrouter=or_ok),
                    "mandatory_reads": MANDATORY,
                    "verify": VERIFY_ACHIEVABLE if role == "verify" and not or_ok else "see .md — OpenRouter activation path",
                    "closeout": role == "verify",
                    "forbidden": forbidden,
                    "openrouter_allowed": or_ok,
                    "one_sa_per_turn": True,
                }
            )

    doc = {
        "schema": "healthy-queue-30-active.v1",
        "product": "SourceA PHASE_STRICT drain — Hub 2 machine (cycle-3 phase-s8)",
        "thread": "STRATEGIC-SLICE",
        "repo": "sourcea",
        "count": len(queue),
        "rhythm": "3 prompts per sa: check → act → verify+closeout",
        "law": "SOURCEA_PHASE_STRICT_RUN_INBOX_LOCKED_v1.md",
        "generated_at": _now(),
        "phase_strict": True,
        "phase_strict_config": str(CONFIG),
        "pick_floor": cfg.get("resume_sa"),
        "sa_range": [picks[0], picks[-1]] if picks else [],
        "skipped_blockers": [
            "lazy pick_floor forward scan",
            "s4/s5/s6 founder lanes",
            "s2/s3 complete",
            "Hub only (H1/H2) · Command DELETED · Cloud Forge Run active",
            "s9 blocked: sa-0954 sa-0964 sa-0979 sa-0989",
        ],
        "queue": queue,
    }

    _write_pack_manifests(cfg, picks, plans)

    if write:
        QUEUE_HOME.parent.mkdir(parents=True, exist_ok=True)
        QUEUE_HOME.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        if QUEUE_REPO.parent.is_dir():
            QUEUE_REPO.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        if run_activate:
            activator = SINA / "activate-run-inbox-phase-strict-v1.py"
            if activator.is_file():
                subprocess.run(
                    [sys.executable, str(activator), "--json"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

    return {
        "ok": True,
        "path": str(QUEUE_HOME),
        "sa_count": len(picks),
        "turn_count": len(queue),
        "sa_range": doc["sa_range"],
        "first_sa": picks[0] if picks else None,
        "resume_sa": cfg.get("resume_sa"),
        "resume_pack": cfg.get("resume_pack"),
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-activate", action="store_true")
    args = p.parse_args()
    row = build_queue(write=True, run_activate=not args.no_activate)
    if args.json:
        print(json.dumps(row, indent=2))
    elif row.get("ok"):
        if row.get("idle"):
            print(f"PHASE_STRICT idle queue · reason={row.get('error') or 'exhausted'}")
        else:
            print(
                f"PHASE_STRICT queue: {row['sa_count']} SAs · {row['turn_count']} turns · {row['sa_range']}"
            )
    else:
        print(json.dumps(row, indent=2), file=sys.stderr)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
