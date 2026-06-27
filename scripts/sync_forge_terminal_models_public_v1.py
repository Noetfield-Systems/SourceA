#!/usr/bin/env python3
"""Export forge model catalog for client fallback (offline UI + online demo)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from model_dispatch import forge_models_payload  # noqa: WPS433

    payload = forge_models_payload()
    out = {
        "schema": "forge-terminal-models-public-v1",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "models": payload.get("models") or [],
        "model_groups": payload.get("groups") or [],
        "model_roles": payload.get("roles") or [],
        "default_model": payload.get("default_model"),
        "default_role": payload.get("default_role"),
        "keys_ready": payload.get("keys_ready") or {},
    }
    targets = [
        ROOT / "apps" / "forge-terminal-v1" / "data" / "forge-terminal-models-public-v1.json",
        ROOT / "SourceA-landing" / "green-unified" / "data" / "forge-terminal-models-public-v1.json",
    ]
    for path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "model_count": len(out["models"]), "paths": [str(p) for p in targets]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
