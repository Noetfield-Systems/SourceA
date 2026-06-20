#!/usr/bin/env python3
"""Consolidate 777 folder: dedupe + one canonical file per context group."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path.home() / "Desktop/iphone Cloud/_organized/777"
CANON = ROOT / "_CANONICAL"
ARCH = ROOT / "_archive"
ARCH_DUP = ARCH / "duplicates"
ARCH_SUPER = ARCH / "superseded"
REPORT = Path(__file__).resolve().parents[1] / "imports/iphone-cloud/777-consolidate-report.json"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def context_key(name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"^ic-\d+__", "", stem, flags=re.I)
    stem = re.sub(r"__dup\d*$", "", stem, flags=re.I)
    stem = re.sub(r"\s*\(\d+\)\s*$", "", stem)
    stem = re.sub(r"\s+\d+$", "", stem)
    # Strip version / status tokens for grouping
    stem = re.sub(
        r"[_\s-]+(v\d+(?:\.\d+)*)(?:\.\d+)*",
        " ",
        stem,
        flags=re.I,
    )
    for tok in (
        "final", "clean", "updated", "fixed", "revised", "ssot", "aligned",
        "enhanced", "ready", "draft", "copy", "optimized", "minimal",
        "onepage", "no sign", "no-sign", "no_signature", "letterhead",
        "clean_updated", "fundinggated", "zb",
    ):
        stem = re.sub(rf"[_\s-]+{tok}[_\s-]*", " ", stem, flags=re.I)
    stem = re.sub(r"[^a-zA-Z0-9]+", " ", stem).lower().strip()
    # Collapse 777 foundation society → foundation society
    stem = re.sub(r"\b777\b", "", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem or "misc"


def version_score(name: str) -> tuple:
    """Higher = preferred canonical."""
    n = name.lower()
    score = 0
    if re.search(r"v(\d+(?:\.\d+)*)", n):
        vers = re.findall(r"v(\d+(?:\.\d+)*)", n)
        best = max(vers, key=lambda v: tuple(int(x) for x in v.split(".")))
        parts = [int(x) for x in best.split(".")]
        score += parts[0] * 10000 + (parts[1] * 100 if len(parts) > 1 else 0) + (parts[2] if len(parts) > 2 else 0)
    if "final" in n:
        score += 500
    if "ssot" in n or "aligned" in n:
        score += 300
    if "clean_updated" in n or "updated" in n:
        score += 200
    if "clean" in n or "fixed" in n:
        score += 150
    if "ready" in n or "enhanced" in n:
        score += 100
    if "minimal" in n:
        score += 50
    if n.endswith(".pdf") and "docx" not in n:
        score += 10  # slight prefer pdf for filing copies
    if "__dup" in n or n.startswith("ic-"):
        score -= 200
    if re.search(r"\(\d+\)", n) or re.search(r"\s2\.docx", n):
        score -= 100
    if "draft" in n and "final" not in n:
        score -= 80
    return (score, -len(name))


def safe_dir(key: str) -> str:
    s = key[:80].replace("/", "-")
    return s or "misc"


def main() -> None:
    if not ROOT.is_dir():
        raise SystemExit(f"Missing {ROOT}")

    for d in (CANON, ARCH_DUP, ARCH_SUPER):
        d.mkdir(parents=True, exist_ok=True)

    files = [
        p
        for p in ROOT.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.parent == ROOT
    ]

    # Pass 1: exact duplicates by hash
    by_hash: dict[str, list[Path]] = {}
    for p in files:
        by_hash.setdefault(file_hash(p), []).append(p)

    hash_canonical: dict[str, Path] = {}
    dup_moved = 0
    for h, group in by_hash.items():
        group.sort(key=lambda p: version_score(p.name), reverse=True)
        winner = group[0]
        hash_canonical[h] = winner
        for loser in group[1:]:
            dest = ARCH_DUP / loser.name
            if dest.exists():
                dest = ARCH_DUP / f"{h[:8]}__{loser.name}"
            shutil.move(str(loser), str(dest))
            dup_moved += 1

    # Remaining files at root
    remaining = [
        p
        for p in ROOT.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.parent == ROOT
    ]

    # Pass 2: context groups — pick one canonical per key+extension family
    by_ctx: dict[str, list[Path]] = {}
    for p in remaining:
        ext = p.suffix.lower()
        key = f"{context_key(p.name)}|{ext}"
        by_ctx.setdefault(key, []).append(p)

    canon_moved = super_moved = 0
    report_groups = []

    for key, group in by_ctx.items():
        ctx, ext = key.rsplit("|", 1)
        group.sort(key=lambda p: version_score(p.name), reverse=True)
        winner = group[0]
        folder = CANON / safe_dir(ctx)
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / winner.name
        if dest.exists() and dest.resolve() != winner.resolve():
            dest = folder / f"canonical__{winner.name}"
        if winner.parent == ROOT:
            shutil.move(str(winner), str(dest))
            canon_moved += 1

        superseded = []
        for loser in group[1:]:
            if loser.parent != ROOT:
                continue
            d = ARCH_SUPER / safe_dir(ctx) / loser.name
            d.parent.mkdir(parents=True, exist_ok=True)
            if d.exists():
                d = ARCH_SUPER / safe_dir(ctx) / f"old__{loser.name}"
            shutil.move(str(loser), str(d))
            super_moved += 1
            superseded.append(loser.name)

        report_groups.append(
            {
                "context": ctx,
                "ext": ext,
                "canonical": str(dest.relative_to(ROOT)),
                "superseded_count": len(superseded),
                "superseded_sample": superseded[:5],
            }
        )

    # Loose files still at root (misc)
    left = [p.name for p in ROOT.iterdir() if p.is_file() and p.parent == ROOT]
    canon_count = sum(1 for _ in CANON.rglob("*") if _.is_file())

    summary = {
        "started_files": len(files),
        "duplicates_archived": dup_moved,
        "canonical_promoted": canon_moved,
        "superseded_archived": super_moved,
        "canonical_files_now": canon_count,
        "left_at_root": left,
        "groups": len(report_groups),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps({"summary": summary, "groups": report_groups}, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    print(f"Report: {REPORT}")
    print(f"Canonical: {CANON}")
    print(f"Archive: {ARCH}")


if __name__ == "__main__":
    main()
