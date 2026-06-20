#!/usr/bin/env python3
"""Pass 2: merge _CANONICAL subfolders into topic buckets; cap files per topic."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path.home() / "Desktop/iphone Cloud/_organized/777"
CANON = ROOT / "_CANONICAL"
TOPICS = ROOT / "_TOPICS"
ARCH = ROOT / "_archive" / "merged_into_topics"

TOPIC_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("01-bylaws-governance", re.compile(r"bylaw|governance|resolution|board.?member|schedule.?b|advocacy|nonpartisan|society.?bylaw", re.I)),
    ("02-budget-finance", re.compile(r"budget|bva|funding|zerobased|startup.?budget|financial|cashflow|summary.?1pager|implementation.?plan", re.I)),
    ("03-bank-board-packs", re.compile(r"bank|board.?pack|cover.?letter|due.?diligence|funder.?script|diligence", re.I)),
    ("04-playbook-operations", re.compile(r"playbook|ssot|hybrid|operating.?framework|roadmap|master.?playbook", re.I)),
    ("05-policies-compliance", re.compile(r"policy|compliance|audit|hooks", re.I)),
    ("06-newcomers-program", re.compile(r"newcomer|compass|prospectus|workshop", re.I)),
    ("07-fundraising-decks", re.compile(r"deck|donor|talking|sponsor|fundraising|pitch|grant", re.I)),
    ("08-zip-packs", re.compile(r"pack\.zip$|_pack\.zip$|\.zip$", re.I)),
    ("09-web-site", re.compile(r"\.html$|index|landing|wireframe|site|\.css$|\.js$", re.I)),
    ("10-templates-data", re.compile(r"template|readme|checklist|\.csv$|\.txt$|\.xml$|mapping", re.I)),
    ("11-witness-legal-misc", re.compile(r"witness|ed.?ad|volunteer|form.?0079|package", re.I)),
    ("99-misc", re.compile(r".", re.I)),
]

# Max files to keep active per topic (rest → archive)
TOPIC_CAPS = {
    "01-bylaws-governance": 5,
    "02-budget-finance": 12,
    "03-bank-board-packs": 10,
    "04-playbook-operations": 8,
    "05-policies-compliance": 15,
    "06-newcomers-program": 10,
    "07-fundraising-decks": 12,
    "08-zip-packs": 8,
    "09-web-site": 15,
    "10-templates-data": 20,
    "11-witness-legal-misc": 10,
    "99-misc": 25,
}


def version_score(name: str) -> tuple:
    n = name.lower()
    score = 0
    if m := re.findall(r"v(\d+(?:\.\d+)*)", n):
        best = max(m, key=lambda v: tuple(int(x) for x in v.split(".")))
        parts = [int(x) for x in best.split(".")]
        score += parts[0] * 10000 + (parts[1] * 100 if len(parts) > 1 else 0) + (parts[2] if len(parts) > 2 else 0)
    for w, pts in (
        ("final", 500), ("ssot", 300), ("updated", 200), ("clean", 150), ("ready", 100),
    ):
        if w in n:
            score += pts
    if "__dup" in n or n.startswith("ic-"):
        score -= 200
    return (score, -len(name))


def topic_for(text: str) -> str:
    for tid, pat in TOPIC_RULES:
        if pat.search(text):
            return tid
    return "99-misc"


def stem_key(name: str) -> str:
    s = Path(name).stem.lower()
    s = re.sub(r"^ic-\d+__", "", s)
    s = re.sub(r"__dup\d*$", "", s)
    s = re.sub(r"v\d+(?:\.\d+)*", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s[:60]


def main() -> None:
    TOPICS.mkdir(parents=True, exist_ok=True)
    ARCH.mkdir(parents=True, exist_ok=True)

    # Collect all files from _CANONICAL tree
    all_files: list[Path] = []
    if CANON.is_dir():
        all_files = [p for p in CANON.rglob("*") if p.is_file() and not p.name.startswith(".")]

    by_topic: dict[str, list[Path]] = {}
    for p in all_files:
        ctx = p.parent.name if p.parent != CANON else ""
        tid = topic_for(f"{ctx} {p.name}")
        by_topic.setdefault(tid, []).append(p)

    kept = archived = 0
    for tid, files in sorted(by_topic.items()):
        dest_dir = TOPICS / tid
        dest_dir.mkdir(parents=True, exist_ok=True)
        cap = TOPIC_CAPS.get(tid, 20)

        # Dedupe by stem+ext within topic
        buckets: dict[str, list[Path]] = {}
        for p in files:
            bk = f"{stem_key(p.name)}|{p.suffix.lower()}"
            buckets.setdefault(bk, []).append(p)

        winners: list[Path] = []
        losers: list[Path] = []
        for group in buckets.values():
            group.sort(key=lambda p: version_score(p.name), reverse=True)
            winners.append(group[0])
            losers.extend(group[1:])

        winners.sort(key=lambda p: version_score(p.name), reverse=True)
        active = winners[:cap]
        extra = winners[cap:] + losers

        for p in active:
            out = dest_dir / p.name
            if out.exists():
                out = dest_dir / f"{stem_key(p.name)[:40]}__{p.name}"
            shutil.move(str(p), str(out))
            kept += 1

        for p in extra:
            out = ARCH / tid / p.name
            out.parent.mkdir(parents=True, exist_ok=True)
            if out.exists():
                out = ARCH / tid / f"extra__{p.name}"
            if p.exists():
                shutil.move(str(p), str(out))
                archived += 1

    # Remove empty _CANONICAL dirs
    if CANON.is_dir():
        for d in sorted(CANON.rglob("*"), key=lambda x: len(str(x)), reverse=True):
            if d.is_dir():
                try:
                    d.rmdir()
                except OSError:
                    pass
        try:
            CANON.rmdir()
        except OSError:
            pass

    topic_counts = {d.name: sum(1 for _ in d.iterdir() if _.is_file()) for d in TOPICS.iterdir() if d.is_dir()}
    total_active = sum(topic_counts.values())
    print(f"OK active={total_active} archived_pass2={archived}")
    for k, v in sorted(topic_counts.items()):
        print(f"  {v:3d}  {k}")


if __name__ == "__main__":
    main()
