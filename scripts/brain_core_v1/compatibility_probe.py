#!/usr/bin/env python3
"""Read-only compatibility probe for Brain Core v1 gate receipts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.brain_core_v1.decision_core import load_locked_definitions
from scripts.brain_core_v1.gate import run_gate
from scripts.brain_core_v1.live_status_probe import probe_live_status_map


MOCK_CASES = [
    {
        "id": "sourcea_live_good",
        "message": "Is SourceA live?",
        "draft": "",
        "live_status": {"sourcea_app_http_status": {"status": "good", "http_status": 200}},
    },
    {
        "id": "sourcea_unknown_fake_pass",
        "message": "Is SourceA live?",
        "draft": "SourceA is live because PASS.",
        "live_status": {"sourcea_app_http_status": {"status": "unknown", "error": "mock timeout"}},
    },
    {
        "id": "forge_degraded_block",
        "message": "Forge Terminal is not connecting.",
        "draft": "Forge Terminal is BLOCK right now.",
        "live_status": {"forge_terminal_runtime_status": {"status": "degraded", "http_status": 503}},
    },
    {
        "id": "proof_unknown",
        "message": "Does every possible SourceA run have perfect public proof?",
        "draft": "",
        "live_status": {"specific_run_public_proof_status": {"status": "unknown"}},
    },
]


def run_mock_cases(*, definitions: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    locked_definitions = definitions or load_locked_definitions()
    return [
        {
            "id": case["id"],
            "receipt": run_gate(
                case["message"],
                case["draft"],
                live_status=case["live_status"],
                definitions=locked_definitions,
            ),
        }
        for case in MOCK_CASES
    ]


def run_live_case(message: str, draft: str, *, timeout: float = 5.0) -> dict[str, Any]:
    return {
        "id": "live_probe",
        "receipt": run_gate(
            message,
            draft,
            live_status=probe_live_status_map(timeout=timeout),
            definitions=load_locked_definitions(),
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Brain Core v1 compatibility probe")
    parser.add_argument("--live-probe", action="store_true")
    parser.add_argument("--message", default="Is SourceA live?")
    parser.add_argument("--draft", default="")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    if args.live_probe:
        result = [run_live_case(args.message, args.draft, timeout=args.timeout)]
    else:
        result = run_mock_cases()
    print(json.dumps({"schema": "brain-core-v1-compatibility-probe", "cases": result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
