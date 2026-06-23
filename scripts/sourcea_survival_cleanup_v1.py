#!/usr/bin/env python3
"""SourceA survival cleanup — let go of past weight; keep only live wiring."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STALE = ROOT / "archive" / "stale"
MANIFEST = ROOT / "data" / "sourcea-survival-cleanup-v1.json"

# Safe delete without manifest (infra/cleanup/README Phase 4).
CACHE_GLOBS = ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache")

# Move to archive/stale/ — heavy, zero or audit-only live wiring.
STALE_MOVES: list[tuple[str, str, str]] = [
    (
        "archive/attachments/evidence",
        "archive/stale/evidence",
        "345MB AEG evidence blobs — audit only; not daily factory",
    ),
    (
        "data/root-machine/graphify-out",
        "archive/stale/mirrors/graphify-out-v1",
        "22MB graphify output — reproducible; not symlinked at root",
    ),
    (
        "data/root-machine/RESEARCH",
        "archive/stale/mirrors/root-machine-research-v1",
        "Duplicate RESEARCH mirror — canonical vault is RESEARCH/ at repo root",
    ),
    (
        "infra/cleanup/secret-scan-report.txt",
        "archive/stale/cleanup-reports/secret-scan-report-v1.txt",
        "73MB grep dump — regenerate via scan-secrets-v1.sh",
    ),
]

# Local-only purge (gitignored or reproducible).
LOCAL_PURGE_DIRS = (
    ROOT / "commercial-video-factory" / "node_modules",
    ROOT / "commercial-video-factory" / "out",
    ROOT / ".tmp",
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
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return total


def _purge_caches() -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for name in CACHE_GLOBS:
        for path in ROOT.rglob(name):
            if not path.is_dir():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith("archive/stale/") or ".git/" in rel:
                continue
            sz = _bytes(path)
            try:
                shutil.rmtree(path)
                actions.append({"action": "deleted_cache", "path": rel, "bytes": sz})
            except OSError as exc:
                actions.append({"action": "cache_skip", "path": rel, "error": str(exc)})
    for path in ROOT.rglob(".DS_Store"):
        if path.is_file():
            try:
                sz = path.stat().st_size
                path.unlink()
                actions.append(
                    {"action": "deleted_ds_store", "path": path.relative_to(ROOT).as_posix(), "bytes": sz}
                )
            except OSError:
                pass
    return actions


def _move_stale(*, dry_run: bool) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for src_rel, dst_rel, note in STALE_MOVES:
        src = ROOT / src_rel
        dst = ROOT / dst_rel
        if not src.exists():
            continue
        sz = _bytes(src)
        row = {"action": "move_stale", "from": src_rel, "to": dst_rel, "bytes": sz, "note": note}
        if dry_run:
            actions.append({**row, "dry_run": True})
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        shutil.move(str(src), str(dst))
        actions.append(row)
        if src_rel == "archive/attachments/evidence":
            stub = ROOT / "archive" / "attachments" / "evidence"
            stub.parent.mkdir(parents=True, exist_ok=True)
            stub.write_text(
                f"# Moved to `{dst_rel}`\n\nSurvival cleanup {_now()} — audit only.\n",
                encoding="utf-8",
            )
    return actions


def _purge_local_dirs(*, dry_run: bool) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for path in LOCAL_PURGE_DIRS:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT).as_posix()
        sz = _bytes(path)
        row = {"action": "purge_local", "path": rel, "bytes": sz, "note": "Reproducible / gitignored — Mac light"}
        if dry_run:
            actions.append({**row, "dry_run": True})
            continue
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)
        actions.append(row)
    return actions


def _write_secret_scan_stub() -> None:
    stub = ROOT / "infra" / "cleanup" / "secret-scan-report.txt"
    stub.write_text(
        f"# Secret scan report moved\n\n"
        f"Full dump: archive/stale/cleanup-reports/secret-scan-report-v1.txt\n"
        f"Regenerate: bash infra/cleanup/scan-secrets-v1.sh\n"
        f"Moved: {_now()}\n",
        encoding="utf-8",
    )


def _patch_start_here() -> bool:
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA survival cleanup")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    dry = not args.apply

    cache = _purge_caches() if args.apply else []
    moves = _move_stale(dry_run=dry)
    purges = _purge_local_dirs(dry_run=dry)

    patched = False
    if args.apply and any(m.get("to", "").endswith("secret-scan-report-v1.txt") for m in moves):
        _write_secret_scan_stub()
        patched = True
    if args.apply:
        patched = _patch_start_here() or patched

    freed = sum(a.get("bytes", 0) for a in cache + moves + purges)
    row = {
        "schema": "sourcea-survival-cleanup-v1",
        "at": _now(),
        "dry_run": dry,
        "freed_bytes": freed,
        "freed_mb": round(freed / 1_000_000, 1),
        "cache_actions": cache,
        "stale_moves": moves,
        "local_purges": purges,
        "start_here_patched": patched,
        "law": "Let go of past weight — archive/stale/ holds audit; apps/ + cloud hold future.",
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        mode = "DRY-RUN" if dry else "APPLIED"
        print(f"SURVIVAL_CLEANUP {mode} freed≈{row['freed_mb']} MB → {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
