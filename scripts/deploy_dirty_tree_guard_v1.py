#!/usr/bin/env python3
"""Refuse deploy when task-scoped paths are dirty — unrelated dirt allowed."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SCOPE_PATHS: dict[str, list[str]] = {
    "brain_worker": [
        "cloud/workers/sourcea-brain-chat-v1/",
        "scripts/brain_cli_v1.sh",
    ],
    "landing": [
        "SourceA-landing/green-unified/",
        "scripts/inject_landing_aeg_proof_v1.py",
        "scripts/inject_sourcea_boot_terminal_v1.py",
        "scripts/inject_landing_buyer_trust_v1.py",
        "scripts/publish_sourcea_landing_v1.py",
        "scripts/verify_buyer_proof_hotfix_v1.py",
    ],
    "fbe": [
        "cloud/Dockerfile.fbe-runner",
        "cloud/railway.toml",
        "data/cloud-forge-run-queue-active-v1.json",
        "data/secondary-cloud-forge-run-batch-",
        "scripts/deploy_fbe_railway_v1.py",
        "scripts/generate_client_proof_cloud_batch_v1.py",
    ],
    "intake": [
        "cloud/workers/sourcea-mvp-intake-v1/",
        "scripts/verify_mvp_intake_proof_v1.py",
    ],
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_porcelain() -> list[tuple[str, str]]:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return []
    rows: list[tuple[str, str]] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        status = line[:2].strip() or line[0]
        path = line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip().strip('"')
        rows.append((status, path))
    return rows


def _matches_scope(path: str, prefixes: list[str]) -> bool:
    norm = path.replace("\\", "/")
    for prefix in prefixes:
        p = prefix.replace("\\", "/")
        if norm == p.rstrip("/") or norm.startswith(p):
            return True
    return False


def check(*, scope: str, extra_paths: list[str] | None = None) -> dict[str, Any]:
    prefixes = list(SCOPE_PATHS.get(scope, []))
    if extra_paths:
        prefixes.extend(extra_paths)
    if not prefixes:
        return {"ok": False, "error": f"unknown_scope:{scope}"}
    dirty_all = _git_porcelain()
    scoped = [p for _st, p in dirty_all if _matches_scope(p, prefixes)]
    dirty_total = len(dirty_all)
    dirty_total_cap = 200
    return {
        "ok": not scoped and dirty_total <= dirty_total_cap,
        "schema": "deploy-dirty-tree-guard-v1",
        "at": _now(),
        "scope": scope,
        "scoped_prefixes": prefixes,
        "dirty_scoped": sorted(set(scoped)),
        "dirty_total": dirty_total,
        "dirty_total_cap": dirty_total_cap,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scope", choices=sorted(SCOPE_PATHS), required=True)
    ap.add_argument("--path", action="append", default=[], dest="extra_paths")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = check(scope=args.scope, extra_paths=list(args.extra_paths))
    if args.json:
        print(json.dumps(row, indent=2))
    elif not row["ok"]:
        print("FAIL deploy-dirty-tree-guard: scoped files dirty:", file=sys.stderr)
        for p in row["dirty_scoped"]:
            print(f"  {p}", file=sys.stderr)
    else:
        print(f"PASS deploy-dirty-tree-guard scope={args.scope}")
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
