"""HTTP helpers for Noetfield SDK."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def load_config() -> dict[str, Any]:
    hub = os.environ.get("NOETFIELD_HUB_URL", "").strip()
    secret = os.environ.get("FBE_INTERNAL_SECRET", "").strip()
    cfg_path = Path.cwd() / ".noetfield.json"
    if cfg_path.is_file():
        try:
            disk = json.loads(cfg_path.read_text(encoding="utf-8"))
            hub = hub or str(disk.get("hub_url") or "").strip()
            secret = secret or str(disk.get("api_key") or disk.get("secret") or "").strip()
        except (OSError, json.JSONDecodeError):
            pass
    if not hub:
        hub = "http://127.0.0.1:13020"
    return {"hub_url": hub.rstrip("/"), "api_key": secret}


def http_json(
    *,
    method: str,
    url: str,
    body: dict[str, Any] | None = None,
    api_key: str = "",
    timeout: int = 120,
) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8"))
        except Exception:
            detail = {"message": str(exc)}
        return {"ok": False, "status": exc.code, "error": "http_error", "detail": detail}
    except Exception as exc:
        return {"ok": False, "error": "request_failed", "message": str(exc)}
