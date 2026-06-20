#!/usr/bin/env python3
"""SourceA commercial film ONLY — :5180 landing · Hub :13020 · Mac Health :13024.

NOT WitnessBC. Separate SSOT: data/commercial-short-film-beats-v1.json

Output:
  SourceA-landing/green-unified/assets/commercial-short-demo.mp4
  ~/Desktop/SourceA-Commercial-Short.mp4
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEATS = ROOT / "data" / "commercial-short-film-beats-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from commercial_short_film_v1 import generate_film  # noqa: E402
from film_elevenlabs_wire_v1 import set_refresh_voice, set_vo_lane  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA commercial film (1080p real UI — NOT WitnessBC)")
    ap.add_argument("--beats", type=Path, default=BEATS)
    ap.add_argument("--skip-publish", action="store_true")
    ap.add_argument("--refresh-voice", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    set_vo_lane("sourcea")
    set_refresh_voice(args.refresh_voice)
    if not args.beats.is_file():
        print(f"FAIL: missing SourceA beats {args.beats}", file=sys.stderr)
        return 1
    try:
        receipt = generate_film(
            beats_path=args.beats,
            skip_publish=args.skip_publish,
            vo_lane="sourcea",
            product="sourcea",
        )
    except (RuntimeError, SystemExit) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"OK: SourceA commercial film · voice={receipt.get('voice_engine')}")
        print(f"OUTPUT={receipt.get('output')}")
        for p in receipt.get("published") or []:
            print(f"PUBLISHED={p}")
        print(f"RECEIPT={receipt.get('receipt_path')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
