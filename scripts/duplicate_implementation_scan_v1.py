#!/usr/bin/env python3
"""L15 duplicate implementation scan — main + open branches overlapping paths."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WATCH_PREFIXES = (
    "data/",
    "scripts/",
    ".github/workflows/",
    "cloud/workers/",
    "docs/GOVERNED_AUTORUN",
    "docs/GITHUB_AUTOMATION",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=str(ROOT), text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        return ""


def _branch_files(ref: str) -> set[str]:
    out = _git("ls-tree", "-r", "--name-only", ref)
    if not out:
        return set()
    return {p for p in out.splitlines() if p.startswith(WATCH_PREFIXES)}


def scan(*, paths: list[str] | None = None) -> dict[str, Any]:
    head = _git("rev-parse", "--abbrev-ref", "HEAD") or "HEAD"
    main_ref = "origin/main" if _git("rev-parse", "--verify", "origin/main") else "main"
    if not _git("rev-parse", "--verify", main_ref):
        main_ref = "HEAD"

    target_paths = paths or []
    if not target_paths:
        diff = _git("diff", "--name-only", main_ref, "HEAD")
        target_paths = [p for p in (diff.splitlines() if diff else []) if p.startswith(WATCH_PREFIXES)]

    branches: list[str] = []
    for line in _git("branch", "-r").splitlines():
        b = line.strip().lstrip("origin/")
        if b in ("HEAD", "main", head) or "->" in b:
            continue
        if b.startswith("cursor/") or b.startswith("sandbox/"):
            branches.append(f"origin/{b}" if not b.startswith("origin/") else b)

    overlaps: list[dict[str, Any]] = []
    for ref in branches[:20]:
        ref_files = _branch_files(ref)
        for p in target_paths:
            if p in ref_files:
                overlaps.append({"path": p, "branch": ref, "kind": "path_overlap"})

    ok = len(overlaps) == 0 or len(target_paths) == 0
    return {
        "schema": "duplicate-implementation-scan-v1",
        "at": _now(),
        "ok": ok,
        "head": head,
        "main_ref": main_ref,
        "target_paths": target_paths[:50],
        "branches_scanned": len(branches[:20]),
        "overlaps": overlaps[:30],
        "report_line": (
            "duplicate_scan_clean · no overlapping paths on active branches"
            if ok
            else f"duplicate_scan WARN · {len(overlaps)} overlaps — reconcile before duplicate impl"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paths", nargs="*", default=[])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = scan(paths=args.paths or None)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
