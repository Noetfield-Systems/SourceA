#!/usr/bin/env python3
"""Governance stairlift — tiered law propagation (hot/warm/full)."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from governance_paths_v1 import (
    AUTHORITY_INDEX,
    GOVERNANCE_ENTRY,
    INCIDENT_FIX_OWNERSHIP,
    NO_FAKE_PROGRESS,
    RESULT_DRIVEN_DISCUSSION,
    SUPER_FAST_HUB,
    WORKER_EVIDENCE_LAW,
)

SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUT = SINA / "governance-stairlift-v1.json"
STATE = SINA / "governance-stairlift-state-v1.json"

WATCH = (
    INCIDENT_FIX_OWNERSHIP,
    NO_FAKE_PROGRESS,
    RESULT_DRIVEN_DISCUSSION,
    SUPER_FAST_HUB,
    GOVERNANCE_ENTRY,
    AUTHORITY_INDEX,
    WORKER_EVIDENCE_LAW,
)

# Runtime SSOT — founder latch / routing must trigger republish (INCIDENT-031 propagation fix)
RUNTIME_WATCH = (
    SINA / "worker-asf-directive-latch-v1.json",
    SINA / "run-inbox-routing-v1.json",
    SINA / "phase-strict-drain-v1.json",
    SINA / "governance-brain-wire-v1.json",
)

TIER_HOT = "hot"    # payload only — turn entry (<200ms on stale)
TIER_WARM = "warm"  # payload + rules loop — closeout on law change (<10s)
TIER_FULL = "full"  # warm + cascade — maintainer / deep validator only


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fingerprint() -> str:
    h = hashlib.sha256()
    for p in WATCH:
        if p.is_file():
            st = p.stat()
            h.update(f"{p}:{st.st_mtime_ns}:{st.st_size}".encode())
    for p in RUNTIME_WATCH:
        if p.is_file():
            st = p.stat()
            h.update(f"runtime:{p}:{st.st_mtime_ns}:{st.st_size}".encode())
    return h.hexdigest()[:16]


def _load_state() -> dict:
    if not STATE.is_file():
        return {}
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _run_rules_loop() -> dict:
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "agent_rules_loop_orchestrator.py"),
                "--phase",
                "founder_rule_change",
                "--json-only",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.stdout.strip():
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError:
                return {"ok": proc.returncode == 0, "raw": proc.stdout[-300:]}
        return {"ok": proc.returncode == 0, "stderr": (proc.stderr or "")[-200:]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}


def _run_cascade_fast() -> dict:
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "governance_propagation_cascade_v1.py"),
                "--reason",
                "governance_stairlift",
                "--fast",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.stdout.strip():
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError:
                return {"ok": proc.returncode == 0}
        return {"ok": proc.returncode == 0}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}


def sync(
    *,
    force: bool = False,
    if_stale: bool = False,
    tier: str = TIER_WARM,
) -> dict:
    t0 = time.monotonic()
    tier = (tier or TIER_WARM).strip().lower()
    if tier not in {TIER_HOT, TIER_WARM, TIER_FULL}:
        tier = TIER_WARM

    fp = _fingerprint()
    prev = _load_state()
    stale = prev.get("fingerprint") != fp
    warm_for = prev.get("warm_done_for")
    full_for = prev.get("full_done_for")

    if if_stale and not stale and not force:
        return {
            "ok": True,
            "skipped": True,
            "reason": "stale_unchanged",
            "fingerprint": fp,
            "tier": tier,
            "ms": int((time.monotonic() - t0) * 1000),
        }

    # Downgrade tier when work already done for this fingerprint
    if not force and not stale:
        pass
    elif tier == TIER_WARM and warm_for == fp:
        tier = TIER_HOT
    elif tier == TIER_FULL and full_for == fp:
        tier = TIER_WARM if warm_for != fp else TIER_HOT

    sys.path.insert(0, str(SCRIPTS))
    from incident_fix_ownership_lib_v1 import payload_for_agents  # noqa: WPS433

    payload = payload_for_agents()
    payload["fingerprint"] = fp
    payload["watch_paths"] = [str(p) for p in WATCH if p.is_file()]
    payload["runtime_watch_paths"] = [str(p) for p in RUNTIME_WATCH if p.is_file()]

    try:
        from founder_directive_ssot_v1 import sync_routing_file  # noqa: WPS433

        sync_routing_file()
    except Exception:
        pass

    SINA.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    rules_loop: dict = {"ok": True, "skipped": True, "reason": f"tier_{tier}"}
    cascade: dict = {"ok": True, "skipped": True, "reason": f"tier_{tier}"}

    if tier in {TIER_WARM, TIER_FULL} and (force or stale or warm_for != fp):
        rules_loop = _run_rules_loop()
    if tier == TIER_FULL and (force or stale or full_for != fp):
        cascade = _run_cascade_fast()

    row = {
        "ok": bool(rules_loop.get("ok", True)),
        "schema": "governance-stairlift-sync-v1",
        "at": _now(),
        "stale": stale,
        "forced": force,
        "tier": tier,
        "ms": int((time.monotonic() - t0) * 1000),
        "fingerprint": fp,
        "payload": payload,
        "rules_loop": rules_loop,
        "cascade_fast": cascade,
        "law": "SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1.md",
    }

    new_state = {
        "fingerprint": fp,
        "at": _now(),
        "last_sync": {"tier": tier, "ms": row["ms"], "at": row["at"]},
    }
    if tier in {TIER_WARM, TIER_FULL} and rules_loop.get("ok", True) and not rules_loop.get("skipped"):
        new_state["warm_done_for"] = fp
    if tier == TIER_FULL and cascade.get("ok", True) and not cascade.get("skipped"):
        new_state["full_done_for"] = fp
    if prev.get("warm_done_for") and prev.get("fingerprint") == fp:
        new_state["warm_done_for"] = prev["warm_done_for"]
    if prev.get("full_done_for") and prev.get("fingerprint") == fp:
        new_state["full_done_for"] = prev["full_done_for"]

    STATE.write_text(json.dumps(new_state, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true")
    p.add_argument("--if-stale", action="store_true")
    p.add_argument("--tier", choices=[TIER_HOT, TIER_WARM, TIER_FULL], default=TIER_WARM)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = sync(force=args.force, if_stale=args.if_stale, tier=args.tier)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
