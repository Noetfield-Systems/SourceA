#!/usr/bin/env python3
"""Bounded resume CLI — delegates to factory_control_v1."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from factory_control_v1 import write_resume_token  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--max-turns", type=int, default=1)
    p.add_argument("--max-packs", type=int, default=1)
    p.add_argument("--trigger", default="ASF: resume drain")
    p.add_argument("--ttl-minutes", type=int, default=30)
    args = p.parse_args()
    print(json.dumps(write_resume_token(
        max_turns=args.max_turns,
        max_packs=args.max_packs,
        trigger=args.trigger,
        ttl_minutes=args.ttl_minutes,
    ), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
