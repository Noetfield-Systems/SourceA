#!/usr/bin/env python3
"""CLI probe for deterministic Brain Core v1 decisions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.brain_core_v1.decision_core import decide, load_locked_definitions
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
    parser.add_argument("--definitions", default=None)
    parser.add_argument("--draft", default="")
    args = parser.parse_args()

    definitions = load_locked_definitions(args.definitions) if args.definitions else None
    decision = decide(args.message, _load_status_map(args.status_json), definitions=definitions)
    result = {"decision": decision}
    if args.draft:
        result["sanitized"] = sanitize_model_output(decision, args.draft)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
