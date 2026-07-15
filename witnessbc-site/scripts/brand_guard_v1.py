#!/usr/bin/env python3
"""Load WitnessBC third-party brand deny patterns from external policy (not in-repo literals)."""

from __future__ import annotations

import base64
import json
import os
import re
from functools import lru_cache
from pathlib import Path

DEFAULT_POLICY = Path.home() / ".sina" / "sourcea-brand-denylist-v1.json"


def policy_path() -> Path:
    raw = os.environ.get("SOURCEA_BRAND_DENYLIST_PATH", "").strip()
    return Path(raw).expanduser() if raw else DEFAULT_POLICY


@lru_cache(maxsize=1)
def _cfg() -> dict:
    path = policy_path()
    if not path.is_file():
        raise FileNotFoundError(
            f"brand denylist missing: {path} — set SOURCEA_BRAND_DENYLIST_PATH or install Mac policy file"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    parts = [base64.b64decode(p).decode("utf-8") for p in data["deny_patterns_b64"]]
    deny = "|".join(re.escape(p) for p in parts)
    return {
        "forbidden": re.compile(deny, re.I),
        "allow": re.compile(data["allow_regex"], re.I),
        "policy_path": str(path),
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
