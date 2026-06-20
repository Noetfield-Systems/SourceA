#!/usr/bin/env python3
"""Batch add/fix **Saved:** YYYY-MM-DDTHH:MM:SSZ headers on markdown docs.

Law: docs/SOURCEA_DOC_DATETIME_MANDATORY_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SAVED_OK = re.compile(
    r"(?:\*\*Saved:\*\*|\*\*saved_at:\*\*|saved_at:)\s*\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
    re.I,
)
DATE_ONLY = re.compile(
    r"(\*\*Saved:\*\*|\*\*saved_at:\*\*|saved_at:)\s*(\d{4}-\d{2}-\d{2})(?!T)",
    re.I,
)
RETROFIT_NOTE = "doc-datetime-law batch retrofit"
ARCHIVE_DATE = re.compile(r"/attachments/(\d{4}-\d{2}-\d{2})/")
RESEARCH_DATE = re.compile(r"/by_date/(\d{4}-\d{2}-\d{2})/")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _head(text: str, n: int = 12) -> str:
    return "\n".join(text.splitlines()[:n])


def needs_fix(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    head = _head(text)
    if SAVED_OK.search(head):
        return None
    if DATE_ONLY.search(head):
        return "date_only"
    return "missing"


def archive_saved_time(path: Path, *, batch_at: str) -> str:
    """Prefer attachment folder date; else file mtime UTC; else batch_at."""
    m = ARCHIVE_DATE.search(path.as_posix())
    if m:
        return f"{m.group(1)}T12:00:00Z"
    try:
        ts = path.stat().st_mtime
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError:
        return batch_at


def research_saved_time(path: Path, *, batch_at: str) -> str:
    """Prefer RESEARCH/by_date/YYYY-MM-DD/ folder date; else file mtime UTC."""
    m = RESEARCH_DATE.search(path.as_posix())
    if m:
        return f"{m.group(1)}T12:00:00Z"
    # Filename prefix YYYY-MM-DD_
    name = path.name
    if len(name) >= 11 and name[4] == "-" and name[7] == "-" and name[10] in ("_", "-"):
        try:
            datetime.strptime(name[:10], "%Y-%m-%d")
            return f"{name[:10]}T12:00:00Z"
        except ValueError:
            pass
    try:
        ts = path.stat().st_mtime
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError:
        return batch_at


def fix_content(text: str, *, batch_at: str, saved_at: str | None = None) -> tuple[str, bool]:
    head_lines = text.splitlines()[:12]
    head = "\n".join(head_lines)
    if SAVED_OK.search(head):
        return text, False

    m = DATE_ONLY.search(text)
    if m:
        # Preserve calendar date, add noon UTC as neutral retrofit time
        date = m.group(2)
        new_saved = f"**Saved:** {date}T12:00:00Z · **Retrofit:** {RETROFIT_NOTE} @ {batch_at}"
        new_text = DATE_ONLY.sub(new_saved, text, count=1)
        return new_text, True

    lines = text.splitlines()
    stamp = saved_at or batch_at
    saved_line = f"**Saved:** {stamp} · **Retrofit:** {RETROFIT_NOTE}"

    # Insert after first heading line if present
    insert_at = 0
    for i, line in enumerate(lines[:8]):
        if line.startswith("#"):
            insert_at = i + 1
            break

    # Skip blank line after title if we're inserting metadata
    if insert_at < len(lines) and lines[insert_at].strip() == "":
        lines.insert(insert_at + 1, saved_line)
    else:
        lines.insert(insert_at, "")
        lines.insert(insert_at + 1, saved_line)

    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), True


def collect_tier1_docs() -> list[Path]:
    docs = ROOT / "docs"
    paths: list[Path] = []
    if docs.is_dir():
        for p in sorted(docs.rglob("*.md")):
            if needs_fix(p):
                paths.append(p)
    return paths


def collect_locked() -> list[Path]:
    paths: list[Path] = []
    for p in sorted(ROOT.glob("*_LOCKED*.md")):
        if needs_fix(p):
            paths.append(p)
    bo = ROOT / "brain-os"
    if bo.is_dir():
        for p in sorted(bo.rglob("*LOCKED*.md")):
            if needs_fix(p):
                paths.append(p)
    return paths


def collect_archive() -> list[Path]:
    paths: list[Path] = []
    archive = ROOT / "archive"
    if not archive.is_dir():
        return paths
    for p in sorted(archive.rglob("*.md")):
        if needs_fix(p):
            paths.append(p)
    return paths


def collect_research() -> list[Path]:
    paths: list[Path] = []
    research = ROOT / "RESEARCH"
    if not research.is_dir():
        return paths
    for p in sorted(research.rglob("*.md")):
        if needs_fix(p):
            paths.append(p)
    return paths


def run(
    paths: list[Path],
    *,
    dry_run: bool = False,
    archive_mode: bool = False,
    research_mode: bool = False,
) -> dict:
    batch_at = _now()
    fixed: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []
    for p in paths:
        reason = needs_fix(p)
        if not reason:
            skipped.append(str(p))
            continue
        try:
            text = p.read_text(encoding="utf-8")
            if archive_mode:
                saved_at = archive_saved_time(p, batch_at=batch_at)
            elif research_mode:
                saved_at = research_saved_time(p, batch_at=batch_at)
            else:
                saved_at = None
            new_text, changed = fix_content(text, batch_at=batch_at, saved_at=saved_at)
            if changed and not dry_run:
                p.write_text(new_text, encoding="utf-8")
            if changed:
                fixed.append(str(p))
        except OSError as e:
            errors.append(f"{p}: {e}")
    return {
        "batch_at": batch_at,
        "fixed_count": len(fixed),
        "skipped_count": len(skipped),
        "error_count": len(errors),
        "fixed": fixed,
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch fix doc Saved datetime headers")
    ap.add_argument("--tier1-docs", action="store_true", help="Fix all docs/ needing header")
    ap.add_argument("--locked", action="store_true", help="Fix root + brain-os LOCKED md")
    ap.add_argument("--archive", action="store_true", help="Fix archive/**/*.md")
    ap.add_argument("--research", action="store_true", help="Fix RESEARCH/**/*.md")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    paths: list[Path] = []
    if args.tier1_docs:
        paths.extend(collect_tier1_docs())
    if args.locked:
        paths.extend(collect_locked())
    if args.archive:
        paths.extend(collect_archive())
    if args.research:
        paths.extend(collect_research())
    if not paths:
        ap.error("Specify --tier1-docs, --locked, --archive, and/or --research")

    # dedupe
    seen: set[str] = set()
    uniq: list[Path] = []
    for p in paths:
        s = str(p.resolve())
        if s not in seen:
            seen.add(s)
            uniq.append(p)

    result = run(
        uniq,
        dry_run=args.dry_run,
        archive_mode=args.archive,
        research_mode=args.research,
    )
    if args.json:
        import json

        print(json.dumps(result, indent=2))
    else:
        print(f"batch_at={result['batch_at']} fixed={result['fixed_count']} errors={result['error_count']}")
        for f in result["fixed"][:20]:
            print(f"FIXED: {f}")
        if result["fixed_count"] > 20:
            print(f"... +{result['fixed_count']-20} more")
    return 0 if result["error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
