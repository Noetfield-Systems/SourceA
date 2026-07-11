"""Package version and rules fingerprint."""
from __future__ import annotations

import hashlib
import json
from importlib import resources

SPINE_VERSION = "1.1.1"
PACKAGE_NAME = "content-quality-spine"
LLM_MODE_DEFAULT = "off"
SUPPORTED_LLM_MODES = ("off", "shadow", "advisory")


def bundled_rules_path(name: str = "conversation-script-logic-registry-v1.json") -> str:
    return str(resources.files("content_quality_spine.rules").joinpath(name))


def rules_hash(name: str = "conversation-script-logic-registry-v1.json") -> str:
    data = resources.files("content_quality_spine.rules").joinpath(name).read_text(encoding="utf-8")
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]
