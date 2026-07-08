#!/usr/bin/env python3
"""Decide Brain corpus refresh mode — skip / light / full (less dirty tree on publish)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "brain-refresh-gate-receipt-v1.json"

POSITIONING = ROOT / "sites/SourceA-landing/green-unified/data/sourcea-positioning-v1.json"
RULES = ROOT / "data/brain-public-rules-v1.json"
BUNDLE = ROOT / "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json"
LANDING_GLOB_DIRS = (
    ROOT / "sites/SourceA-landing/green-unified",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _file_fingerprint(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def _landing_html_fingerprint() -> str:
    h = hashlib.sha256()
    green = LANDING_GLOB_DIRS[0]
    if not green.is_dir():
        return ""
    for html in sorted(green.rglob("*.html")):
        if "dist" in html.parts or "reference" in html.parts:
            continue
        rel = html.relative_to(green).as_posix()
        h.update(rel.encode())
        h.update(html.read_bytes())
    return h.hexdigest()[:16]


def _bundle_generated_at() -> str:
    if not BUNDLE.is_file():
        return ""
    try:
        return json.loads(BUNDLE.read_text(encoding="utf-8")).get("generated_at") or ""
    except json.JSONDecodeError:
        return ""


def _bundle_one_line() -> str:
    if not BUNDLE.is_file():
        return ""
    try:
        bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    for ch in bundle.get("chunks") or []:
        if ch.get("lane") == "rules" and "one_line" in (ch.get("content") or "").lower():
            for line in (ch.get("content") or "").splitlines():
                if line.strip().lower().startswith("sourcea is"):
                    return line.strip()
    return ""


def decide(*, force: str | None = None) -> dict:
    """Return action: skip | light | full."""
    force = (force or os.environ.get("SOURCEA_PUBLISH_BRAIN_MODE") or "").strip().lower()
    if force in ("skip", "0", "off", "false"):
        return {"action": "skip", "reason": "forced_skip"}
    if force in ("full", "1", "force"):
        return {"action": "full", "reason": "forced_full"}
    if force == "light":
        return {"action": "light", "reason": "forced_light"}

    pos_fp = _file_fingerprint(POSITIONING)
    rules_fp = _file_fingerprint(RULES)
    html_fp = _landing_html_fingerprint()

    state_path = SINA / "brain-refresh-fingerprints-v1.json"
    prev: dict = {}
    if state_path.is_file():
        try:
            prev = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prev = {}

    pos_line = ""
    if POSITIONING.is_file():
        try:
            pos_line = json.loads(POSITIONING.read_text(encoding="utf-8")).get("one_line") or ""
        except json.JSONDecodeError:
            pass

    bundle_line = _bundle_one_line()
    voice_drift = bool(pos_line and bundle_line and pos_line not in bundle_line)

    if not BUNDLE.is_file():
        action, reason = "full", "no_bundle"
    elif html_fp and html_fp != prev.get("html_fp"):
        action, reason = "full", "landing_html_changed"
    elif voice_drift or pos_fp != prev.get("pos_fp") or rules_fp != prev.get("rules_fp"):
        action, reason = "light", "positioning_or_rules_changed"
    else:
        action, reason = "skip", "brain_fresh_enough"

    return {
        "action": action,
        "reason": reason,
        "at": _now(),
        "fingerprints": {
            "pos_fp": pos_fp,
            "rules_fp": rules_fp,
            "html_fp": html_fp,
        },
        "bundle_generated_at": _bundle_generated_at(),
        "voice_drift": voice_drift,
        "positioning_one_line": pos_line[:120],
    }


def save_fingerprints(row: dict) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    path = SINA / "brain-refresh-fingerprints-v1.json"
    path.write_text(json.dumps({"at": _now(), **row.get("fingerprints", {})}, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", choices=["skip", "light", "full"])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", action="store_true", help="Persist fingerprints after successful refresh")
    args = ap.parse_args()

    row = decide(force=args.force)
    if args.save and row.get("fingerprints"):
        save_fingerprints(row)

    RECEIPT.write_text(json.dumps({"schema": "brain-refresh-gate-v1", **row}, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"{row['action']}: {row['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
