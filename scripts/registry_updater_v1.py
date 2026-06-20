#!/usr/bin/env python3
"""SourceA Registry Updater — closes the loop between receipts and REGISTRY.json.

Reads every DONE receipt in receipts/ → marks the matching plan as done in
REGISTRY.json → updates the .md file front matter → prints a summary.

Run after each Worker turn, or standalone to catch up.

Usage:
    python3 scripts/registry_updater_v1.py          # catch-up all DONE receipts
    python3 scripts/registry_updater_v1.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT         = Path(__file__).resolve().parents[1]
REGISTRY     = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"
RECEIPTS_DIR = ROOT / "receipts"
LOG_PATH     = Path.home() / ".sina" / "registry-updater-v1.jsonl"

DONE_STATUSES = {"DONE", "done", "CHECK_PASSED", "PASS", "VERIFIED"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as f:
        f.write(json.dumps({**row, "at": _now()}) + "\n")


def _load_registry() -> tuple[dict | list, list]:
    raw = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw, raw
    plans = raw.get("plans") or raw.get("items") or []
    return raw, plans


def _save_registry(raw: dict | list, plans: list) -> None:
    if isinstance(raw, list):
        REGISTRY.write_text(json.dumps(plans, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        raw_copy = dict(raw)
        key = "plans" if "plans" in raw_copy else "items"
        raw_copy[key] = plans
        REGISTRY.write_text(json.dumps(raw_copy, indent=2, ensure_ascii=False), encoding="utf-8")


def _update_md_status(md_path: Path, dry_run: bool) -> bool:
    """Set status: done in the .md file front matter. Returns True if changed."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return False
    # Match YAML front matter status field
    pattern = r"(^---\n.*?^status:\s*)(\S+)(.*?^---)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not match:
        return False
    current = match.group(2).strip()
    if current == "done":
        return False  # already done
    new_text = text[:match.start(2)] + "done" + text[match.end(2):]
    if not dry_run:
        md_path.write_text(new_text, encoding="utf-8")
    return True


def run(dry_run: bool = False) -> dict:
    if not RECEIPTS_DIR.is_dir():
        return {"ok": True, "updated": 0, "msg": "no receipts dir"}

    raw, plans = _load_registry()
    plan_by_id = {p.get("id", ""): p for p in plans}

    receipts = sorted(RECEIPTS_DIR.glob("sa-*-receipt.json"))
    updated = []
    skipped = []
    not_found = []

    for receipt_file in sorted(receipts):
        try:
            receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        sa_id  = receipt.get("sa_id") or receipt_file.stem.split("-receipt")[0]
        status = receipt.get("status", "")

        if status not in DONE_STATUSES:
            skipped.append(sa_id)
            continue
        if str(status).upper() == "BATCH_CLOSEOUT_ONLY":
            skipped.append(sa_id)
            continue
        if str(receipt.get("round_type") or "").lower() not in ("verify", ""):
            skipped.append(sa_id)
            continue
        evidence = (receipt.get("evidence") or receipt.get("summary") or "").strip()
        if not evidence:
            skipped.append(sa_id)
            continue
        if not sa_id.startswith("sa-") or not receipt_file.name.endswith("-receipt.json"):
            skipped.append(sa_id)
            continue

        plan = plan_by_id.get(sa_id)
        if not plan:
            not_found.append(sa_id)
            continue

        if plan.get("status") == "done":
            skipped.append(sa_id)
            continue

        # Update registry in memory
        if not dry_run:
            plan["status"] = "done"

        # Update .md file front matter
        md_rel = plan.get("path", "")
        md_changed = False
        if md_rel:
            md_path = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / md_rel
            if not md_path.exists():
                md_path = ROOT / md_rel
            md_changed = _update_md_status(md_path, dry_run)

        updated.append(sa_id)
        print(f"  ✅ {sa_id} → done  (md_updated={md_changed})")
        _log({"event": "REGISTRY_UPDATE", "sa_id": sa_id, "dry_run": dry_run})

    if updated and not dry_run:
        _save_registry(raw, plans)

    # Recount
    done_count = sum(1 for p in plans if p.get("status") == "done")
    total = len(plans)

    result = {
        "ok": True,
        "updated": len(updated),
        "skipped": len(skipped),
        "not_found": len(not_found),
        "registry_done": done_count,
        "registry_total": total,
        "dry_run": dry_run,
    }
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Registry: {done_count}/{total} done  (+{len(updated)} this run)")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="SourceA Registry Updater")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    result = run(dry_run=args.dry_run)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
