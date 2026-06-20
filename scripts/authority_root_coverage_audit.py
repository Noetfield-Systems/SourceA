#!/usr/bin/env python3
"""Root *_LOCKED*.md coverage audit — T1/T2/T3 tiers + fail list for validators."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md"
LAW_ROOT = ROOT / "brain-os/entry/LAW_ROOT_INDEX_LOCKED_v1.md"
MANIFEST = ROOT / "SOURCEA_AUTHORITY_REGISTRY_GOV_UNIFY_BATCH_2026-06-11_LOCKED_v1.md"
DATA_ALLOWLIST = ROOT / "data" / "authority-root-allowlist-v1.json"


def _basenames_from_md(text: str) -> set[str]:
    return {m.group(1) for m in re.finditer(r"([A-Za-z0-9_./-]+_LOCKED[a-zA-Z0-9_.-]*\.md)", text)}


def root_locked_files() -> list[str]:
    return sorted(p.name for p in ROOT.glob("*_LOCKED*.md") if p.is_file())


def authority_basenames() -> set[str]:
    if not INDEX.is_file():
        return set()
    return _basenames_from_md(INDEX.read_text(encoding="utf-8", errors="replace"))


def law_root_basenames() -> set[str]:
    if not LAW_ROOT.is_file():
        return set()
    return _basenames_from_md(LAW_ROOT.read_text(encoding="utf-8", errors="replace"))


def incident_corpus_basenames() -> set[str]:
    from ecosystem_incidents_index import LOCKED_ROOT_INCIDENT_REPORTS  # noqa: WPS433

    return {Path(p).name for p in LOCKED_ROOT_INCIDENT_REPORTS}


def manifest_allowlist_basenames() -> set[str]:
    allow: set[str] = set()
    if MANIFEST.is_file():
        text = MANIFEST.read_text(encoding="utf-8", errors="replace")
        in_allow = False
        for line in text.splitlines():
            if line.strip().startswith("## Allowlist"):
                in_allow = True
                continue
            if in_allow and line.startswith("## ") and "Allowlist" not in line:
                in_allow = False
            if in_allow:
                allow |= _basenames_from_md(line)
    if DATA_ALLOWLIST.is_file():
        try:
            row = json.loads(DATA_ALLOWLIST.read_text(encoding="utf-8"))
            for name in row.get("basenames") or []:
                allow.add(str(name))
        except (OSError, json.JSONDecodeError):
            pass
    return allow


def classify(basename: str, auth: set[str], law: set[str], inc: set[str], allow: set[str]) -> str:
    if basename in auth:
        return "T1"
    if basename in law:
        return "T2"
    if basename in inc or basename in allow:
        return "T3_REGISTERED"
    return "T3_ORPHAN"


def audit() -> dict:
    files = root_locked_files()
    auth = authority_basenames()
    law = law_root_basenames()
    inc = incident_corpus_basenames()
    allow = manifest_allowlist_basenames()
    tiers: dict[str, list[str]] = {"T1": [], "T2": [], "T3_REGISTERED": [], "T3_ORPHAN": []}
    for name in files:
        tier = classify(name, auth, law, inc, allow)
        tiers[tier].append(name)
    return {
        "ok": len(tiers["T3_ORPHAN"]) == 0,
        "total": len(files),
        "counts": {k: len(v) for k, v in tiers.items()},
        "tiers": tiers,
        "orphans": tiers["T3_ORPHAN"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true", help="Exit 1 if any T3 orphan")
    args = parser.parse_args()
    result = audit()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Root LOCKED files: {result['total']}")
        for tier, count in result["counts"].items():
            print(f"  {tier}: {count}")
        if result["orphans"]:
            print("T3_ORPHAN:")
            for o in result["orphans"]:
                print(f"  - {o}")
    if args.check and not result["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
