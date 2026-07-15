#!/usr/bin/env python3
"""Apply customer-facing copy normalize across green-unified HTML/CSS."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "sites" / "SourceA-landing" / "green-unified"

# Order matters — longer phrases first.
REPLACEMENTS = [
    ("Powered by SourceA", "Powered by SourceA"),
    ("Verification (screen-share)", "Verification (screen-share)"),
    ("How verification works", "How verification works"),
    ("How verification works", "How verification works"),
    ("verification demo", "verification demo"),
    ("Verification demo", "Verification demo"),
    ("Verification · replay", "Verification · replay"),
    ("the live demo", "the live demo"),
    ("Verification +", "Verification +"),
    ("Controlled execution", "Controlled execution"),
    ("Verification →", "Verification →"),
    (">Verification</a>", "Verification</a>"),
    (">Verification</span>", "Verification</span>"),
    (">>Verification<", ">Verification<"),
    ("/proof\">Verification", "/proof\">Verification"),
    ("System status", "System status"),
    ("Logged and reviewable", "Logged and reviewable"),
    ("Delivery records", "Delivery records"),
    ("PASS or BLOCK logged", "clear pass or fail checks"),
    ("passes logged", "logged every send"),
    ("Logged and signed", "Logged and signed"),
    ("replay logged", "replay anytime"),
    ("Receipts logged", "Records saved"),
    ("logged every run", "logged every run"),
    ("See live receipt", "See live demo"),
    ("live receipt", "live demo"),
    ("shareable receipt", "delivery summary"),
    ("Shareable client receipt", "Shareable delivery summary"),
    ("Delivery receipt", "Delivery summary"),
    ("controlled execution", "verified delivery"),
    ("agent work desk", "agent work desk"),
    ("delivery desk", "delivery desk"),
    ("factory workflows", "factory workflows"),
    ("platform seats", "platform seats"),
    ("controlled sends", "tracked sends"),
    ("production-ready", "production-ready"),
    ("tracked outreach", "tracked outreach"),
    ("sandbox workflows", "sandbox workflows"),
    ("scoped loop", "scoped build"),
    ("specialist team", "specialist team"),
    ("controlled console", "operations console"),
    ("controlled specialist", "specialist"),
    ("ops monitor", "ops monitor"),
    ("Controlled sends", "Tracked sends"),
    ("verification built in", "verification built in"),
    ("in the repository ·", "logged ·"),
    (" land logged", " are saved"),
    ("sealed logged", "saved securely"),
]

CSS_REPLACEMENTS = [
    ("Agent Run shell + light/dark layout themes sections", "Agent Run shell + marketing sections"),
    ("Pillar chips (SourceA)", "Pillar chips"),
    ("Verification + compare", "Verification + compare"),
    ("Verification beat cards", "Verification step cards"),
    ("Verification verdict row", "Verification verdict row"),
]

SKIP_SUBSTRINGS = (
    "investors.html",  # investor-facing; controlled execution OK in thesis
)

TECHNICAL_KEEP = re.compile(
    r"receipt_id|BOOT_REPORT|governance-dispatch-receipt|cross-lane-edit-guard|schema"
)


def _should_skip(path: Path) -> bool:
    s = str(path)
    return any(x in s for x in SKIP_SUBSTRINGS)


def _apply(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def main() -> int:
    changed = 0
    for path in sorted(GREEN.rglob("*")):
        if "dist" in path.parts or path.name.startswith("."):
            continue
        if _should_skip(path):
            continue
        if path.suffix in (".html", ".js") or path.name == "README.md":
            raw = path.read_text(encoding="utf-8", errors="replace")
            new = _apply(raw, REPLACEMENTS)
            if new != raw:
                path.write_text(new, encoding="utf-8")
                changed += 1
        elif path.name in ("sourcea.css", "green-unified.css") or (
            path.suffix == ".css" and "sourcea" in path.name
        ):
            raw = path.read_text(encoding="utf-8", errors="replace")
            new = _apply(raw, CSS_REPLACEMENTS)
            if new != raw:
                path.write_text(new, encoding="utf-8")
                changed += 1

    trust_json = GREEN / "data" / "trust-signals-public-v1.json"
    if trust_json.is_file():
        raw = trust_json.read_text(encoding="utf-8")
        new = raw.replace(
            "Powered by SourceA",
            "Powered by SourceA",
        )
        if new != raw:
            trust_json.write_text(new, encoding="utf-8")
            changed += 1

    print(f"dejargon_green_unified_public_copy_v1 OK — {changed} files updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
