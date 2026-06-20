#!/usr/bin/env python3
"""FORGE FACTORY era transition — archive Goal1 stale state · seed cycle2 queue · activate mode.

Law: data/factory-era-v1.json · data/forge-factory-unified-brand-v1.json
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
ERA_SSOT = ROOT / "data" / "factory-era-v1.json"
QUEUE_SSOT = ROOT / "data" / "forge-factory-queue-cycle2-v1.json"
ARCHIVE_DIR = ROOT / "archive" / "attachments" / "factory-era" / "goal1-bootstrap-1000-complete-2026-06-20"
HOME_QUEUE = SINA / "healthy-queue-30-active.json"
REPO_QUEUE = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts" / "healthy-queue-30-active.json"
HOME_STATE = SINA / "healthy-queue-state-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _archive_snapshot(name: str, src: Path) -> dict:
    if not src.is_file():
        return {"name": name, "ok": False, "skipped": True}
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    dst = ARCHIVE_DIR / src.name
    shutil.copy2(src, dst)
    return {"name": name, "ok": True, "archived_to": str(dst)}


def transition(*, dry_run: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    steps: list[dict] = []
    ok = True

    archive_targets = [
        ("factory-now", SINA / "factory-now-v1.json"),
        ("live-ongoing-prompts", SINA / "live-ongoing-prompts-next-10-v1.json"),
        ("healthy-queue-exhausted", HOME_QUEUE),
        ("factory-mode", SINA / "factory-mode-v1.json"),
    ]
    archived = []
    if not dry_run:
        for name, path in archive_targets:
            archived.append(_archive_snapshot(name, path))

    queue_src = _read(QUEUE_SSOT)
    if not queue_src.get("queue"):
        return {"ok": False, "error": "forge_factory_queue_empty", "steps": steps}

    hq = {
        "schema": "healthy-queue-30-active.v1",
        "product": queue_src.get("product") or "FORGE FACTORY cycle 2",
        "thread": queue_src.get("thread") or "FORGE-FACTORY",
        "repo": "sourcea",
        "count": len(queue_src.get("queue") or []),
        "rhythm": queue_src.get("rhythm") or "CHECK → ACT → VERIFY",
        "law": queue_src.get("law") or "data/forge-factory-unified-brand-v1.json",
        "generated_at": _now(),
        "era": "forge_factory_cycle2",
        "brand": "FORGE FACTORY",
        "phase_strict": False,
        "phase_strict_complete": False,
        "queue_exhausted": False,
        "sa_range": queue_src.get("sa_range") or [],
        "queue": queue_src.get("queue") or [],
    }
    state = {
        "next_pos": 1,
        "last_advanced_at": _now(),
        "last_completed_pos": 0,
        "skip_sa_slice": False,
        "skipped_positions": 0,
        "queue_exhausted": False,
        "era": "forge_factory_cycle2",
    }

    if not dry_run:
        SINA.mkdir(parents=True, exist_ok=True)
        HOME_QUEUE.write_text(json.dumps(hq, indent=2) + "\n", encoding="utf-8")
        HOME_STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        REPO_QUEUE.parent.mkdir(parents=True, exist_ok=True)
        REPO_QUEUE.write_text(json.dumps(hq, indent=2) + "\n", encoding="utf-8")
        era_dst = SINA / "factory-era-v1.json"
        era_dst.write_text(ERA_SSOT.read_text(encoding="utf-8"), encoding="utf-8")

    steps.append({"step": "seed_queue", "ok": True, "head": "sa-1201", "count": hq["count"], "dry_run": dry_run})

    if not dry_run:
        from factory_control_v1 import (  # noqa: WPS433
            KILL_FLAG,
            STOP_RECEIPT,
            _atomic_write,
            _set_mode_file,
            rebuild_factory_now,
        )

        KILL_FLAG.unlink(missing_ok=True)
        stop = _read(STOP_RECEIPT)
        if stop:
            stop.update({"cleared_by_asf": True, "cleared_at": _now(), "cleared_by": "forge_factory_era_transition"})
            _atomic_write(STOP_RECEIPT, stop)
        _set_mode_file("FORGE_FACTORY", set_by="forge_factory_era_transition", reason="FORGE FACTORY cycle 2 active")
        fn = rebuild_factory_now(caller="forge_factory_era_transition", force=True)
        steps.append(
            {
                "step": "factory_mode",
                "ok": True,
                "mode": fn.get("mode"),
                "queue_sa": fn.get("queue_sa"),
                "line": fn.get("line"),
            }
        )
    else:
        steps.append({"step": "factory_mode", "ok": True, "dry_run": True, "mode": "FORGE_FACTORY"})

    if not dry_run:
        try:
            from rule_propagation_fanout_v1 import fanout  # noqa: WPS433

            fan = fanout(reason="forge_factory_era_transition")
            steps.append({"step": "rule_fanout", "ok": bool(fan.get("ok"))})
            ok = ok and bool(fan.get("ok"))
        except Exception as exc:
            steps.append({"step": "rule_fanout", "ok": False, "error": str(exc)[:120]})
            ok = False

        try:
            from queue_ssot_unify_v1 import unify_queue_ssot  # noqa: WPS433

            u = unify_queue_ssot()
            steps.append({"step": "queue_ssot_unify", "ok": bool(u.get("ok", True))})
        except Exception as exc:
            steps.append({"step": "queue_ssot_unify", "ok": False, "error": str(exc)[:120]})

    receipt = {
        "schema": "forge-factory-era-transition-receipt-v1",
        "ok": ok and not dry_run,
        "at": _now(),
        "dry_run": dry_run,
        "era": "forge_factory_cycle2",
        "brand": "FORGE FACTORY",
        "archived": archived,
        "steps": steps,
        "line": f"FORGE FACTORY · cycle2 · queue sa-1201 · mode FORGE_FACTORY · Goal1 archived",
    }
    if not dry_run:
        rp = SINA / "forge-factory-era-transition-receipt-v1.json"
        rp.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="FORGE FACTORY era transition")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = transition(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
