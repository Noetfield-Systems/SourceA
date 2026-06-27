#!/usr/bin/env python3
"""Forge Production MVP — governance CLI wrapping existing kernel.

Reads JSON from stdin, writes decision JSON to stdout.
Law: docs/FORGE_PRODUCTION_MVP_WIRING_LOCKED_v1.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from forge_governance_kernel_v1 import govern  # noqa: E402


def main() -> int:
    try:
        req: dict[str, Any] = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "DENY", "reason": f"invalid_json:{exc}"}))
        return 1

    decision = govern(
        agent_id=str(req.get("agent_id") or "forge-worker-1"),
        agent_role=str(req.get("agent_role") or "builder"),
        action_type=str(req.get("action_type") or "read_file"),
        payload=dict(req.get("payload") or {}),
        task_id=str(req.get("task_id") or ""),
        dry_run=bool(req.get("dry_run", True)),
        legal_review=bool(req.get("legal_review", False)),
        charge_on_allow=not bool(req.get("dry_run", True)),
    )
    print(json.dumps(decision, ensure_ascii=False))
    return 0 if decision.get("status") == "ALLOW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
