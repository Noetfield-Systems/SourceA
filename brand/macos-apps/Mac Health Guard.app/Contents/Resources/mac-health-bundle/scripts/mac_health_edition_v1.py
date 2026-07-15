#!/usr/bin/env python3
"""Mac Health Guard — edition/paths SSOT.

Every other mac_health_*.py module imports SINA (the data directory) and the
edition flags from here instead of hardcoding a path. Two editions, chosen
automatically at runtime with no config file required:

- "commercial" (default): the product a stranger downloads and runs. Zero
  coupling to this maintainer's personal SourceA/Mac Law automation. Data
  lives in the standard macOS per-app location,
  ~/Library/Application Support/Mac Health Guard.
- "personal": this maintainer's own machine. Opts in automatically whenever
  SINA_SOURCEA is set (every launchd job and script in this repo already
  sets it) or MAC_HEALTH_EDITION=personal is set explicitly. Data stays at
  ~/.sina so nothing already logged moves or breaks.

Modules that are personal-only (cloud glance, agent mandates, founder
session gate, W2 plan probes, etc.) should check IS_PERSONAL before wiring
themselves into the commercial request/response path.
"""
from __future__ import annotations

import os
from pathlib import Path

BRAND_NAME = "Mac Health Guard"
BUNDLE_ID = "com.sina.machealth.standalone"


def _detect_edition() -> str:
    explicit = os.environ.get("MAC_HEALTH_EDITION", "").strip().lower()
    if explicit in ("commercial", "personal"):
        return explicit
    if os.environ.get("SINA_SOURCEA", "").strip():
        return "personal"
    return "commercial"


EDITION = _detect_edition()
IS_PERSONAL = EDITION == "personal"
IS_COMMERCIAL = not IS_PERSONAL

SINA = (
    (Path.home() / ".sina")
    if IS_PERSONAL
    else (Path.home() / "Library" / "Application Support" / BRAND_NAME)
)
