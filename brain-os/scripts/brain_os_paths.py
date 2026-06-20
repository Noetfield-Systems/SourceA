#!/usr/bin/env python3
"""Canonical paths for unified brain-os layout under SourceA."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # SourceA root
BRAIN_OS = ROOT / "brain-os"
BO_SCRIPTS = BRAIN_OS / "scripts"

ENTRY = BRAIN_OS / "entry"
LAW = BRAIN_OS / "law"
MEMORY = BRAIN_OS / "memory"
CONTRACT = BRAIN_OS / "contract"
ENFORCEMENT = BRAIN_OS / "enforcement"
INCIDENTS = BRAIN_OS / "incidents"
SYSTEM = BRAIN_OS / "system"
PLAN_REGISTRY = BRAIN_OS / "plan-registry"
RUNTIME_DOC = BRAIN_OS / "runtime"
WTM = BRAIN_OS / "wtm"
LANES = BRAIN_OS / "lanes"
CURSOR_RULES = BRAIN_OS / "cursor" / "rules"

REGISTRY_JSON = PLAN_REGISTRY / "sourcea-1000" / "REGISTRY.json"
SOURCEA_PRIORITY = PLAN_REGISTRY / "SOURCEA-PRIORITY.md"

# Legacy stubs still resolve via these relative paths from ROOT
LEGACY_PLAN_LIBRARY = ROOT / "os" / "plan-library"
LEGACY_CHAT_HANDOFFS = ROOT / "os" / "chat-handoffs"


def resolve_plan_registry() -> Path:
    if PLAN_REGISTRY.is_dir():
        return PLAN_REGISTRY
    return ROOT / "os" / "plan-library"
