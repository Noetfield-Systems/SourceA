#!/usr/bin/env python3
"""Compact SourceA — move database/archive planes to SinaaiDataBase; leave living center."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINAIDB = Path.home() / "Desktop" / "SinaaiDataBase"
BATCH = "sourcea-exit-2026-06-23"
DEST = SINAIDB / "archive" / BATCH
MANIFEST = ROOT / "data" / "sourcea-compact-migration-v1.json"

RETIRED_CURSOR_RULES = (
    "000-founder-rules.mdc",
    "001-founder-zero-sina-command-name.mdc",
    "agent-report-story-quality.mdc",
    "sina-command-ui.mdc",
    "prompt-queue.mdc",
    "background-terminal-cart-check.mdc",
    "sina-advisor.mdc",
    "sina-command-protected.mdc",
    "sina-command-readonly.mdc",
)

PLAN_PROMPT_GLOBS = (
    "sourcea-1000/prompts",
    "sourcea--1000/prompts",
    "enforcement-1000/prompts",
    "broker-pack-1000/prompts",
    "automation-converge-1000/prompts",
    "automation-fast-track-100/prompts",
    "healthy-prompt-pack-v1/prompts",
    "worker-dual-40/prompts",
    "devbridge-extension-300/prompts",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _bytes(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        try:
            return path.stat().st_size
        except OSError:
            return 0
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def _move_tree(src: Path, dst: Path, *, dry_run: bool) -> dict[str, Any] | None:
    if not src.exists():
        return None
    rel = src.relative_to(ROOT).as_posix() if src.is_relative_to(ROOT) else str(src)
    sz = _bytes(src)
    row = {"from": rel, "to": str(dst), "bytes": sz}
    if dry_run:
        row["dry_run"] = True
        return row
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    shutil.move(str(src), str(dst))
    return row


def _write_archive_stub() -> None:
    stub = ROOT / "archive" / "README.md"
    stub.parent.mkdir(parents=True, exist_ok=True)
    stub.write_text(
        f"""# Archive broker — not in SourceA (living center)

**Moved:** {_now()}  
**Database plane:** `{DEST}/archive-from-sourcea/`

SourceA keeps **living code + law SSOT only**. All historical attachments, stale trials, and superseded material live in **SinaaiDataBase** (search/archive broker — no daily jobs).

```bash
# Audit read (search only)
ls ~/Desktop/SinaaiDataBase/archive/{BATCH}/
```

**Living SSOT:** `data/sourcea-living-center-v1.json` · `START_HERE_COMPACT_v1.md`
""",
        encoding="utf-8",
    )


def _write_living_center() -> None:
    center = {
        "schema": "sourcea-living-center-v1",
        "version": "1.0.0",
        "at": _now(),
        "one_law": "SourceA = compact living center — apps · scripts · cloud · data SSOT · 8 cursor rules · brain-os entry law only.",
        "archive_broker": str(DEST),
        "sinaaidatabase": str(SINAIDB),
        "planes": {
            "product": ["apps/", "packages/", "SourceA-landing/green-unified/", "witnessbc-site/"],
            "cloud": ["cloud/", "scripts/deploy_fbe_railway_v1.py"],
            "data_ssot": ["data/*.json", "PROGRAM_PROGRESS.json"],
            "law_entry": [
                "brain-os/law/entry/START_HERE_LOCKED_v1.md",
                "brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md",
                "brain-os/INDEX_LOCKED_v1.md",
            ],
            "cursor_rules_always": 8,
            "cursor_rules_doc": "data/cursor-cost-intelligence-routing-v1.json",
        },
        "forbidden_in_sourcea": [
            "archive attachments as daily law",
            "superseded cursor rules",
            "1000-prompt trees locally (broker only)",
            "duplicate os/plan-library",
        ],
        "proposal": "docs/SOURCEA_FOUNDER_AI_AGENTIC_PLATFORM_PROPOSAL_v1.md",
    }
    path = ROOT / "data" / "sourcea-living-center-v1.json"
    path.write_text(json.dumps(center, indent=2) + "\n", encoding="utf-8")


def compact(*, dry_run: bool) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    DEST.mkdir(parents=True, exist_ok=True)

    # 1) Full archive plane
    src_archive = ROOT / "archive"
    if src_archive.exists() and any(src_archive.iterdir()):
        row = _move_tree(src_archive, DEST / "archive-from-sourcea", dry_run=dry_run)
        if row:
            actions.append(row)

    # 2) Retired cursor rules
    rules_dst = DEST / "cursor-rules-retired"
    for name in RETIRED_CURSOR_RULES:
        src = ROOT / ".cursor" / "rules" / name
        if src.is_file():
            row = _move_tree(src, rules_dst / name, dry_run=dry_run)
            if row:
                actions.append(row)

    # 3) Plan-registry prompt trees (database — not living)
    pr = ROOT / "brain-os" / "plan-registry"
    for rel in PLAN_PROMPT_GLOBS:
        src = pr / rel
        if src.is_dir():
            row = _move_tree(src, DEST / "plan-registry-prompts" / rel.replace("/", "__"), dry_run=dry_run)
            if row:
                actions.append(row)

    # 4) os/plan-library duplicate
    os_pl = ROOT / "os" / "plan-library"
    if os_pl.is_dir():
        row = _move_tree(os_pl, DEST / "os-plan-library", dry_run=dry_run)
        if row:
            actions.append(row)

    # 5) Repo execution logs
    for rel in ("REPO_EXECUTION_LOGS", "data/repo-logs"):
        src = ROOT / rel
        if src.exists():
            row = _move_tree(src, DEST / rel.replace("/", "_"), dry_run=dry_run)
            if row:
                actions.append(row)

    if not dry_run:
        _write_archive_stub()
        _write_living_center()
        broker_manifest = {
            "schema": "sinaaidb-sourcea-exit-v1",
            "batch": BATCH,
            "moved_at": _now(),
            "from_repo": str(ROOT),
            "actions_count": len(actions),
            "living_center": str(ROOT / "data/sourcea-living-center-v1.json"),
        }
        (DEST / "manifest.json").write_text(json.dumps(broker_manifest, indent=2) + "\n", encoding="utf-8")

    freed = sum(a.get("bytes", 0) for a in actions)
    return {
        "schema": "sourcea-compact-migration-v1",
        "at": _now(),
        "dry_run": dry_run,
        "dest": str(DEST),
        "freed_bytes": freed,
        "freed_mb": round(freed / 1_000_000, 1),
        "actions": actions,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Compact SourceA → SinaaiDataBase archive")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = compact(dry_run=not args.apply)
    MANIFEST.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        mode = "DRY-RUN" if row["dry_run"] else "APPLIED"
        print(f"SOURCEA_COMPACT {mode} freed≈{row['freed_mb']}MB → {row['dest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
