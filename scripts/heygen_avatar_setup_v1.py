#!/usr/bin/env python3
"""Wire HeyGen API key for avatar pipeline (LinkedIn / tier C social).

Usage:
  python3 scripts/heygen_avatar_setup_v1.py --check --json
  python3 scripts/heygen_avatar_setup_v1.py --api-key '...' --json
  python3 scripts/heygen_avatar_setup_v1.py --write-example --json

Writes ~/.sina/heygen-v1.env:
  HEYGEN_API_KEY

Receipt: ~/.sina/enforcement/heygen-avatar-setup-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "enforcement" / "heygen-avatar-setup-receipt-v1.json"
DASHBOARD = "https://app.heygen.com/settings?nav=API"

sys.path.insert(0, str(ROOT / "scripts"))
from heygen_avatar_wire_v1 import (  # noqa: E402
    HEYGEN_EXAMPLE,
    HEYGEN_SECRETS,
    heygen_config,
    upsert_heygen_secret,
    verify_key,
    write_env_example,
    _mask_key,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_status() -> dict:
    cfg = heygen_config()
    example_path = write_env_example()
    verify = verify_key(cfg["api_key"]) if cfg["api_key"] else {"ok": False, "error": "missing_key"}
    master_candidates = [
        SINA / "avatar-pipeline-v1" / "master-image.jpg",
        SINA / "avatar-pipeline-v1" / "master-image.png",
        Path.home() / "Desktop" / "founder-headshot.jpg",
    ]
    master = next((p for p in master_candidates if p.is_file() and p.stat().st_size > 1000), None)
    return {
        "ok": bool(cfg["api_key"]) and verify.get("ok"),
        "schema": "heygen-avatar-setup-v1",
        "at": _now(),
        "heygen_configured": bool(cfg["api_key"]),
        "key_valid": verify.get("ok", False),
        "key_mask": _mask_key(cfg["api_key"]) if cfg["api_key"] else None,
        "secrets_path": str(HEYGEN_SECRETS),
        "example_path": str(example_path),
        "example_exists": example_path.is_file(),
        "master_image": str(master) if master else None,
        "master_image_ready": master is not None,
        "dashboard": DASHBOARD,
        "verify": verify,
        "avatar_scripts": [
            "scripts/avatar_pipeline_v1.py",
            "avatar-pipeline.sh",
        ],
        "founder_line": (
            "HeyGen live — run: cd ~/Desktop/SourceA && bash avatar-pipeline.sh linkedin"
            if verify.get("ok") and master
            else (
                "HeyGen key OK — drop master-image.jpg at ~/.sina/avatar-pipeline-v1/ then bash avatar-pipeline.sh linkedin"
                if verify.get("ok")
                else (
                    f"Copy {HEYGEN_EXAMPLE} → {HEYGEN_SECRETS} and set HEYGEN_API_KEY"
                    if not cfg["api_key"]
                    else f"HeyGen key invalid — refresh at {DASHBOARD}"
                )
            )
        ),
    }


def save_key(*, api_key: str) -> dict:
    api_key = (api_key or "").strip()
    if not api_key or len(api_key) < 12:
        return {
            "ok": False,
            "error": "invalid_key_shape",
            "founder_line": f"Paste HEYGEN_API_KEY from {DASHBOARD}",
        }
    verify = verify_key(api_key)
    if not verify.get("ok"):
        return {
            "ok": False,
            "error": verify.get("error", "invalid_key"),
            "verify": verify,
            "founder_line": verify.get("detail") or "HeyGen key verify failed",
        }
    upsert_heygen_secret("HEYGEN_API_KEY", api_key)
    write_env_example()
    row = {
        "ok": True,
        "schema": "heygen-avatar-setup-v1",
        "at": _now(),
        "key_mask": _mask_key(api_key),
        "verify": verify,
        "secrets_path": str(HEYGEN_SECRETS),
        "founder_line": "HeyGen wired — drop master-image.jpg then bash avatar-pipeline.sh linkedin",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Wire HeyGen API for avatar pipeline")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write-example", action="store_true", help="Write heygen-v1.env.example only")
    ap.add_argument("--api-key")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.write_example:
        path = write_env_example()
        row = {"ok": True, "example_path": str(path), "founder_line": f"Edit {HEYGEN_SECRETS} from example"}
        print(json.dumps(row, indent=2) if args.json else row["founder_line"])
        return 0

    if args.check:
        row = check_status()
        print(json.dumps(row, indent=2) if args.json else row["founder_line"])
        return 0 if row.get("ok") else 1

    key = (args.api_key or "").strip() or sys.stdin.read().strip()
    row = save_key(api_key=key)
    print(json.dumps(row, indent=2) if args.json else row.get("founder_line", "FAIL"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
