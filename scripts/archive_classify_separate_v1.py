#!/usr/bin/env python3
"""Classify archive/ into using vs stale; move stale buckets under archive/stale/."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
DOCS_ARCHIVE = ROOT / "docs" / "archive"
STALE_ROOT = ARCHIVE / "stale"
USING_INDEX = ARCHIVE / "using" / "README.md"
MANIFEST = ROOT / "data" / "archive-classification-v1.json"

# Top-level buckets that stay at archive/<name> — cited by scripts, law, validators.
USING_BUCKETS = frozenset(
    {
        "attachments",
        "legacy",
        "superseded",
        "root-stubs",
        "using",
    }
)

# Frozen clones / trials — no runtime dependency; move to archive/stale/<category>/.
STALE_MOVES: dict[str, str] = {
    "trial-vercel-full-clone-v1": "trials",
    "trial-vercel-local-clones-v1": "trials",
    "trial-vercel-live-snapshot-v1": "trials",
    "noetfield-trial-clone-v1": "trials",
    "witnessbc-journalism-clone-v1": "retired-products",
}

# Paths to rewrite when stale buckets move (old prefix -> new prefix under archive/stale/).
PATH_REWRITES = (
    (
        "archive/witnessbc-journalism-clone-v1",
        "archive/stale/retired-products/witnessbc-journalism-clone-v1",
    ),
)

SCAN_DIRS = (
    ROOT / "scripts",
    ROOT / "brain-os",
    ROOT / "docs",
    ROOT / "data",
    ROOT / "apps",
    ROOT / ".cursor",
    ROOT / "os",
    ROOT / "knowledge-library",
)

SKIP_SCAN_PARTS = frozenset({"archive", "REPO_EXECUTION_LOGS", "data/repo-logs", ".git"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _bucket_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return total


def _count_refs(prefix: str) -> int:
    needle = prefix.replace("\\", "/")
    count = 0
    for base in SCAN_DIRS:
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if any(part in SKIP_SCAN_PARTS for part in rel.split("/")):
                continue
            if path.suffix not in (
                ".py",
                ".sh",
                ".md",
                ".mdc",
                ".json",
                ".yaml",
                ".yml",
                ".ts",
                ".tsx",
                ".js",
                ".html",
            ):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if needle in text:
                count += 1
    return count


def _list_top_buckets() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not ARCHIVE.is_dir():
        return rows
    for child in sorted(ARCHIVE.iterdir()):
        if child.name.startswith("."):
            continue
        if child.name in ("using", "stale", "README.md"):
            continue
        if child.is_file() and child.suffix == ".md":
            continue
        if child.is_dir():
            kind = "dir"
        elif child.is_file():
            kind = "file"
        else:
            continue
        rel = f"archive/{child.name}"
        if child.name in USING_BUCKETS:
            tier = "using"
            reason = "Active archive plane — scripts/law/validators cite this path."
        elif child.name in STALE_MOVES:
            tier = "stale"
            reason = f"Trial/retired clone — move to archive/stale/{STALE_MOVES[child.name]}/"
        else:
            refs = _count_refs(rel)
            tier = "using" if refs > 0 else "stale"
            reason = f"Auto: {refs} active code refs" if refs else "Auto: zero active code refs"
        rows.append(
            {
                "path": rel,
                "kind": kind,
                "tier": tier,
                "bytes": _bucket_size(child),
                "active_refs": _count_refs(rel) if tier == "using" else 0,
                "reason": reason,
            }
        )
    return rows


def _docs_archive_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not DOCS_ARCHIVE.is_dir():
        return rows
    for child in sorted(DOCS_ARCHIVE.iterdir()):
        if child.name.startswith("."):
            continue
        rel = f"docs/archive/{child.name}"
        refs = _count_refs(rel)
        rows.append(
            {
                "path": rel,
                "kind": "dir" if child.is_dir() else "file",
                "tier": "using_plane",
                "bytes": _bucket_size(child),
                "active_refs": refs,
                "reason": "docs/archive = superseded-draft destination plane (content stale; folder in use).",
            }
        )
    return rows


def _write_using_readme(buckets: list[dict[str, Any]]) -> None:
    using_dir = ARCHIVE / "using"
    using_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Archive — using (active planes)",
        "",
        f"**Built:** {_now()}",
        "",
        "These paths are cited by live scripts, law, or validators. **Do not move** without updating references.",
        "",
        "| Path | Size | Refs | Why |",
        "|------|------|------|-----|",
    ]
    for row in buckets:
        if row["tier"] != "using":
            continue
        if row["path"] in ("archive/using", "archive/stale"):
            continue
        sz = row["bytes"]
        if sz >= 1_000_000:
            size_s = f"{sz / 1_000_000:.1f} MB"
        elif sz >= 1000:
            size_s = f"{sz / 1000:.1f} KB"
        else:
            size_s = f"{sz} B"
        lines.append(
            f"| `{row['path']}/` | {size_s} | {row.get('active_refs', 0)} | {row['reason']} |"
        )
    lines += [
        "",
        "## docs/archive/",
        "",
        "Superseded drafts and quarantined UI experiments — destination plane per `infra/cleanup/README.md`.",
        "",
        "Stale trial clones live under `archive/stale/` — see `archive/stale/README.md`.",
        "",
        f"Machine manifest: `data/archive-classification-v1.json`",
    ]
    USING_INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _stale_inventory() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not STALE_ROOT.is_dir():
        return rows
    for category in sorted(STALE_ROOT.iterdir()):
        if not category.is_dir() or category.name.startswith("."):
            continue
        if category.name == "README.md":
            continue
        for bucket in sorted(category.iterdir()):
            if bucket.name.startswith("."):
                continue
            rel = f"archive/stale/{category.name}/{bucket.name}"
            rows.append(
                {
                    "path": rel,
                    "category": category.name,
                    "bytes": _bucket_size(bucket),
                    "note": "Frozen — audit / git history only",
                }
            )
    return rows


def _write_stale_readme(moved: list[dict[str, Any]]) -> None:
    STALE_ROOT.mkdir(parents=True, exist_ok=True)
    readme = STALE_ROOT / "README.md"
    inventory = _stale_inventory()
    display = moved if moved else inventory
    lines = [
        "# Archive — stale (frozen audit only)",
        "",
        f"**Built:** {_now()}",
        "",
        "Trial Vercel clones, retired product mirrors, and zero-ref buckets. **Not** daily law or factory intake.",
        "",
        "| Path | Category | Size | Note |",
        "|------|----------|------|------|",
    ]
    for row in display:
        sz = row.get("bytes", 0)
        if sz >= 1_000_000:
            size_s = f"{sz / 1_000_000:.1f} MB"
        elif sz >= 1000:
            size_s = f"{sz / 1000:.1f} KB"
        else:
            size_s = f"{sz} B"
        lines.append(
            f"| `{row['path']}` | {row.get('category', '—')} | {size_s} | {row.get('note', '')} |"
        )
    if not display:
        lines.append("| _(none yet)_ | — | — | Run `--apply` to move stale buckets |")
    lines += [
        "",
        "Law pointer for WitnessBC journalism clone: update `data/witnessbc-two-lane-observe-v1.json` if path changes.",
    ]
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _apply_moves() -> list[dict[str, Any]]:
    moved: list[dict[str, Any]] = []
    for name, category in STALE_MOVES.items():
        src = ARCHIVE / name
        if not src.exists():
            continue
        dst = STALE_ROOT / category / name
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        moved.append(
            {
                "path": f"archive/stale/{category}/{name}",
                "from": f"archive/{name}",
                "category": category,
                "bytes": _bucket_size(dst),
                "note": "Moved by archive_classify_separate_v1.py",
            }
        )
    return moved


def _rewrite_paths() -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for old, new in PATH_REWRITES:
        for base in SCAN_DIRS:
            if not base.is_dir():
                continue
            for path in base.rglob("*"):
                if not path.is_file():
                    continue
                rel = path.relative_to(ROOT).as_posix()
                if "archive/stale" in rel and path.suffix not in (".py", ".md", ".json"):
                    continue
                if path.suffix not in (".py", ".md", ".json", ".mdc", ".yaml", ".yml", ".sh"):
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except OSError:
                    continue
                if old not in text:
                    continue
                path.write_text(text.replace(old, new), encoding="utf-8")
                actions.append({"path": rel, "rewrote": f"{old} -> {new}"})
    return actions


def main() -> int:
    ap = argparse.ArgumentParser(description="Classify and separate archive using vs stale")
    ap.add_argument("--apply", action="store_true", help="Move stale buckets to archive/stale/")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    buckets = _list_top_buckets()
    docs_rows = _docs_archive_rows()
    moved: list[dict[str, Any]] = []
    rewrites: list[dict[str, str]] = []

    if args.apply:
        moved = _apply_moves()
        if moved:
            rewrites = _rewrite_paths()
        buckets = _list_top_buckets()

    _write_using_readme(buckets)
    _write_stale_readme(moved)

    row = {
        "schema": "archive-classification-v1",
        "built_at": _now(),
        "using_buckets": [b for b in buckets if b["tier"] == "using"],
        "stale_buckets": _stale_inventory(),
        "docs_archive": docs_rows,
        "moved": moved,
        "path_rewrites": rewrites,
        "law": "infra/cleanup/README.md",
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        using_n = len(row["using_buckets"])
        stale_n = len(row["stale_buckets"])
        print(f"ARCHIVE_CLASSIFY using={using_n} stale={stale_n} moved={len(moved)}")
        print(f"  manifest: {MANIFEST}")
        print(f"  using index: {USING_INDEX}")
        print(f"  stale index: {STALE_ROOT / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
