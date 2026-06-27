#!/usr/bin/env python3
"""Chat Unify Terminal Motor — independent wrapper (peer to Forge Terminal motor).

Public name for Chat Unify's living IDE/terminal stack inside Chat Unify.app only.
  • This motor → /api/chat-unify-ide/v1
  • Forge Terminal motor → separate app (Forge Terminal.app) — not used here.

Implementation delegates to shared stack; responses are tagged product=chat-unify.
"""
from __future__ import annotations

from chat_unify_ide_v1 import (  # noqa: F401
    MOTOR_ID,
    MOTOR_LABEL,
    PRODUCT,
    get_run,
    handle_post,
    status_light,
    status_payload,
)

MOTOR_PUBLIC_NAME = "chat-unify-terminal-motor-v1"
TERMINAL_MOTOR_LABEL = "Chat Unify Terminal Motor"
