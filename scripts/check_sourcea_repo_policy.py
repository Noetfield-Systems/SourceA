#!/usr/bin/env python3
"""Validate SourceA repository boundary policy.

The checker is intentionally light enough for Mac founder sessions. It validates
the machine-readable policy and inspects only git path metadata, not payload
contents.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "repo-policy.json"

REQUIRED_OWNS = {
    "kernel/eval machines",
    "traceability",
    "registries",
    "reusable contracts",
    "public API/cloud workers",
    "versioned exports",
}

REQUIRED_NOT_OWN = {
    "active Noetfield product files",
    "active TrustField product files",
    "legal matter files",
    "entity operations files",
}

REQUIRED_DEP_MODES = {
    "contracts",
    "exports",
    "manifests",
    "public API/cloud workers",
}

POLICY_LANE_PATHS = {
    "AGENTS.md",
    ".cursor/rules/sourcea-repo-boundary.mdc",
    "repo-policy.json",
    "scripts/check_sourcea_repo_policy.py",
    "docs/SOURCEA_REPO_POLICY_LOCKED_v1.md",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def load_policy() -> dict[str, Any]:
    try:
        data = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("repo-policy.json is missing")
    except json.JSONDecodeError as exc:
        fail(f"repo-policy.json is invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail("repo-policy.json must contain a JSON object")
    return data


def require_subset(name: str, required: set[str], actual: object) -> None:
    if not isinstance(actual, list):
        fail(f"{name} must be a list")
    missing = sorted(required - set(actual))
    if missing:
        fail(f"{name} is missing required entries: {missing}")


def parse_status_paths() -> list[str]:
    raw = run_git(["status", "--porcelain=v1", "-z", "-uall"])
    records = [record for record in raw.split("\0") if record]
    paths: list[str] = []
    for record in records:
        status = record[:2]
        body = record[3:]
        if status.startswith("R") or status.startswith("C"):
            parts = body.split("\0")
            paths.extend(part for part in parts if part)
        else:
            paths.append(body)
    return sorted(set(paths))


def is_forbidden_loose_path(path: str, forbidden_roots: list[str]) -> bool:
    normalized = path.rstrip("/")
    for root in forbidden_roots:
        clean_root = root.rstrip("/")
        if normalized == clean_root or normalized.startswith(clean_root + "/"):
            return True
    return False


def is_active_product_path(path: str, markers: list[str]) -> bool:
    lowered = path.lower()
    if any(marker.lower() in lowered for marker in markers):
        allowed_context = (
            "archive/",
            "docs/",
            "repo-policy.json",
            ".cursor/rules/",
            "scripts/check_sourcea_repo_policy.py",
            "AGENTS.md",
        )
        return not path.startswith(allowed_context)
    return False


def validate_policy(data: dict[str, Any]) -> None:
    if data.get("version") != "sourcea-repo-policy-v1":
        fail("version must be sourcea-repo-policy-v1")
    if data.get("lane") != "repo-policy":
        fail("lane must be repo-policy")

    authority = data.get("authority")
    if not isinstance(authority, dict):
        fail("authority must be an object")
    if authority.get("role") != "upstream authority engine":
        fail("authority.role must be upstream authority engine")
    require_subset("authority.owns", REQUIRED_OWNS, authority.get("owns"))
    require_subset("authority.does_not_own", REQUIRED_NOT_OWN, authority.get("does_not_own"))

    boundaries = data.get("boundaries")
    if not isinstance(boundaries, dict):
        fail("boundaries must be an object")
    require_subset(
        "boundaries.cross_product_dependency_mode",
        REQUIRED_DEP_MODES,
        boundaries.get("cross_product_dependency_mode"),
    )
    forbidden_modes = boundaries.get("forbidden_cross_product_dependency_mode")
    if not isinstance(forbidden_modes, list) or "internal scripts" not in forbidden_modes:
        fail("boundaries.forbidden_cross_product_dependency_mode must include internal scripts")

    working_tree = data.get("working_tree")
    if not isinstance(working_tree, dict):
        fail("working_tree must be an object")
    max_files = working_tree.get("max_files_per_pass")
    if not isinstance(max_files, int) or not 20 <= max_files <= 40:
        fail("working_tree.max_files_per_pass must be an integer between 20 and 40")
    if working_tree.get("lane_rule") != "one lane, one atomic commit":
        fail("working_tree.lane_rule must be one lane, one atomic commit")
    if working_tree.get("generated_evidence_backlog_rule") != "snapshot + manifest, not loose repo dirt":
        fail("generated/evidence/backlog rule must require snapshot + manifest")

    policy_files = data.get("policy_files")
    if not isinstance(policy_files, list) or set(policy_files) != POLICY_LANE_PATHS:
        fail("policy_files must match the approved SourceA repo-policy lane paths")


def validate_status(data: dict[str, Any], *, clean_tree: bool) -> None:
    paths = parse_status_paths()
    if clean_tree and paths:
        fail(f"working tree is not clean: {len(paths)} dirty path(s)")

    max_files = data["working_tree"]["max_files_per_pass"]
    if len(paths) > max_files:
        fail(f"dirty path count {len(paths)} exceeds max_files_per_pass {max_files}")

    forbidden_roots = data["working_tree"]["forbidden_loose_roots"]
    loose = [path for path in paths if is_forbidden_loose_path(path, forbidden_roots)]
    if loose:
        fail(f"loose generated/evidence/backlog paths must be snapshotted: {loose[:10]}")

    markers = data["boundaries"]["active_product_markers"]
    active_product_paths = [path for path in paths if is_active_product_path(path, markers)]
    if active_product_paths:
        fail(f"active product/legal/entity paths do not belong in SourceA changes: {active_product_paths[:10]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean-tree", action="store_true", help="Require git status --short to be empty.")
    args = parser.parse_args()

    data = load_policy()
    validate_policy(data)
    validate_status(data, clean_tree=args.clean_tree)

    status_count = len(parse_status_paths())
    print(
        json.dumps(
            {
                "ok": True,
                "policy": data["version"],
                "lane": data["lane"],
                "dirty_path_count": status_count,
                "clean_tree_required": args.clean_tree,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
