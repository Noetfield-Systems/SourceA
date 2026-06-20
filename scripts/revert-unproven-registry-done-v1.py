#!/usr/bin/env python3
"""Revert inflated REGISTRY done → backlog (batch closeout without receipt)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"
PACK = ROOT / "brain-os/plan-registry/sourcea-1000"
LOG = Path.home() / ".sina/audits/revert-unproven-registry-done-v1.jsonl"

sys.path.insert(0, str(ROOT / "scripts"))
from registry_honest_lib_v1 import audit_registry_done  # noqa: E402
from yaml_quarantine_lib_v1 import quarantine_yaml_for_sa  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _set_md_backlog(rel: str) -> bool:
    path = PACK / rel
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    changed = False
    for st in ("done", "in_progress", "active"):
        pat = f"status: {st}"
        if pat in text:
            text = text.replace(pat, "status: backlog", 1)
            changed = True
            break
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


def revert(*, dry_run: bool = False) -> dict:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    plans = reg["plans"]
    audit = audit_registry_done()
    honest = set(audit.get("honest_done_ids") or [])

    reverted: list[str] = []
    kept: list[str] = sorted(honest)
    quarantined_yaml: list[str] = []

    for pl in plans:
        if pl.get("status") != "done":
            continue
        sa = pl.get("id") or ""
        if sa in honest:
            continue
        reverted.append(sa)
        if not dry_run:
            pl["status"] = "backlog"
            rel = pl.get("path") or ""
            if rel:
                _set_md_backlog(rel)
            moved = quarantine_yaml_for_sa(sa_id=sa, reason="revert_unproven_atomic")
            quarantined_yaml.extend(moved)

    if not dry_run and reverted:
        REG.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")

    row = {
        "ok": True,
        "dry_run": dry_run,
        "reverted_count": len(reverted),
        "kept_honest_count": len(kept),
        "quarantined_yaml_count": len(quarantined_yaml),
        "reverted_sample": reverted[:20],
        "kept": kept,
    }
    _log(row)
    return row


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = revert(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"revert-unproven-registry-done-v1 "
            f"reverted={row['reverted_count']} kept_honest={row['kept_honest_count']} "
            f"dry_run={row['dry_run']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
