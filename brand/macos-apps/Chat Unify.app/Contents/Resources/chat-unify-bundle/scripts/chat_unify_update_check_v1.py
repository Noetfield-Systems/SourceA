#!/usr/bin/env python3
"""Chat Unify — in-app update check (installed app vs published .dmg)."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REMOTE_MANIFEST = "https://sourcea.app/downloads/chat-unify-mac-v1.json"
DEFAULT_DMG = "https://sourcea.app/downloads/chat-unify-mac-v1.dmg"


def _repo_root() -> Path:
    import os

    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for candidate in (
        Path.home() / "Desktop" / "SourceA",
        Path(__file__).resolve().parents[1],
    ):
        if (candidate / "data" / "chat-unify-platform-catalog-v1.json").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


def _parse_version(raw: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", str(raw or "0"))
    if not parts:
        return (0,)
    return tuple(int(p) for p in parts[:4])


def version_lt(left: str, right: str) -> bool:
    return _parse_version(left) < _parse_version(right)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _fetch_remote_manifest() -> dict[str, Any] | None:
    try:
        req = urllib.request.Request(
            REMOTE_MANIFEST,
            headers={"User-Agent": "ChatUnify-UpdateCheck/1"},
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (OSError, json.JSONDecodeError, urllib.error.URLError, ValueError):
        return None


def update_check_payload(*, current_version: str) -> dict[str, Any]:
    root = _repo_root()
    download_url = DEFAULT_DMG
    sha256 = ""
    sources: list[tuple[str, str, str, str]] = []  # version, url, sha, label
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    remote = _fetch_remote_manifest()
    if remote and remote.get("version"):
        sources.append(
            (
                str(remote["version"]),
                str(remote.get("public_url") or DEFAULT_DMG),
                str(remote.get("sha256") or ""),
                "sourcea.app",
            )
        )

    for path in (
        Path.home() / ".sina" / "chat-unify-dmg-publish-receipt-v1.json",
        root / "sites" / "SourceA-landing" / "green-unified" / "downloads" / "chat-unify-mac-v1.json",
        root / "SourceA-landing" / "green-unified" / "downloads" / "chat-unify-mac-v1.json",
    ):
        row = _read_json(path)
        if row and row.get("version"):
            sources.append(
                (
                    str(row["version"]),
                    str(row.get("public_url") or DEFAULT_DMG),
                    str(row.get("sha256") or ""),
                    f"disk:{path.name}",
                )
            )

    if not sources:
        sources.append((current_version, DEFAULT_DMG, "", "bundled"))

    latest_row = max(sources, key=lambda row: _parse_version(row[0]))
    latest_version, download_url, sha256, source = latest_row
    update_available = version_lt(current_version, latest_version)
    if update_available:
        founder_line = (
            f"Update available — you're on v{current_version}, "
            f"latest is v{latest_version}. Download the new .dmg and replace the app."
        )
    else:
        founder_line = f"You're on the latest version (v{current_version})."

    return {
        "ok": True,
        "schema": "chat-unify-update-check-v1",
        "checked_at": checked_at,
        "current_version": current_version,
        "latest_version": latest_version,
        "update_available": update_available,
        "download_url": download_url,
        "sha256": sha256 or None,
        "source": source,
        "founder_line": founder_line,
    }
