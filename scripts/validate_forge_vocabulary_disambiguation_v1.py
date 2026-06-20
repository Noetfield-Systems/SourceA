#!/usr/bin/env python3
"""Scan for stale ICP-forge path drift — Forge product name stays canonical."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = (
    "data/icp-forge/",
    "data/icp-forge",
    "icp-output-forge-v1.json",
    "icp-forge-account-v1",
    '"forge_dir"',
    '"forge_now"',
    '"forge_queued"',
    '"forge_gate"',
    "forge each brand",
)
SKIP_DIRS = {"node_modules", ".git", "graphify-out", "receipts", "archive", "agent-control-panel"}
SKIP_FILES = {
    "sourcea-forge-vocabulary-disambiguation-v1.json",
    "icp-output-compiler-v1.json",
    "factory-output-route-compiler-v1.json",
    "brain-os/law/MACHINE_THREE_PIPELINES_CALIBRATE_TUNE_FORGE_LOCKED_v1.md",
    "machine_forge_pipeline_v1.py",
    "machine_three_pipelines_router_v1.py",
    "machine_three_pipelines_lib_v1.py",
    "founder_prompt_pack_build_v1.py",
    "founder_prompt_pack_versions.py",
}


def main() -> int:
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(s in path.parts for s in SKIP_DIRS):
            continue
        if path.name in SKIP_FILES or path.name == "validate_forge_vocabulary_disambiguation_v1.py":
            continue
        if path.suffix not in {".json", ".py", ".md", ".html", ".js"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for term in FORBIDDEN:
            if term in text:
                hits.append(f"{path.relative_to(ROOT)}: {term}")
    if hits:
        print("STALE_ICP_FORGE_DRIFT")
        for h in sorted(set(hits)):
            print(h)
        return 1
    print("PASS — no stale icp-forge vocabulary in active tree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
