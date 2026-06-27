#!/usr/bin/env python3
"""Governance SSOT registry — active/superseded/stale check.

Registry: data/sourcea-governance-ssot-registry-v1.json
Receipt: ~/.sina/sourcea-governance-ssot-registry-check-v1.json (with --write-receipt)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "sourcea-governance-ssot-registry-v1.json"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-governance-ssot-registry-check-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from governance_paths_v1 import AUTHORITY_INDEX, AUTHORITY_REGISTRY_GOV, LAW_ROOT_INDEX  # noqa: E402

RULE_LIKE_GLOBS_DEFAULT = (
    "brain-os/ssot/*.md",
    "brain-os/roadmap/SOURCEA_*.md",
    "brain-os/law/**/*_LOCKED*.md",
)

LOCKED_PATH_RE = re.compile(
    r"(brain-os/law/[A-Za-z0-9_./-]+_LOCKED[a-zA-Z0-9_.-]*\.md)"
)
LOCKED_BASENAME_RE = re.compile(r"([A-Za-z0-9_./-]+_LOCKED[a-zA-Z0-9_.-]*\.md)")


def _rule_like_globs(reg: dict) -> tuple[str, ...]:
    globs = reg.get("rule_like_globs")
    if isinstance(globs, list) and globs:
        return tuple(str(g) for g in globs)
    return RULE_LIKE_GLOBS_DEFAULT


def _exclude_name_patterns(reg: dict) -> tuple[str, ...]:
    patterns = reg.get("rule_like_exclude_name_patterns")
    if isinstance(patterns, list) and patterns:
        return tuple(str(p) for p in patterns)
    return ("*INDEX_LOCKED*.md", "README_LOCKED*.md")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_registry() -> dict:
    if not REGISTRY.is_file():
        return {"ok": False, "error": "registry_missing", "path": str(REGISTRY)}
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _resolve(path: str | None) -> Path | None:
    if not path:
        return None
    p = ROOT / path
    return p if p.is_file() else None


def _basenames_from_md(text: str) -> set[str]:
    return {m.group(1) for m in LOCKED_BASENAME_RE.finditer(text)}


def _paths_from_md(text: str) -> set[str]:
    paths = {m.group(1) for m in LOCKED_PATH_RE.finditer(text)}
    for basename in _basenames_from_md(text):
        for fp in (ROOT / "brain-os" / "law").rglob(basename):
            if fp.is_file():
                paths.add(str(fp.relative_to(ROOT)))
    return paths


def _law_authority_registered_paths(reg: dict) -> set[str]:
    """Paths declared in authority index, law root index, gov unify manifest, allowlist."""
    paths: set[str] = set()
    corpus_files = [
        AUTHORITY_INDEX,
        LAW_ROOT_INDEX,
        AUTHORITY_REGISTRY_GOV,
    ]
    for rel_key in ("law_authority_index", "law_root_index"):
        rel = reg.get(rel_key)
        if rel:
            corpus_files.append(ROOT / rel)

    for md_file in corpus_files:
        if md_file.is_file():
            paths |= _paths_from_md(md_file.read_text(encoding="utf-8", errors="replace"))

    allowlist = ROOT / "data" / "authority-root-allowlist-v1.json"
    if allowlist.is_file():
        try:
            row = json.loads(allowlist.read_text(encoding="utf-8"))
            for basename in row.get("basenames") or []:
                for fp in (ROOT / "brain-os" / "law").rglob(str(basename)):
                    if fp.is_file():
                        paths.add(str(fp.relative_to(ROOT)))
                root_fp = ROOT / str(basename)
                if root_fp.is_file():
                    paths.add(str(root_fp.relative_to(ROOT)))
        except (OSError, json.JSONDecodeError):
            pass

    return paths


def _registry_paths(entries: list[dict]) -> set[str]:
    paths: set[str] = set()
    for e in entries:
        for key in ("path", "pdf_path", "symlink_path"):
            p = e.get(key)
            if p:
                paths.add(p)
    return paths


def _skip_scan_path(fp: Path, exclude_patterns: tuple[str, ...]) -> bool:
    if "superseded" in fp.parts or "archive" in fp.parts:
        return True
    name = fp.name
    return any(fnmatch(name, pat) for pat in exclude_patterns)


def check_registry(*, write_receipt: bool = False) -> dict:
    reg = load_registry()
    if reg.get("error"):
        return reg

    entries = reg.get("entries") or []
    active_laws = [e for e in entries if e.get("status") == "active" and e.get("family") == "llm_agent_operating_law"]
    issues: list[str] = []
    rows: list[dict] = []

    if len(active_laws) != 1:
        issues.append(f"expected exactly 1 active llm_agent_operating_law, found {len(active_laws)}")

    active_id = reg.get("active_operating_law_id")
    active_row = next((e for e in entries if e.get("id") == active_id), None)
    if not active_row or active_row.get("status") != "active":
        issues.append(f"active_operating_law_id {active_id!r} missing or not active")

    registered_paths = _registry_paths(entries)
    stale_law = reg.get("stale_law")
    if stale_law:
        registered_paths.add(str(stale_law))
    law_authority_paths = _law_authority_registered_paths(reg)
    all_registered = registered_paths | law_authority_paths
    exclude_patterns = _exclude_name_patterns(reg)

    for e in entries:
        p = _resolve(e.get("path"))
        pdf = _resolve(e.get("pdf_path"))
        row = {
            "id": e.get("id"),
            "status": e.get("status"),
            "path": e.get("path"),
            "exists": bool(p or pdf or (e.get("path") is None and e.get("status") == "superseded")),
        }
        if e.get("path") and not p and e.get("status") == "active":
            issues.append(f"active entry missing file: {e.get('path')}")
            row["exists"] = False
        rows.append(row)

    stale: list[dict] = []
    for pattern in _rule_like_globs(reg):
        for fp in ROOT.glob(pattern):
            if _skip_scan_path(fp, exclude_patterns):
                continue
            rel = str(fp.relative_to(ROOT))
            if rel not in all_registered:
                plane = "law" if rel.startswith("brain-os/law/") else "ssot_plane"
                stale.append(
                    {
                        "path": rel,
                        "plane": plane,
                        "reason": "no registry status — ambiguous authority",
                    }
                )

    stale.sort(key=lambda s: (s["plane"], s["path"]))

    result = {
        "ok": len(issues) == 0 and len(stale) == 0,
        "schema": "sourcea-governance-ssot-registry-check-v1",
        "at": _now(),
        "registry_path": str(REGISTRY),
        "law_authority_index": reg.get("law_authority_index"),
        "active_operating_law_id": active_id,
        "active_operating_law_path": active_row.get("path") if active_row else None,
        "active_count": len(active_laws),
        "registered_path_count": len(all_registered),
        "entries_checked": rows,
        "stale_candidates": stale,
        "stale_count": len(stale),
        "stale_by_plane": {
            "law": sum(1 for s in stale if s["plane"] == "law"),
            "ssot_plane": sum(1 for s in stale if s["plane"] == "ssot_plane"),
        },
        "issues": issues,
    }

    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        result["receipt_path"] = str(RECEIPT)

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance SSOT registry check")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()
    row = check_registry(write_receipt=args.write_receipt)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print("OK" if row.get("ok") else "FAIL")
        if row.get("active_operating_law_path"):
            print(f"ACTIVE: {row['active_operating_law_path']}")
        print(f"STALE: {row.get('stale_count', 0)} (law={row.get('stale_by_plane', {}).get('law', 0)})")
        for s in row.get("stale_candidates") or []:
            print(f"STALE?: [{s.get('plane')}] {s['path']}")
        for i in row.get("issues") or []:
            print(f"ISSUE: {i}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
