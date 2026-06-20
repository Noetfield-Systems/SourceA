#!/usr/bin/env python3
"""Flatten _organized to minimal tree: _organized/{subject}/ only."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

CLOUD = Path.home() / "Desktop" / "iphone Cloud"
ORG = CLOUD / "_organized"
INBOX = CLOUD / "_INBOX"

# Re-classify raw → subject from filename/path hints
RECLASS = [
    ("noetfield", re.compile(r"noetfield|witnex", re.I)),
    ("777", re.compile(r"777|seven77|foundation", re.I)),
    ("trustfield", re.compile(r"trustfield|witness.?bc|witnessai", re.I)),
    ("witness", re.compile(r"witness", re.I)),
    ("virlux", re.compile(r"virlux|primepath", re.I)),
    ("sina_os", re.compile(r"prompt|n8n|agent|codex|sina.?prompt|orchestr", re.I)),
    ("investor", re.compile(r"investor|board.?bio|founder|talking.?point|deck", re.I)),
    ("personal", re.compile(r"passport|rental|cibc|resume|career|insurance|void|cheque|kazemnezhad", re.I)),
    ("contractor", re.compile(r"contractor|carpenter", re.I)),
    ("lexre", re.compile(r"lexre", re.I)),
]


def guess_subject(path: Path, current: str) -> str:
    if current != "raw":
        return current
    text = str(path)
    for subj, pat in RECLASS:
        if pat.search(text):
            return subj
    return "raw"


def safe_flat_name(name: str) -> str:
    return name.strip().replace("\0", "")


def main() -> None:
    if not ORG.is_dir():
        raise SystemExit(f"Missing {ORG}")

    used: dict[str, set[str]] = {}
    moved = errors = 0

    files = sorted(ORG.rglob("*"), key=lambda p: len(str(p)), reverse=True)
    for src in files:
        if not src.is_file() or src.name == ".DS_Store":
            continue
        parts = src.relative_to(ORG).parts
        if len(parts) < 2:
            continue
        subject = parts[0]
        if subject in used and len(parts) == 2:
            continue  # already flat

        subject = guess_subject(src, subject)
        dest_dir = ORG / subject
        if subject == "raw":
            dest_dir = INBOX
        dest_dir.mkdir(parents=True, exist_ok=True)

        base = safe_flat_name(src.name)
        key = subject
        used.setdefault(key, set())
        dest = dest_dir / base
        if dest.name in used[key] or dest.exists():
            stem, suf = Path(base).stem, Path(base).suffix
            dest = dest_dir / f"{stem}__dup{suf}" if suf else dest_dir / f"{stem}__dup"
            n = 2
            while dest.exists():
                dest = dest_dir / f"{stem}__dup{n}{suf}"
                n += 1
        used[key].add(dest.name)

        if src.resolve() == dest.resolve():
            continue
        try:
            shutil.move(str(src), str(dest))
            moved += 1
        except OSError as e:
            errors += 1
            print(f"ERR {src}: {e}")

    # Remove empty nested dirs (bottom-up)
    removed_dirs = 0
    for d in sorted(ORG.rglob("*"), key=lambda p: len(str(p)), reverse=True):
        if d.is_dir() and d != ORG:
            try:
                if not any(d.iterdir()):
                    d.rmdir()
                    removed_dirs += 1
            except OSError:
                pass

    print(f"OK flattened moved={moved} errors={errors} removed_empty_dirs={removed_dirs}")
    print("Structure: _organized/{{subject}}/  (+ _INBOX for remaining raw)")
    for subj in sorted(ORG.iterdir()):
        if subj.is_dir():
            n = sum(1 for _ in subj.rglob("*") if _.is_file())
            print(f"  {n:4d}  {subj.name}/")


if __name__ == "__main__":
    main()
