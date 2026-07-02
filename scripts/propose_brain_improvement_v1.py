#!/usr/bin/env python3
"""Propose a brain improvement from a sandbox branch — local tests + verifier metadata."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPOSALS_DIR = ROOT / "reports/brain-improvement-proposals-v1"
BRAIN_CORE_TESTS = ROOT / "tests/brain_core_v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_tests() -> tuple[bool, str]:
    if not BRAIN_CORE_TESTS.is_dir():
        return True, "skipped_no_tests"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(BRAIN_CORE_TESTS), "-q"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    tail = (result.stdout + result.stderr).strip()[-800:]
    return result.returncode == 0, tail


def current_branch() -> str:
    return subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Propose brain improvement from sandbox branch.")
    parser.add_argument("--domain", default="brain_core", help="brain_core | locked_defs | contract_pages")
    parser.add_argument("--desc", required=True, help="Short description slug")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    branch = current_branch()
    if not branch.startswith("sandbox/brain/"):
        print(f"WARN: branch {branch!r} does not match sandbox/brain/<domain>/<desc>")

    tests_ok, tests_tail = run_tests()
    proposal = {
        "schema": "brain_improvement_proposal_v1",
        "proposed_at": _now(),
        "branch": branch,
        "domain": args.domain,
        "description": args.desc,
        "artifact_type": "brain_worker_bundle",
        "proposal_label": f"{args.domain}:{args.desc}",
        "local_tests_ok": tests_ok,
        "local_tests_tail": tests_tail,
        "next_steps": [
            "Push branch to origin",
            "Run SG scripts/run_parallel_brain_candidates_v1.sh",
            "Gate with --sandbox-id brain_worker when PASS",
        ],
    }

    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    slug = args.desc.replace("/", "-").replace(" ", "-")[:48]
    out = PROPOSALS_DIR / f"{args.domain}-{slug}.json"
    out.write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    proposal["proposal_path"] = str(out)

    if args.json:
        print(json.dumps(proposal, indent=2, sort_keys=True))
    else:
        print(f"proposal: {out}")
        print(f"local_tests_ok={tests_ok}")

    return 0 if tests_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
