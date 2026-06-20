#!/usr/bin/env python3
"""Move iphone Cloud files into _organized/{subject}/{field}/{spec_tier}/ per manifest."""
from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

CLOUD = Path.home() / "Desktop/iphone Cloud"
ORG = CLOUD / "_organized"
IMPORTS = Path(__file__).resolve().parents[1] / "imports" / "iphone-cloud"
SKIP_NAMES = {".DS_Store", ".localized"}
SKIP_PREFIXES = ("_organized/", "_INBOX/",)


def latest_manifest() -> Path:
    manifests = sorted(IMPORTS.glob("iphone-cloud-manifest-*.jsonl"))
    if not manifests:
        raise SystemExit(f"No manifest in {IMPORTS} — run iphone-cloud-inventory.py first")
    return manifests[-1]


def safe_name(name: str, max_len: int = 180) -> str:
    name = name.strip().replace("\0", "")
    if len(name) <= max_len:
        return name
    stem = Path(name).stem[:120]
    suf = Path(name).suffix
    return stem + suf


def dest_path(row: dict, used: dict[str, int]) -> Path:
    subj = row["subject"]
    field = row["field"]
    tier = row["spec_tier"]
    base = safe_name(row["filename"])
    key = f"{subj}/{field}/{tier}/{base}"
    if key in used:
        used[key] += 1
        stem, suf = Path(base).stem, Path(base).suffix
        base = f"{row['id']}__{stem}{suf}"
    else:
        used[key] = 1
    return ORG / subj / field / tier / base


def main() -> None:
    manifest = latest_manifest()
    ORG.mkdir(parents=True, exist_ok=True)
    (CLOUD / "_INBOX").mkdir(exist_ok=True)

    used: dict[str, int] = {}
    moved = skipped = missing = errors = 0
    log: list[str] = []

    with manifest.open(encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]

    for row in rows:
        rel = row["source_path"]
        if any(rel.startswith(p) for p in SKIP_PREFIXES):
            skipped += 1
            continue
        if Path(rel).name in SKIP_NAMES:
            skipped += 1
            continue

        src = CLOUD / rel
        if not src.is_file():
            missing += 1
            continue

        dst = dest_path(row, used)
        dst.parent.mkdir(parents=True, exist_ok=True)

        if src.resolve() == dst.resolve():
            skipped += 1
            continue

        if dst.exists():
            dst = dst.parent / f"{row['id']}__{dst.name}"

        try:
            shutil.move(str(src), str(dst))
            moved += 1
        except OSError as e:
            errors += 1
            log.append(f"ERR {rel}: {e}")

    # Move stragglers: anything left under CLOUD not in _organized/_INBOX
    for path in list(CLOUD.rglob("*")):
        if not path.is_file() or path.name in SKIP_NAMES:
            continue
        rel = str(path.relative_to(CLOUD))
        if rel.startswith("_organized/") or rel.startswith("_INBOX/"):
            continue
        inbox_dst = CLOUD / "_INBOX" / safe_name(path.name)
        if inbox_dst.exists():
            inbox_dst = CLOUD / "_INBOX" / f"leftover__{path.name}"
        try:
            inbox_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(inbox_dst))
            moved += 1
            log.append(f"INBOX {rel}")
        except OSError as e:
            errors += 1
            log.append(f"INBOX ERR {rel}: {e}")

    report = IMPORTS / "iphone-cloud-move-report.txt"
    report.write_text(
        "\n".join(
            [
                f"manifest: {manifest.name}",
                f"moved: {moved}",
                f"skipped: {skipped}",
                f"missing: {missing}",
                f"errors: {errors}",
                "",
                *log[:500],
            ]
        ),
        encoding="utf-8",
    )
    print(f"OK moved={moved} skipped={skipped} missing={missing} errors={errors}")
    print(f"Report: {report}")
    print(f"Organized root: {ORG}")


if __name__ == "__main__":
    main()
