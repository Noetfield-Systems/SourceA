#!/usr/bin/env python3
"""Spawn gate — re-exports factory_control_v1 (single SSOT)."""
from factory_control_v1 import (  # noqa: F401
    clear_poison_stall,
    drain_spawn_allowed,
    exit_if_spawn_blocked,
    kill_flag_active,
    turn_allowed,
    write_poison_stall,
)
