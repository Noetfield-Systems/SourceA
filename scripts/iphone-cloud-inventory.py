#!/usr/bin/env python3
"""Step 1: inventory iphone Cloud → CSV + starter manifest JSONL (heuristic classify)."""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

CLOUD = Path.home() / "Desktop/iphone Cloud"
OUT_DIR = Path(__file__).resolve().parents[1] / "imports" / "iphone-cloud"

SUBJECT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("noetfield", re.compile(r"noetfield|witnex", re.I)),
    ("777", re.compile(r"777|seven77", re.I)),
    ("trustfield", re.compile(r"trustfield|witness.?bc|witnessai", re.I)),
    ("witness", re.compile(r"witness", re.I)),
    ("virlux", re.compile(r"virlux|primepath", re.I)),
    ("sina_os", re.compile(r"prompt|n8n|agent.?ai|codex|sina.?prompt|dev.?bridge", re.I)),
    ("investor", re.compile(r"investor|board.?bio|founder.?pack|talking.?point", re.I)),
    ("personal", re.compile(r"passport|rental|cibc|resume|career|insurance|void.?cheque", re.I)),
    ("contractor", re.compile(r"contractor|carpenter", re.I)),
    ("lexre", re.compile(r"lexre", re.I)),
]

FIELD_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("legal", re.compile(r"resolution|corporate|charter|application|contract|legal|bylaw", re.I)),
    ("spec", re.compile(r"spec|protocol|routing|governance|architecture|intake", re.I)),
    ("marketing", re.compile(r"deck|one.?pager|linkedin|landing|brief|pitch|posts", re.I)),
    ("finance", re.compile(r"unit.?economics|capital.?gap|void.?cheque|bank|invoice", re.I)),
    ("ops", re.compile(r"checklist|sop|handoff|procurement|pack|kit", re.I)),
    ("prompt", re.compile(r"prompt|n8n", re.I)),
    ("code", re.compile(r"\.(html|tsx|ts|js|css|zip)$", re.I)),
    ("research", re.compile(r"research|competitor|gap.?map", re.I)),
]

FOLDER_SUBJECT = {
    "Sina Business/Noetfield": "noetfield",
    "The 777 Foundation": "777",
    "Next Steps 777": "777",
    "Board 777": "777",
    "Prompt Pack 777": "777",
    "Witness": "witness",
    "Token": "trustfield",
    "lexre": "lexre",
    "Contractor Business": "contractor",
    "Career": "personal",
    "Resume": "personal",
    "RBC": "personal",
    "Codex": "sina_os",
    "Python": "sina_os",
    "Bridge Parallel": "witness",
}


def folder_subject(rel: str) -> str | None:
    for prefix, subj in FOLDER_SUBJECT.items():
        if rel.startswith(prefix):
            return subj
    if rel.startswith("Sina Business"):
        return "noetfield"  # default bucket — refine by filename
    return None


def classify(name: str, rel: str, suffix: str) -> tuple[str, str, str]:
    text = f"{rel}/{name}"
    subj = folder_subject(rel) or "raw"
    for code, pat in SUBJECT_PATTERNS:
        if pat.search(text):
            subj = code
            break

    field = "ops"
    if suffix in {".html", ".tsx", ".ts", ".js", ".css", ".zip"}:
        field = "code"
    else:
        for code, pat in FIELD_PATTERNS:
            if pat.search(text):
                field = code
                break

    tier = "draft"
    if re.search(r"v\d|_v\d|locked", text, re.I):
        tier = "active"
    if "untitled" in rel.lower():
        tier = "raw"
    if re.search(r"\(\d+\)", name):
        tier = "archive"

    return subj, field, tier


def main() -> None:
    if not CLOUD.is_dir():
        raise SystemExit(f"Missing: {CLOUD}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    csv_path = OUT_DIR / f"iphone-cloud-inventory-{ts}.csv"
    manifest_path = OUT_DIR / f"iphone-cloud-manifest-{ts}.jsonl"

    rows: list[dict] = []
    n = 0
    for path in CLOUD.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        rel = str(path.relative_to(CLOUD))
        subj, field, tier = classify(path.name, rel, path.suffix.lower())
        n += 1
        row = {
            "id": f"ic-{n:05d}",
            "source_path": rel,
            "filename": path.name,
            "ext": path.suffix.lower(),
            "size_bytes": path.stat().st_size,
            "subject": subj,
            "field": field,
            "spec_tier": tier,
            "status": "classified",
        }
        rows.append(row)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    with manifest_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Summary by subject/field
    summary: dict[str, int] = {}
    for r in rows:
        key = f"{r['subject']}/{r['field']}"
        summary[key] = summary.get(key, 0) + 1
    top = sorted(summary.items(), key=lambda x: -x[1])[:20]
    print(f"OK: {n} files")
    print(f"CSV: {csv_path}")
    print(f"Manifest: {manifest_path}")
    print("Top subject/field:")
    for k, c in top:
        print(f"  {c:4d}  {k}")


if __name__ == "__main__":
    main()
