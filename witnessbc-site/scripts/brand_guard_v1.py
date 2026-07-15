#!/usr/bin/env python3
"""Load WitnessBC third-party brand deny patterns without embedding names in callers."""

from __future__ import annotations

import base64
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DENYLIST = ROOT / "data" / "brand-denylist-v1.json"


@lru_cache(maxsize=1)
def _cfg() -> dict:
    data = json.loads(DENYLIST.read_text(encoding="utf-8"))
    parts = [base64.b64decode(p).decode("utf-8") for p in data["deny_patterns_b64"]]
    deny = "|".join(re.escape(p) for p in parts)
    return {
        "forbidden": re.compile(deny, re.I),
        "allow": re.compile(data["allow_regex"], re.I),
    }


def line_is_forbidden(line: str) -> bool:
    cfg = _cfg()
    if not cfg["forbidden"].search(line):
        return False
    return not cfg["allow"].search(line)


def text_has_forbidden(text: str) -> bool:
    return any(line_is_forbidden(line) for line in text.splitlines())


def forbidden_in_ref_html(cite_html: str, url: str) -> bool:
    return text_has_forbidden(f"{cite_html} {url}")
