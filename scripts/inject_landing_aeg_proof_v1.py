#!/usr/bin/env python3
"""Inject latest AEG forensic proof into landing — buyer-facing aeg-live.json."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "SourceA-landing" / "green-unified"
DATA = LANDING / "data"
SINA = Path.home() / ".sina"
AEG_LATEST = SINA / "aeg-latest-receipt-v1.json"
RECEIPT = SINA / "sourcea-aeg-live-inject-v1.json"
PUBLIC_URLS = SINA / "sourcea-public-urls-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _sanitize_terminal(text: str) -> str:
    home = str(Path.home())
    text = text.replace(home, "~")
    text = re.sub(r"/Users/[^/\s]+", "~", text)
    return text.strip()


def _checks_from_boot() -> list[dict]:
    boot = _read_json(DATA / "boot-proof.json")
    return boot.get("checks") or []


def build_aeg_live() -> dict:
    latest = _read_json(AEG_LATEST)
    bundle_dir = Path(str(latest.get("bundle_dir") or ""))
    terminal = ""
    term_path = bundle_dir / "terminal.txt"
    if term_path.is_file():
        terminal = _sanitize_terminal(term_path.read_text(encoding="utf-8", errors="replace"))
    elif latest.get("terminal", {}).get("path"):
        tp = Path(str(latest["terminal"]["path"]))
        if tp.is_file():
            terminal = _sanitize_terminal(tp.read_text(encoding="utf-8", errors="replace"))

    critic = _read_json(SINA / "critic-boot-v1.json")
    boot = _read_json(DATA / "boot-proof.json")
    pub = _read_json(PUBLIC_URLS)
    base = str(pub.get("base_url") or "http://127.0.0.1:5180").rstrip("/")
    site_proof = f"{base}/sourcea/proof/live.html"

    verdict = latest.get("verdict") or critic.get("verdict") or "UNKNOWN"
    blockers = latest.get("blockers") or critic.get("blockers") or []
    checks = _checks_from_boot() or critic.get("checks") or []
    if boot.get("ok") and boot.get("verdict") == "PASS":
        verdict = "PASS"
        blockers = []
        checks = boot.get("checks") or checks

    return {
        "schema": "sourcea-aeg-live-v1",
        "at": _now(),
        "evidence_id": latest.get("evidence_id"),
        "verdict": verdict,
        "blockers": blockers,
        "terminal_transcript": terminal,
        "checks": checks,
        "boot_verdict": boot.get("verdict"),
        "site_proof_url": site_proof,
        "forensic_archive_url": latest.get("proof_url"),
        "hosted_at": latest.get("hosted_at") or latest.get("at"),
        "disclaimer": "Live inject from factory disk · same schema as weekly export bundle",
    }


def update_public_urls(site_proof: str) -> None:
    row = _read_json(PUBLIC_URLS)
    if not row:
        row = {"schema": "sourcea-public-urls-v1", "at": _now()}
    row["aeg_live_url"] = site_proof
    row["proof_url"] = site_proof
    row["at"] = _now()
    boot = _read_json(DATA / "boot-proof.json")
    if boot.get("verdict"):
        row["boot_verdict"] = boot.get("verdict")
    PUBLIC_URLS.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Inject AEG live proof JSON for landing")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    row = build_aeg_live()
    out_path = DATA / "aeg-live.json"
    if not args.dry_run:
        DATA.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        update_public_urls(str(row.get("site_proof_url") or ""))
        RECEIPT.write_text(
            json.dumps(
                {
                    "schema": "sourcea-aeg-live-inject-v1",
                    "at": _now(),
                    "path": str(out_path),
                    "evidence_id": row.get("evidence_id"),
                    "site_proof_url": row.get("site_proof_url"),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: aeg-live · {row.get('evidence_id')} · {row.get('site_proof_url')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
