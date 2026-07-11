"""Bridge to SourceA Language Layer + model routing (optional import)."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


def resolve_sourcea_scripts() -> Path | None:
    env = os.environ.get("SOURCEA_REPO_ROOT") or os.environ.get("SOURCEA_SPINE_DEV_ROOT")
    if env:
        scripts = Path(env)
        if scripts.name == "content-quality-spine":
            scripts = scripts.parent.parent / "scripts"
        elif scripts.name != "scripts":
            scripts = scripts / "scripts"
        if (scripts / "ai_unify_api_v1.py").is_file():
            return scripts
    here = Path(__file__).resolve()
    candidate = here.parents[3] / "scripts"
    if (candidate / "ai_unify_api_v1.py").is_file():
        return candidate
    return None


def dispatch_excellence_llm(*, system: str, user: str, model_budget: str = "low") -> dict[str, Any]:
    scripts = resolve_sourcea_scripts()
    if not scripts:
        return {"ok": False, "error": "sourcea_scripts_unavailable"}
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        from ai_unify_api_v1 import dispatch_raw, pick_provider  # noqa: WPS433
    except ImportError as exc:
        return {"ok": False, "error": f"import_failed:{exc}"}

    if pick_provider("auto") == "none":
        return {"ok": False, "error": "no_api_key"}

    model = "gemini-2.5-flash" if model_budget in ("low", "none", "") else None
    return dispatch_raw(
        system=system,
        user=user,
        provider="auto",
        model=model,
        source="content-quality-spine-excellence",
        light_gate=True,
    )
