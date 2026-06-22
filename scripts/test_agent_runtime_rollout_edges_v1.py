#!/usr/bin/env python3
"""Rollout bucket edge cases — percent 0, 1, 100."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from agent_runtime_config_v1 import _bucket  # noqa: WPS433


def main() -> int:
    sample = "rollout-edge-sample-context"
    assert _bucket(sample, 0) is False, "percent 0 must never bucket"
    assert _bucket(sample, 100) is True, "percent 100 must always bucket"

    hits = sum(1 for i in range(1000) if _bucket(f"edge-{i:04d}", 1))
    assert hits > 0, "percent 1 should bucket some contexts"
    assert hits < 1000, "percent 1 should not bucket all contexts"

    print(f"OK: rollout edges percent 0/1/100 (percent-1 hits={hits}/1000)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
