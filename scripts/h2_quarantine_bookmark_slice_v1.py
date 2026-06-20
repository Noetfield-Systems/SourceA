#!/usr/bin/env python3
"""H2 quarantine bookmark slice — legacy retired; H2 must not link /legacy/ (sa-0825)."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from typing import Any

SLICE_SCHEMA = "h2-quarantine-bookmark-slice-v1"
LEGACY_CANONICAL = "/legacy/"
RETIRE_LAW = "ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md"


def _fetch_legacy_status(*, base: str = "http://127.0.0.1:13020") -> dict[str, Any]:
    url = base.rstrip("/") + LEGACY_CANONICAL
    req = urllib.request.Request(url, method="GET")

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
            return None

    opener = urllib.request.build_opener(_NoRedirect, urllib.request.HTTPHandler)
    try:
        with opener.open(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            code = resp.getcode()
    except urllib.error.HTTPError as exc:
        code = exc.code
        loc = exc.headers.get("Location", "")
        if code in (301, 302, 303, 307, 308):
            return {
                "ok": True,
                "url": url,
                "http_status": code,
                "retired": True,
                "redirect_to": loc or "/",
                "has_readonly_banner": False,
                "mentions_read_only": False,
            }
        return {"ok": False, "url": url, "http_status": code, "error": str(exc)}
    except (OSError, urllib.error.URLError) as exc:
        return {"ok": False, "url": url, "error": str(exc)}

    banner_m = re.search(
        r'id="museum-readonly-banner"[^>]*>(.*?)</div>',
        html,
        re.S | re.I,
    )
    banner = re.sub(r"\s+", " ", banner_m.group(1)).strip() if banner_m else ""
    low = banner.lower()
    return {
        "ok": code == 200,
        "url": url,
        "http_status": code,
        "retired": False,
        "banner_text": banner[:280],
        "has_readonly_banner": bool(banner_m),
        "mentions_read_only": "read only" in low,
        "mentions_archive": "archive" in low or "museum" in low,
        "links_h1": 'href="/"' in banner or "super fast hub" in low,
    }


def _h2_banner_museum_href(html: str) -> str:
    m = re.search(
        r'Museum\s*→\s*<a[^>]+href="([^"]+)"',
        html,
        re.I,
    )
    return m.group(1) if m else ""


def quarantine_bookmark_slice_payload(*, base: str = "http://127.0.0.1:13020") -> dict[str, Any]:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    machines_html = (root / "agent-control-panel" / "machines" / "index.html").read_text(
        encoding="utf-8"
    )
    legacy = _fetch_legacy_status(base=base)
    museum_href = _h2_banner_museum_href(machines_html)

    museum_absent = not museum_href
    legacy_retired = bool(legacy.get("retired"))
    legacy_quarantined = legacy_retired or bool(
        legacy.get("has_readonly_banner") and legacy.get("mentions_read_only")
    )
    cross_ok = museum_absent and legacy_quarantined and legacy.get("ok")

    if cross_ok and legacy_retired:
        display_line = "Command retired · /legacy/ redirects to H1 · no legacy link on daily H2"
    elif cross_ok:
        display_line = "Archive quarantined · no legacy link on daily H1/H2 · READ ONLY banner live"
    else:
        parts = []
        if not museum_absent:
            parts.append(f"H2 still links legacy {museum_href!r} — remove from daily banner")
        if not legacy_quarantined:
            parts.append("/legacy/ still serves monolith — must redirect or 410")
        display_line = "Misaligned: " + "; ".join(parts or ["unknown"])

    return {
        "ok": True,
        "schema": SLICE_SCHEMA,
        "hub": "H2",
        "slice": "quarantine_bookmark",
        "legacy_url": LEGACY_CANONICAL,
        "legacy_retired": legacy_retired,
        "h2_museum_href": museum_href,
        "h2_is_daily_bookmark": False,
        "h1_daily_bookmark": "/",
        "legacy_banner": legacy,
        "cross_check_ok": cross_ok,
        "display_line": display_line,
        "law": RETIRE_LAW,
    }
