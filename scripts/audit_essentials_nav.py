#!/usr/bin/env python3
"""Fail build if app.js NAV ids diverge from hub_essentials_index NAV_TABS.

Worker Hub mode (command_retired_forever): validate essentials index coverage instead of app.js.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
APP_JS = SOURCE_A / "agent-control-panel" / "assets" / "app.js"
sys.path.insert(0, str(SOURCE_A / "scripts"))

from hub_essentials_index import NAV_TABS, hub_essentials_payload  # noqa: E402
from hub_worker_mode_v1 import worker_hub_mode  # noqa: E402


def _nav_ids_from_app_js() -> list[str]:
    text = APP_JS.read_text(encoding="utf-8", errors="replace")
    block = re.search(r"const NAV = \[(.*?)\n  \];", text, re.DOTALL)
    if not block:
        raise RuntimeError("NAV block not found in app.js")
    raw = re.findall(r'\{\s*id:\s*"([^"]+)"', block.group(1))
    return list(dict.fromkeys(raw))


def _audit_worker_hub() -> tuple[bool, list[str]]:
    errors: list[str] = []
    payload = hub_essentials_payload()
    cov = payload.get("nav_coverage") or {}
    missing = list(cov.get("missing_nav_tabs") or [])
    missing_extra = list(cov.get("missing_extra_tabs") or [])
    if missing:
        errors.append(f"NAV_TABS not indexed in essentials: {missing}")
    if missing_extra:
        errors.append(f"EXTRA_TABS not indexed in essentials: {missing_extra}")
    return not errors, errors


def main() -> int:
    errors: list[str] = []

    if worker_hub_mode():
        ok, wh_errors = _audit_worker_hub()
        if not ok:
            errors.extend(wh_errors)
        if errors:
            print("ESSENTIALS NAV SYNC FAILED (worker-hub):")
            for e in errors:
                print(f"  - {e}")
            return 1
        print(f"OK: NAV sync (worker-hub) · {len(NAV_TABS)} sidebar tabs indexed in essentials")
        return 0

    if not APP_JS.is_file():
        errors.append(f"missing app.js and not worker-hub mode: {APP_JS}")
        print("ESSENTIALS NAV SYNC FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    app_ids = _nav_ids_from_app_js()
    app_set = set(app_ids)
    tabs_set = set(NAV_TABS)
    if app_set != tabs_set:
        missing_in_app = sorted(tabs_set - app_set)
        extra_in_app = sorted(app_set - tabs_set)
        if missing_in_app:
            errors.append(f"NAV_TABS not in app.js NAV: {missing_in_app}")
        if extra_in_app:
            errors.append(f"app.js NAV ids not in NAV_TABS: {extra_in_app}")
    if errors:
        print("ESSENTIALS NAV SYNC FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: NAV sync · {len(NAV_TABS)} sidebar tabs match app.js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
