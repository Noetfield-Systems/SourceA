#!/usr/bin/env python3
"""Regression checks for SourceA's client-only Supabase auth config fallback."""
from __future__ import annotations
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sourcea_auth_sync", ROOT / "scripts" / "sync_sourcea_platform_auth_public_v1.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

with tempfile.TemporaryDirectory(prefix="sourcea-public-auth-ci-") as workdir:
    folder = Path(workdir)
    module.OUT = folder / "sourcea-platform-auth-config-v1.json"
    module.SECRETS = folder / "secrets-not-provided.env"
    original = json.loads((ROOT / "SourceA-landing" / "green-unified" / "data" / "sourcea-platform-auth-config-v1.json").read_text())
    assert original["configured"] is True, "Repo's public anon client configuration is not enabled"
    assert original["supabase_url"].startswith("https://")
    assert original["venture"] == "sourcea"
    assert "service_role" not in original
    module.OUT.write_text(json.dumps(original), encoding="utf-8")
    result = module.sync()
    actual = json.loads(module.OUT.read_text())
    assert result["configured"] is True and result["source"] == "committed_public_anon_config"
    assert actual["supabase_url"] == original["supabase_url"]
    assert actual["supabase_anon_key"] == original["supabase_anon_key"]
    assert "service_role" not in actual

    module.OUT.unlink()
    result = module.sync()
    assert result["configured"] is False, "Must fail closed when both local and committed config are missing"

    rejected = dict(original, service_role="must-never-expose")
    module.OUT.write_text(json.dumps(rejected))
    result = module.sync()
    assert result["configured"] is False, "Never accept a committed config containing server credentials"

print("SOURCEA_PUBLIC_AUTH_SYNC_PASS committed_public_only=True missing_fails_closed=True unsafe_key_rejected=True")
