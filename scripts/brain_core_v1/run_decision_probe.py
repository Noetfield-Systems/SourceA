#!/usr/bin/env python3
"""CLI probe for deterministic Brain Core v1 decisions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.brain_core_v1.decision_core import decide, load_locked_definitions
from scripts.brain_core_v1.live_status_probe import decision_status_map, probe_live_status_map
from scripts.brain_core_v1.sanitizer import sanitize_model_output


def _load_status_map(raw: str) -> dict[str, object]:
    if not raw:
        return {}
    maybe_path = Path(raw)
    if maybe_path.is_file():
        return json.loads(maybe_path.read_text(encoding="utf-8"))
    return json.loads(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Brain Core v1 deterministic decision probe")
    parser.add_argument("--message", required=True)
    parser.add_argument("--status-json", default="{}")
    parser.add_argument("--live-probe", action="store_true")
    parser.add_argument("--probe-timeout", type=float, default=5.0)
    parser.add_argument("--definitions", default=None)
    parser.add_argument("--draft", default="")
    args = parser.parse_args()

    definitions = load_locked_definitions(args.definitions) if args.definitions else None
    if args.live_probe:
        live_status_map = probe_live_status_map(timeout=args.probe_timeout)
        status_map = decision_status_map(live_status_map)
    else:
        live_status_map = None
        status_map = decision_status_map(_load_status_map(args.status_json))
    decision = decide(args.message, status_map, definitions=definitions)
    result = {"decision": decision, "status_map": status_map}
    if live_status_map is not None:
        result["live_status_map"] = live_status_map
    if args.draft:
        result["sanitized"] = sanitize_model_output(decision, args.draft)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
