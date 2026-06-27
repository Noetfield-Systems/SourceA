#!/usr/bin/env python3
"""Chat Unify Living IDE Motor — independent product wrapper (peer to Forge Terminal).

Same implementation stack underneath; **not** the Forge Terminal motor:
  • Chat Unify IDE  → POST /api/chat-unify-ide/v1  (Chat Unify.app :13023)
  • Forge Terminal  → POST /api/forge-terminal/v1  (Forge Terminal.app :13029)

Smart router / multi-agent stays on /api/chat-unify-engine/v1 (separate motor).
"""
from __future__ import annotations

from typing import Any

MOTOR_ID = "chat-unify-terminal-motor-v1"
MOTOR_LABEL = "Chat Unify Terminal Motor"
PRODUCT = "chat-unify"
PEER_MOTOR = "forge-terminal-v1"
PEER_PORT = 13029


def _tag(row: dict[str, Any]) -> dict[str, Any]:
    if isinstance(row, dict):
        row.setdefault("motor", MOTOR_ID)
        row.setdefault("motor_label", MOTOR_LABEL)
        row.setdefault("product", PRODUCT)
        row.setdefault("peer_motor", PEER_MOTOR)
        row.setdefault("peer_port", PEER_PORT)
        row.pop("forge_terminal_motor", None)
    return row


def handle_post(body: dict[str, Any]) -> dict[str, Any]:
    from forge_terminal_v1 import handle_post as _post  # noqa: WPS433

    return _tag(_post(body))


def status_payload(workspace_path: str | None = None) -> dict[str, Any]:
    from forge_terminal_v1 import status_payload as _status  # noqa: WPS433

    return _tag(_status(workspace_path=workspace_path))


def status_light(workspace_path: str | None = None) -> dict[str, Any]:
    from forge_terminal_v1 import status_light as _light  # noqa: WPS433

    return _tag(_light(workspace_path=workspace_path))


def get_run(run_id: str = "") -> dict[str, Any]:
    from forge_terminal_v1 import get_run as _get  # noqa: WPS433

    return _tag(_get(run_id=run_id))
