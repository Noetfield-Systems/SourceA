#!/usr/bin/env python3
"""Inline policy checks for validate-mac-control-dispatch-v1.sh (no heredoc — Mac-safe)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.mac_control_dispatch_v1 import (  # noqa: E402
    mac_observe_only_block,
    path_is_mac_motor_blocked,
)

ALLOW = (
    "/api/cloud-worker/dispatch/v1",
    "/api/loop-specialist/tick/v1",
    "/api/forge/v02/run/v1",
    "/api/cloud-forge-run/observer/v1",
    "/api/cloud-forge-run/queue/v1",
)
BLOCK = (
    "/api/cloud-forge-run/auto-tick/v1",
    "/api/cloud-forge-run/proceed/v1",
    "/api/forge/v02/drain/v1",
)


def main() -> int:
    for path in ALLOW:
        assert not path_is_mac_motor_blocked(path), path
        assert mac_observe_only_block(path=path) is None, path

    for path in BLOCK:
        assert path_is_mac_motor_blocked(path), path
        blocked = mac_observe_only_block(path=path)
        assert blocked and blocked.get("error") == "mac_observe_only", path

    mutate = mac_observe_only_block(
        path="/api/cloud-forge-run/queue/v1",
        body={"action": "skip_head"},
    )
    assert mutate and mutate.get("motor_blocked") is True
    read_only = mac_observe_only_block(
        path="/api/cloud-forge-run/queue/v1",
        body={"action": "get_head"},
    )
    assert read_only is None
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
