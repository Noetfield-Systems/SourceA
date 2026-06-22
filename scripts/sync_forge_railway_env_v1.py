#!/usr/bin/env python3
"""Sync Forge Railway env from local vault — never prints secret values."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRETS = Path.home() / ".sina" / "secrets.env"
SERVICE = "sourcea-fbe-runner"


def _parse_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _gh_token() -> str:
    try:
        proc = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode == 0:
            return (proc.stdout or "").strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            timeout=15,
        )
        for line in (proc.stdout or "").splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def sync(*, dry_run: bool = False) -> dict:
    env = _parse_env(SECRETS)
    github = env.get("GITHUB_TOKEN", "").strip() or _gh_token()
    openrouter = env.get("OPENROUTER_API_KEY", "").strip()
    pairs = {
        "FORGE_GITHUB_OWNER": "kazemnezhadsina144-dot",
        "FORGE_GITHUB_REPO": "SourceA",
        "FORGE_GITHUB_PLANS_PATH": "plans",
        "FORGE_GITHUB_REF": "main",
        "FBE_CLOUD_WORKER_URL": "https://sourcea-fbe-runner-production.up.railway.app",
    }
    if openrouter:
        pairs["OPENROUTER_API_KEY"] = openrouter
    if github:
        pairs["GITHUB_TOKEN"] = github
    set_keys = list(pairs.keys())
    missing = []
    if not openrouter:
        missing.append("OPENROUTER_API_KEY")
    if not github:
        missing.append("GITHUB_TOKEN")
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "would_set": set_keys,
            "missing": missing,
        }
    args = ["railway", "variables", "set"]
    for k, v in pairs.items():
        args.append(f"{k}={v}")
    args.extend(["-s", SERVICE])
    proc = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, timeout=120)
    return {
        "ok": proc.returncode == 0,
        "set": set_keys,
        "missing": missing,
        "code": proc.returncode,
        "tail": (proc.stdout or proc.stderr or "")[-400:],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = sync(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print("ok" if row.get("ok") else "fail", "set", row.get("set"), "missing", row.get("missing"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
