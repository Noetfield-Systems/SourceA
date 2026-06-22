#!/usr/bin/env python3
"""Runtime agent config loader — factory variations from disk SSOT (LaunchDarkly-shaped)."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "agent-runtime-factory-registry-v1.json"
BAY_SSOT = ROOT / "data" / "cloud-comprehension-bay-v1.json"

DEFAULT_VARIATION = {
    "config_version": "1.0.0",
    "meaning_min": 65,
    "label": "legacy",
    "retry_on_blocked": False,
    "relax_language_gate": False,
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_registry() -> dict[str, Any]:
    return _read_json(REGISTRY_PATH)


def factory_registry_entry(factory_id: str) -> dict[str, Any]:
    reg = load_registry()
    factories = reg.get("factories") or {}
    row = factories.get(factory_id)
    if not row:
        raise KeyError(f"factory not in registry: {factory_id}")
    return row


def factory_id_for_bay_slug(bay_slug: str) -> str | None:
    reg = load_registry()
    for fid, row in (reg.get("factories") or {}).items():
        if str(row.get("bay_slug") or "") == bay_slug:
            return str(fid)
    if bay_slug == "comprehension-loop-bay":
        return "comprehension-loop-factory-v1"
    return None


def _resolve_ssot_path(*, factory_id: str | None = None, bay_slug: str | None = None) -> Path:
    entry: dict[str, Any] = {}
    if factory_id:
        try:
            entry = factory_registry_entry(factory_id)
        except KeyError:
            entry = {}
    elif bay_slug:
        fid = factory_id_for_bay_slug(bay_slug)
        if fid:
            entry = factory_registry_entry(fid)

    env_key = str(entry.get("env_ssot") or "").strip()
    if env_key:
        override = os.environ.get(env_key, "").strip()
        if override:
            path = Path(override)
            return path if path.is_absolute() else ROOT / path

    if bay_slug == "comprehension-loop-bay" and not entry:
        legacy = os.environ.get("AGENT_RUNTIME_BAY_SSOT", "").strip()
        if legacy:
            path = Path(legacy)
            return path if path.is_absolute() else ROOT / path
        return BAY_SSOT

    ssot = str(entry.get("ssot") or "")
    if ssot:
        path = Path(ssot)
        return path if path.is_absolute() else ROOT / path

    generic = os.environ.get("AGENT_RUNTIME_FACTORY_SSOT", "").strip()
    if generic:
        path = Path(generic)
        return path if path.is_absolute() else ROOT / path
    return BAY_SSOT


def _pick_variation_key(doc: dict[str, Any], *, context_id: str = "") -> str:
    active = str(doc.get("active_variation_key") or doc.get("rollout", {}).get("active") or "default")
    variations = doc.get("variations") or {}
    if active in variations:
        return active
    if "default" in variations:
        return "default"
    if variations:
        return next(iter(variations))
    return "default"


def _bucket(context_id: str, percent: int) -> bool:
    if percent >= 100:
        return True
    if percent <= 0:
        return False
    seed = hashlib.sha256(context_id.encode("utf-8")).hexdigest()
    slot = int(seed[:8], 16) % 100
    return slot < percent


def _default_variation_for_doc(doc: dict[str, Any]) -> dict[str, Any]:
    schema = str(doc.get("schema") or "")
    if schema.startswith("cloud-comprehension-bay"):
        return dict(DEFAULT_VARIATION)
    if schema.startswith("video-ad-factory-runtime"):
        return {
            "config_version": "1.0.0",
            "mock_llm": True,
            "require_approval": True,
            "vo_lane": "sourcea",
            "elevenlabs_model": "eleven_multilingual_v2",
            "label": "standard",
        }
    if schema.startswith("noetfield-copilot-runtime"):
        return {
            "config_version": "1.0.0",
            "policy_strictness": "strict",
            "require_tle_receipt": True,
            "allowed_actions": ["read", "summarize"],
            "block_pii_export": True,
            "label": "standard",
        }
    return {"config_version": "1.0.0", "label": "standard"}


def load_factory_runtime_config(
    factory_id: str,
    *,
    context_id: str = "",
    variation_key: str | None = None,
    config_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry = factory_registry_entry(factory_id)
    doc = _read_json(_resolve_ssot_path(factory_id=factory_id))
    bay_slug = str(doc.get("bay_slug") or entry.get("bay_slug") or "")
    base_default = _default_variation_for_doc(doc)

    if config_override:
        merged = {**base_default, **config_override}
        merged["factory_id"] = factory_id
        merged["bay_slug"] = bay_slug
        merged["variation_key"] = str(config_override.get("variation_key") or "override")
        return merged

    variations = doc.get("variations") or {}
    rollout = doc.get("rollout") or {}
    percent = int(rollout.get("percent") or 100)

    if variation_key and variation_key in variations:
        key = variation_key
    elif context_id and percent < 100:
        alt = str(rollout.get("active") or doc.get("active_variation_key") or "default")
        key = alt if _bucket(context_id, percent) else _pick_variation_key(doc)
    else:
        key = _pick_variation_key(doc, context_id=context_id)

    row = {**base_default, **(variations.get(key) or {})}
    row["factory_id"] = factory_id
    row["bay_slug"] = bay_slug
    row["variation_key"] = key
    row["config_version"] = row.get("config_version") or base_default.get("config_version")
    row["rollout_percent"] = percent
    row["active_variation_key"] = str(doc.get("active_variation_key") or "default")
    return row


def load_bay_config(
    bay_slug: str,
    *,
    context_id: str = "",
    variation_key: str | None = None,
    config_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fid = factory_id_for_bay_slug(bay_slug)
    if fid:
        return load_factory_runtime_config(
            fid,
            context_id=context_id,
            variation_key=variation_key,
            config_override=config_override,
        )

    doc = _read_json(_resolve_ssot_path(bay_slug=bay_slug))
    if str(doc.get("bay_slug") or "") != bay_slug and bay_slug == "comprehension-loop-bay":
        doc = doc or {"bay_slug": bay_slug}

    base_default = _default_variation_for_doc(doc)
    if config_override:
        merged = {**base_default, **config_override}
        merged["bay_slug"] = bay_slug
        merged["variation_key"] = str(config_override.get("variation_key") or "override")
        return merged

    variations = doc.get("variations") or {}
    rollout = doc.get("rollout") or {}
    percent = int(rollout.get("percent") or 100)

    if variation_key and variation_key in variations:
        key = variation_key
    elif context_id and percent < 100:
        alt = str(rollout.get("active") or doc.get("active_variation_key") or "default")
        key = alt if _bucket(context_id, percent) else _pick_variation_key(doc)
    else:
        key = _pick_variation_key(doc, context_id=context_id)

    row = {**base_default, **(variations.get(key) or {})}
    row["bay_slug"] = bay_slug
    row["variation_key"] = key
    row["rollout_percent"] = percent
    return row


def load_variation_by_key(bay_slug: str, variation_key: str) -> dict[str, Any]:
    return load_bay_config(bay_slug, variation_key=variation_key)
