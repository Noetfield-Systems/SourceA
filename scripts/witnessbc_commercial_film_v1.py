#!/usr/bin/env python3
"""WitnessBC commercial film — 1080p real UI capture from witnessbc-site (:8090).

Uses commercial_short_film_v1.generate_film with Witness AI beats SSOT.
Law: >=70% real Proof Lab UI · no fake motion-graphics-only hero films.

Output:
  witnessbc-site/assets/witnessbc-commercial.mp4
  witnessbc-site/assets/w1-demo.mp4 (proof embed)
  ~/Desktop/WitnessBC-Commercial.mp4
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEATS = ROOT / "data" / "witnessbc-commercial-film-beats-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from commercial_short_film_v1 import generate_film  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="WitnessBC commercial film (1080p real UI)")
    ap.add_argument("--beats", type=Path, default=BEATS)
    ap.add_argument("--skip-publish", action="store_true")
    ap.add_argument("--refresh-voice", action="store_true", help="Bypass ElevenLabs cache; re-fetch narration")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    from film_elevenlabs_wire_v1 import set_refresh_voice  # noqa: E402

    set_refresh_voice(args.refresh_voice)
    if not args.beats.is_file():
        print(f"FAIL: missing beats {args.beats}", file=sys.stderr)
        return 1
    try:
        receipt = generate_film(
            beats_path=args.beats,
            skip_publish=args.skip_publish,
            vo_lane="witnessbc",
            product="witnessbc",
        )
    except (RuntimeError, SystemExit) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"OK: WitnessBC commercial film · voice={receipt.get('voice_engine')}")
        print(f"OUTPUT={receipt.get('output')}")
        for p in receipt.get("published") or []:
            print(f"PUBLISHED={p}")
        print(f"RECEIPT={receipt.get('receipt_path')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
