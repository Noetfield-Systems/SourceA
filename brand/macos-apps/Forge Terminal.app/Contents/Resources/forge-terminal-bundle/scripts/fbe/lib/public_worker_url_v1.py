"""Shared FBE public worker URL + health probe — Wave 1 unified law.

One probe everywhere: HTTPS public URL · GET /health · ok=true · service starts with fbe.
Never treat mono_mirror_fallback or http://127.x as FBE_CLOUD_WORKER_URL.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SINA = Path.home() / ".sina"
FBE_CFG = ROOT / "data" / "fbe_cloud_worker_config_v1.json"
SECRETS = SINA / "secrets.env"
LOCAL_PREFIXES = ("http://127.", "http://localhost", "http://0.0.0.0")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _secret(key: str) -> str:
    if not SECRETS.is_file():
        return ""
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    return ""


def is_local_url(url: str) -> bool:
    u = str(url or "").lower()
    return any(u.startswith(p) for p in LOCAL_PREFIXES)


def fbe_health_ok(url: str, *, timeout: float = 8.0) -> bool:
    if not url:
        return False
    try:
        req = urllib.request.Request(f"{url.rstrip('/')}/health", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            row = json.loads(resp.read().decode("utf-8"))
        return bool(row.get("ok")) and str(row.get("service", "")).startswith("fbe")
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return False


def fbe_health_probe(url: str, *, timeout: float = 8.0) -> dict:
    if not url:
        return {"ok": False, "error": "empty_url"}
    try:
        req = urllib.request.Request(f"{url.rstrip('/')}/health", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            row = json.loads(resp.read().decode("utf-8"))
        ok = bool(row.get("ok")) and str(row.get("service", "")).startswith("fbe")
        return {"ok": ok, "health": row}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def resolve_public_fbe_url(*, require_health: bool = True) -> tuple[str, str]:
    """Return (url, source). No mirror fallback — farm mirror is NOT fbe-cloud-worker."""
    cfg = _read(FBE_CFG)
    url = _secret("FBE_CLOUD_WORKER_URL") or str(cfg.get("worker_url") or "")
    if url.startswith("https://"):
        if not require_health or fbe_health_ok(url):
            return url.rstrip("/"), "secrets" if _secret("FBE_CLOUD_WORKER_URL") else "config"
        return "", "https_unhealthy"
    dep = _read(SINA / "fbe-cloud-deploy-receipt-v1.json")
    dep_url = str(dep.get("worker_url") or "")
    if dep_url.startswith("https://"):
        if not require_health or fbe_health_ok(dep_url):
            return dep_url.rstrip("/"), "deploy_receipt"
        return "", "deploy_receipt_unhealthy"
    if is_local_url(url):
        return "", "local_only_not_cloud"
    return "", "missing_or_not_public_https"
